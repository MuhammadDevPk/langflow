#!/usr/bin/env python3
"""
Export Langflow flows to JSON files for version control.

This script fetches all flows from your Langflow instance and saves them
as JSON files in the flows/ directory, making them Git-trackable.

Usage:
    python export_flows.py --api-key YOUR_API_KEY

Or set environment variable:
    export LANGFLOW_API_KEY=your_key_here
    python export_flows.py
"""

import os
import json
import argparse
import requests
from pathlib import Path
from typing import Dict, List, Any


def get_all_flows(base_url: str, api_key: str) -> List[Dict[str, Any]]:
    """Fetch all flows from Langflow API."""
    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }

    try:
        response = requests.get(
            f"{base_url}/api/v1/flows/",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching flows: {e}")
        return []


def get_flow_details(base_url: str, api_key: str, flow_id: str) -> Dict[str, Any]:
    """Fetch detailed flow data including all nodes and edges."""
    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }

    try:
        response = requests.get(
            f"{base_url}/api/v1/flows/{flow_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching flow {flow_id}: {e}")
        return {}


def sanitize_filename(name: str) -> str:
    """Convert flow name to safe filename."""
    # Replace invalid filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    # Limit length and strip whitespace
    return name.strip()[:100]


def remove_component_metadata(flow_data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove component version metadata to prevent update notifications.

    This removes version-specific metadata from components so they automatically
    use the latest version when imported on different machines.
    """
    if not isinstance(flow_data, dict):
        return flow_data

    # Navigate to nodes in the flow
    if "data" in flow_data and isinstance(flow_data["data"], dict):
        if "nodes" in flow_data["data"] and isinstance(flow_data["data"]["nodes"], list):
            for node in flow_data["data"]["nodes"]:
                if isinstance(node, dict) and "data" in node:
                    node_data = node["data"]
                    if isinstance(node_data, dict) and "node" in node_data:
                        component = node_data["node"]
                        # Remove version metadata that causes update notifications
                        if isinstance(component, dict):
                            # Remove version-related fields
                            for field in ["frozen", "is_input", "is_output", "official"]:
                                component.pop(field, None)

    return flow_data


def scrub_secrets_from_flow(flow_data: Dict[str, Any], parent_key: str = None) -> Dict[str, Any]:
    """Remove API keys and secrets from flow data before saving.

    Args:
        flow_data: The flow data to scrub
        parent_key: The parent key name (used to avoid scrubbing component code)
    """
    if isinstance(flow_data, dict):
        for key, value in flow_data.items():
            # Skip scrubbing if this is component code
            # Component code is stored in template.code.value and should never be scrubbed
            if parent_key == "code" and key == "value":
                continue

            # Clear value fields for API keys and folder IDs
            # Template structure is: template.openai_api_key.value = "sk-xxx"
            if key == "value" and parent_key in ["api_key", "openai_api_key", "langflow_api_key", "folder_id"]:
                if isinstance(value, str) and len(value) > 0:
                    flow_data[key] = ""  # Empty string!
            elif isinstance(value, (dict, list)):
                flow_data[key] = scrub_secrets_from_flow(value, parent_key=key)
    elif isinstance(flow_data, list):
        return [scrub_secrets_from_flow(item, parent_key=parent_key) for item in flow_data]

    return flow_data


def export_all_flows(
    base_url: str = "http://localhost:7860",
    api_key: str = None,
    output_dir: str = None,
    scrub: bool = True
):
    """Export all flows from Langflow to individual JSON files."""
    
    # Determine output directory relative to this script if not specified
    if output_dir is None:
        script_dir = Path(__file__).parent
        output_path = script_dir / "flows"
    else:
        output_path = Path(output_dir)

    if not api_key:
        api_key = os.getenv("LANGFLOW_API_KEY")

    if not api_key:
        print("Error: API key required. Set LANGFLOW_API_KEY environment variable or use --api-key flag")
        return False

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    print(f"Fetching flows from {base_url}...")
    flows = get_all_flows(base_url, api_key)

    if not flows:
        print("No flows found or error occurred")
        return False

    print(f"Found {len(flows)} flow(s)")

    # Export each flow
    exported = 0
    for flow in flows:
        flow_id = flow.get("id")
        flow_name = flow.get("name", "unnamed_flow")

        print(f"\nExporting: {flow_name} (ID: {flow_id})")

        # Get full flow details
        flow_data = get_flow_details(base_url, api_key, flow_id)

        if flow_data:
            # Scrub secrets from flow data
            flow_data = scrub_secrets_from_flow(flow_data)

            # Remove component metadata to prevent update notifications
            flow_data = remove_component_metadata(flow_data)

            # Remove folder_id to make flows portable across different Langflow instances
            if "folder_id" in flow_data:
                del flow_data["folder_id"]
            if "folder" in flow_data:
                del flow_data["folder"]

            # Create filename
            safe_name = sanitize_filename(flow_name)
            filename = f"{safe_name}_{flow_id}.json"
            filepath = output_path / filename

            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(flow_data, f, indent=2, ensure_ascii=False)

            print(f"  ✓ Saved to: {filepath}")
            exported += 1
        else:
            print(f"  ✗ Failed to export")

    print(f"\n{'='*60}")
    print(f"Successfully exported {exported}/{len(flows)} flows to {output_dir}/")
    print(f"{'='*60}")

    # Create a manifest file
    manifest = {
        "exported_at": None,  # Could add timestamp
        "total_flows": len(flows),
        "flows": [
            {
                "id": flow.get("id"),
                "name": flow.get("name"),
                "filename": f"{sanitize_filename(flow.get('name', 'unnamed_flow'))}_{flow.get('id')}.json"
            }
            for flow in flows
        ]
    }

    manifest_path = output_path / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"\nManifest saved to: {manifest_path}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Export Langflow flows to JSON files"
    )
    parser.add_argument(
        "--api-key",
        help="Langflow API key (or set LANGFLOW_API_KEY env var)",
        default=None
    )
    parser.add_argument(
        "--base-url",
        help="Langflow base URL",
        default="http://localhost:7860"
    )
    parser.add_argument(
        "--output",
        help="Output directory for flow JSONs",
        default="flows"
    )

    args = parser.parse_args()

    success = export_flows(
        base_url=args.base_url,
        api_key=args.api_key,
        output_dir=args.output
    )

    if success:
        print("\n💡 Next steps:")
        print("  1. Review the exported flows in the flows/ directory")
        print("  2. Add them to Git:")
        print("     git add flows/")
        print('     git commit -m "Add Langflow flows"')
        print("     git push")
        print("\n  3. To re-export flows after making changes:")
        print("     python export_flows.py")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
