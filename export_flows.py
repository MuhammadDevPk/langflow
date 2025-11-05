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


def scrub_secrets_from_flow(flow_data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove API keys and secrets from flow data before saving."""
    if isinstance(flow_data, dict):
        for key, value in flow_data.items():
            # Check specific fields that might contain secrets
            if key in ["api_key", "openai_api_key", "value"] and isinstance(value, str):
                # Check if it looks like an OpenAI key
                if value.startswith("sk-") and len(value) > 20:
                    flow_data[key] = "sk-YOUR_OPENAI_API_KEY_HERE"
                # Check for other common API key patterns
                elif "api" in str(value).lower() and len(value) > 30:
                    flow_data[key] = "YOUR_API_KEY_HERE"
            elif isinstance(value, (dict, list)):
                flow_data[key] = scrub_secrets_from_flow(value)
    elif isinstance(flow_data, list):
        return [scrub_secrets_from_flow(item) for item in flow_data]

    return flow_data


def export_flows(base_url: str = "http://localhost:7860", api_key: str = None, output_dir: str = "flows"):
    """Export all flows to JSON files."""

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
