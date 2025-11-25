#!/usr/bin/env python3
"""
Smart Langflow flow importer that automatically handles folder management.

This script:
1. Checks if folders/projects exist in Langflow
2. If yes, imports to the first folder
3. If no, creates a "Voxhive Flows" folder and imports there

Usage:
    python import_flows.py --api-key YOUR_API_KEY

Or set environment variable:
    export LANGFLOW_API_KEY=your_key_here
    python import_flows.py
"""

import os
import json
import argparse
import requests
from pathlib import Path
from typing import List, Optional, Dict, Any


def check_langflow_running(base_url: str) -> bool:
    """Check if Langflow is running."""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_folders(base_url: str, api_key: str) -> List[Dict[str, Any]]:
    """Get all folders/projects in Langflow."""
    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }

    try:
        response = requests.get(f"{base_url}/api/v1/folders/", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Warning: Could not fetch folders: {e}")

    return []


def create_folder(base_url: str, api_key: str, folder_name: str) -> Optional[str]:
    """Create a new folder and return its ID."""
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    data = {
        "name": folder_name,
        "description": "Imported flows from repository"
    }

    try:
        response = requests.post(
            f"{base_url}/api/v1/folders/",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code in (200, 201):
            result = response.json()
            return result.get("id")
        else:
            print(f"Error creating folder: HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"Error creating folder: {e}")
        return None


def get_or_create_target_folder(base_url: str, api_key: str) -> Optional[str]:
    """Get existing folder or create a new one for imports."""
    print("Checking for existing folders...")

    folders = get_folders(base_url, api_key)

    if folders:
        # Use the first folder found
        folder = folders[0]
        folder_id = folder.get("id")
        folder_name = folder.get("name", "Unnamed Folder")
        print(f"✓ Found existing folder: '{folder_name}'")
        print(f"  Folder ID: {folder_id}")
        print(f"  Will import all flows to this folder\n")
        return folder_id
    else:
        # No folders exist, create one
        print("No folders found. Creating a new folder...")
        folder_name = "Voxhive Flows"
        folder_id = create_folder(base_url, api_key, folder_name)

        if folder_id:
            print(f"✓ Created folder: '{folder_name}'")
            print(f"  Folder ID: {folder_id}")
            print(f"  Will import all flows to this folder\n")
            return folder_id
        else:
            print("✗ Failed to create folder")
            print("  Will import flows to root level\n")
            return None


def get_flow_files(flows_dir: str = "flows") -> List[Path]:
    """Get all flow JSON files from directory."""
    flows_path = Path(flows_dir)

    if not flows_path.exists():
        print(f"Error: {flows_dir} directory not found")
        return []

    # Get all JSON files except manifest
    flow_files = [
        f for f in flows_path.glob("*.json")
        if f.name not in ["manifest.json"]
    ]

    return sorted(flow_files)


def get_existing_flows(base_url: str, api_key: str) -> set:
    """Get names of existing flows."""
    headers = {"accept": "application/json", "x-api-key": api_key}

    try:
        response = requests.get(f"{base_url}/api/v1/flows/", headers=headers, timeout=10)
        if response.status_code == 200:
            flows = response.json()
            return {flow.get("name") for flow in flows}
    except:
        pass

    return set()


def inject_folder_id_into_flow(flow_data: dict, folder_id: str) -> dict:
    """Inject the current folder ID into Progress Agent Builder components."""
    nodes = flow_data.get("data", {}).get("nodes", [])

    for node in nodes:
        node_data = node.get("data", {})
        # Check if this is a Progress Agent Builder component
        if node_data.get("type") == "ProgressAgentBuilder":
            template = node_data.get("node", {}).get("template", {})
            # Inject the folder_id into the template
            if "folder_id" in template:
                template["folder_id"]["value"] = folder_id

    return flow_data


def update_flow_components(base_url: str, api_key: str, flow_id: str) -> bool:
    """Update all components in a flow to latest versions."""
    try:
        headers = {
            "accept": "application/json",
            "x-api-key": api_key,
        }

        # First get the flow to update its components
        response = requests.get(
            f"{base_url}/api/v1/flows/{flow_id}",
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            return False

        flow_data = response.json()

        # Update the flow (this triggers component updates)
        update_response = requests.patch(
            f"{base_url}/api/v1/flows/{flow_id}",
            headers={**headers, "Content-Type": "application/json"},
            json=flow_data,
            timeout=30
        )

        return update_response.status_code in (200, 201)

    except Exception:
        return False


def import_flow(base_url: str, api_key: str, flow_file: Path, folder_id: Optional[str] = None) -> Optional[str]:
    """Import a single flow file into Langflow. Returns flow_id if successful."""
    try:
        # Read the flow file
        with open(flow_file, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)

        # If we have a folder_id, inject it into Progress Agent Builder components
        if folder_id:
            flow_data = inject_folder_id_into_flow(flow_data, folder_id)

        # Prepare the upload
        headers = {
            "accept": "application/json",
            "x-api-key": api_key,
        }

        # Build URL with folder_id
        url = f"{base_url}/api/v1/flows/upload/"
        if folder_id:
            url += f"?folder_id={folder_id}"

        # Upload the flow
        files = {
            "file": (flow_file.name, json.dumps(flow_data), "application/json")
        }

        response = requests.post(url, headers=headers, files=files, timeout=30)

        if response.status_code in (200, 201):
            # Get the imported flow ID from response
            result = response.json()
            
            # Handle case where result is a list (some Langflow versions)
            if isinstance(result, list) and len(result) > 0:
                result = result[0]
            
            flow_id = result.get("id")

            # Auto-update components to latest versions
            if flow_id:
                update_flow_components(base_url, api_key, flow_id)

            return flow_id
        else:
            print(f"    Error: HTTP {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"    Error: {str(e)}")
        return None


def import_all_flows(
    base_url: str = "http://localhost:7860",
    api_key: str = None,
    flows_dir: str = "flows",
    skip_existing: bool = True
):
    """Smart import: auto-detect or create folder, then import all flows."""

    # Check API key
    if not api_key:
        api_key = os.getenv("LANGFLOW_API_KEY")

    if not api_key:
        print("Error: API key required. Set LANGFLOW_API_KEY environment variable or use --api-key flag")
        return False

    # Check if Langflow is running
    print(f"Checking if Langflow is running on {base_url}...")
    if not check_langflow_running(base_url):
        print(f"\n✗ Error: Langflow is not running on {base_url}")
        print("  Please start Langflow first:")
        print("    uv run langflow run")
        return False
    print("✓ Langflow is running\n")

    # Get or create target folder
    folder_id = get_or_create_target_folder(base_url, api_key)

    # Get all flow files
    flow_files = get_flow_files(flows_dir)

    if not flow_files:
        print("No flow files found to import")
        return False

    print(f"Found {len(flow_files)} flow file(s) to import\n")

    # Get existing flows if skip_existing is True
    existing_flow_names = set()
    if skip_existing:
        existing_flow_names = get_existing_flows(base_url, api_key)
        if existing_flow_names:
            print(f"Found {len(existing_flow_names)} existing flow(s) - will skip duplicates\n")

    # Import each flow
    print("="*60)
    print("Importing flows...")
    print("="*60)

    imported = 0
    skipped = 0
    failed = 0

    for flow_file in flow_files:
        # Extract flow name from file
        flow_name = flow_file.stem
        try:
            with open(flow_file, 'r', encoding='utf-8') as f:
                flow_data = json.load(f)
                flow_name = flow_data.get("name", flow_name)
        except:
            pass

        print(f"\n📄 {flow_name}")

        # Check if flow already exists
        if skip_existing and flow_name in existing_flow_names:
            print(f"   ⏭️  Skipped (already exists)")
            skipped += 1
            continue

        # Import the flow
        imported_id = import_flow(base_url, api_key, flow_file, folder_id)
        if imported_id:
            print(f"   ✓ Imported successfully")
            print(f"     ID: {imported_id}")
            imported += 1
            
            # Check if this is the Unified Agent flow and save its ID
            if "Appointment Scheduler (Unified)" in flow_name:
                try:
                    config_path = Path("flow_config.json")
                    with open(config_path, "w") as f:
                        json.dump({"flow_id": imported_id}, f, indent=2)
                    print(f"   💾 Saved Flow ID to {config_path}")
                except Exception as e:
                    print(f"   ⚠️ Failed to save flow config: {e}")
        else:
            print(f"   ✗ Failed to import")
            failed += 1

    # Print summary
    print("\n" + "="*60)
    print(f"Import Summary:")
    print(f"  ✓ Imported: {imported}")
    if skipped > 0:
        print(f"  ⏭️  Skipped:  {skipped}")
    if failed > 0:
        print(f"  ✗ Failed:   {failed}")
    print("="*60)

    if imported > 0:
        print(f"\n✓ Successfully imported {imported} flow(s)!")
        if folder_id:
            print(f"  Open {base_url}/all/folder/{folder_id} to see them")
        else:
            print(f"  Open {base_url}/flows to see them")

        print("\n💡 Remember: API keys were removed for security.")
        print("   You need to add your OpenAI API key to each flow in Langflow UI")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Smart Langflow flow importer with auto folder management"
    )
    parser.add_argument(
        "--api-key",
        help="Langflow API key (or set LANGFLOW_API_KEY env var)",
        default=None
    )
    parser.add_argument(
        "--base-url",
        help="Langflow base URL (default: http://localhost:7860)",
        default="http://localhost:7860"
    )
    parser.add_argument(
        "--flows-dir",
        help="Directory containing flow JSON files (default: flows)",
        default="flows"
    )
    parser.add_argument(
        "--force",
        help="Import all flows even if they already exist",
        action="store_true"
    )

    args = parser.parse_args()

    success = import_all_flows(
        base_url=args.base_url,
        api_key=args.api_key,
        flows_dir=args.flows_dir,
        skip_existing=not args.force
    )

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
