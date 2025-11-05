#!/usr/bin/env python3
"""
Import Langflow flows from JSON files into Langflow database.

This script imports all flow JSON files from the flows/ directory
into your local Langflow instance via the API.

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
from typing import List


def get_flow_files(flows_dir: str = "flows") -> List[Path]:
    """Get all flow JSON files from directory."""
    flows_path = Path(flows_dir)

    if not flows_path.exists():
        print(f"Error: {flows_dir} directory not found")
        return []

    # Get all JSON files except manifest and README
    flow_files = [
        f for f in flows_path.glob("*.json")
        if f.name not in ["manifest.json"]
    ]

    return sorted(flow_files)


def import_flow(base_url: str, api_key: str, flow_file: Path, folder_id: str = None) -> bool:
    """Import a single flow file into Langflow."""
    try:
        # Read the flow file
        with open(flow_file, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)

        # Prepare the upload
        headers = {
            "accept": "application/json",
            "x-api-key": api_key,
        }

        # Build URL with optional folder_id
        url = f"{base_url}/api/v1/flows/upload/"
        if folder_id:
            url += f"?folder_id={folder_id}"

        # Upload the flow
        files = {
            "file": (flow_file.name, json.dumps(flow_data), "application/json")
        }

        response = requests.post(url, headers=headers, files=files, timeout=30)

        if response.status_code in (200, 201):
            return True
        else:
            print(f"    Error: HTTP {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"    Error: {str(e)}")
        return False


def import_all_flows(
    base_url: str = "http://localhost:7860",
    api_key: str = None,
    flows_dir: str = "flows",
    folder_id: str = None,
    skip_existing: bool = True
):
    """Import all flows from directory."""

    if not api_key:
        api_key = os.getenv("LANGFLOW_API_KEY")

    if not api_key:
        print("Error: API key required. Set LANGFLOW_API_KEY environment variable or use --api-key flag")
        return False

    # Get all flow files
    flow_files = get_flow_files(flows_dir)

    if not flow_files:
        print("No flow files found to import")
        return False

    print(f"Found {len(flow_files)} flow file(s) to import")
    print(f"Importing to {base_url}...")
    print()

    # Get existing flows if skip_existing is True
    existing_flow_names = set()
    if skip_existing:
        try:
            headers = {"accept": "application/json", "x-api-key": api_key}
            response = requests.get(f"{base_url}/api/v1/flows/", headers=headers, timeout=10)
            if response.status_code == 200:
                existing_flows = response.json()
                existing_flow_names = {flow.get("name") for flow in existing_flows}
                print(f"Found {len(existing_flow_names)} existing flow(s) in Langflow")
                print()
        except Exception as e:
            print(f"Warning: Could not fetch existing flows: {e}")
            print()

    # Import each flow
    imported = 0
    skipped = 0
    failed = 0

    for flow_file in flow_files:
        # Extract flow name from filename (remove UUID suffix)
        flow_name = flow_file.stem
        # Try to get the actual flow name from the file
        try:
            with open(flow_file, 'r', encoding='utf-8') as f:
                flow_data = json.load(f)
                flow_name = flow_data.get("name", flow_name)
        except:
            pass

        print(f"📄 {flow_name}")

        # Check if flow already exists
        if skip_existing and flow_name in existing_flow_names:
            print(f"   ⏭️  Skipped (already exists)")
            skipped += 1
            continue

        # Import the flow
        if import_flow(base_url, api_key, flow_file, folder_id):
            print(f"   ✓ Imported successfully")
            imported += 1
        else:
            print(f"   ✗ Failed to import")
            failed += 1

    # Print summary
    print()
    print("="*60)
    print(f"Import Summary:")
    print(f"  ✓ Imported: {imported}")
    if skipped > 0:
        print(f"  ⏭️  Skipped:  {skipped}")
    if failed > 0:
        print(f"  ✗ Failed:   {failed}")
    print("="*60)

    if imported > 0:
        print(f"\n✓ Successfully imported {imported} flow(s) to Langflow!")
        print(f"  Open {base_url}/flows to see them")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Import Langflow flows from JSON files"
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
        "--flows-dir",
        help="Directory containing flow JSON files",
        default="flows"
    )
    parser.add_argument(
        "--folder-id",
        help="Target folder ID in Langflow (optional)",
        default=None
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
        folder_id=args.folder_id,
        skip_existing=not args.force
    )

    if success:
        print("\n💡 Tip: After importing, you'll need to add your OpenAI API keys")
        print("   to the imported flows in Langflow UI (they were removed for security)")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
