#!/usr/bin/env python3
"""
Move flows to a specific folder or remove folder assignment.

This fixes the issue where imported flows have folder IDs from another
machine and aren't visible in the UI.

Usage:
    # Move all flows to a specific folder
    python move_flows_to_folder.py --api-key YOUR_KEY --folder-id FOLDER_ID

    # Remove folder assignment from all flows (move to root/My Files)
    python move_flows_to_folder.py --api-key YOUR_KEY --clear

    # Move specific flows by name pattern
    python move_flows_to_folder.py --api-key YOUR_KEY --folder-id FOLDER_ID --pattern "Voxie"
"""

import os
import argparse
import requests
from typing import Optional


def update_flow_folder(
    base_url: str,
    api_key: str,
    flow_id: str,
    folder_id: Optional[str] = None
) -> bool:
    """Update the folder assignment for a flow."""
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    # Prepare the update payload
    data = {}
    if folder_id is None:
        # Remove folder assignment
        data["folder_id"] = None
    else:
        data["folder_id"] = folder_id

    try:
        response = requests.patch(
            f"{base_url}/api/v1/flows/{flow_id}",
            headers=headers,
            json=data,
            timeout=10
        )

        return response.status_code in (200, 201)

    except Exception as e:
        print(f"    Error: {e}")
        return False


def get_all_flows(base_url: str, api_key: str):
    """Get all flows."""
    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }

    try:
        response = requests.get(f"{base_url}/api/v1/flows/", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching flows: {e}")

    return []


def move_flows(
    base_url: str = "http://localhost:7860",
    api_key: str = None,
    folder_id: Optional[str] = None,
    clear: bool = False,
    pattern: Optional[str] = None
):
    """Move flows to a folder or clear folder assignment."""

    if not api_key:
        api_key = os.getenv("LANGFLOW_API_KEY")

    if not api_key:
        print("Error: API key required")
        return False

    if not clear and not folder_id:
        print("Error: Either --folder-id or --clear must be specified")
        return False

    # Get all flows
    flows = get_all_flows(base_url, api_key)

    if not flows:
        print("No flows found")
        return False

    print(f"Found {len(flows)} flow(s)")

    # Filter by pattern if specified
    if pattern:
        flows = [f for f in flows if pattern.lower() in f.get("name", "").lower()]
        print(f"Filtered to {len(flows)} flow(s) matching '{pattern}'")

    if clear:
        print("Clearing folder assignments (moving to My Files)...\n")
        target_folder = None
    else:
        print(f"Moving flows to folder: {folder_id}\n")
        target_folder = folder_id

    # Update each flow
    updated = 0
    failed = 0

    for flow in flows:
        flow_id = flow.get("id")
        flow_name = flow.get("name", "Unnamed")
        current_folder = flow.get("folder_id", "root")

        print(f"📄 {flow_name}")
        print(f"   Current folder: {current_folder}")

        if update_flow_folder(base_url, api_key, flow_id, target_folder):
            print(f"   ✓ Updated successfully")
            updated += 1
        else:
            print(f"   ✗ Failed to update")
            failed += 1

        print()

    # Print summary
    print("="*60)
    print(f"Summary:")
    print(f"  ✓ Updated: {updated}")
    if failed > 0:
        print(f"  ✗ Failed:  {failed}")
    print("="*60)

    if updated > 0:
        print(f"\n✓ Successfully updated {updated} flow(s)!")
        if clear:
            print("  Flows are now visible in 'My Files'")
        else:
            print(f"  Open http://localhost:7860/all/folder/{folder_id} to see them")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Move flows to a folder or clear folder assignments"
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
        "--folder-id",
        help="Target folder ID to move flows to",
        default=None
    )
    parser.add_argument(
        "--clear",
        help="Clear folder assignments (move to My Files/root)",
        action="store_true"
    )
    parser.add_argument(
        "--pattern",
        help="Only move flows matching this name pattern",
        default=None
    )

    args = parser.parse_args()

    success = move_flows(
        base_url=args.base_url,
        api_key=args.api_key,
        folder_id=args.folder_id,
        clear=args.clear,
        pattern=args.pattern
    )

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
