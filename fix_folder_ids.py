#!/usr/bin/env python3
"""
Remove empty folder_id fields from flow JSON files.

Langflow API rejects flows with folder_id: "" (empty string).
It expects either a valid UUID or the field to not exist.
"""

import json
from pathlib import Path


def fix_flow_file(flow_path: Path) -> bool:
    """Remove problematic folder_id fields from a flow file."""
    try:
        with open(flow_path, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)

        modified = False

        # Remove top-level folder_id if it's empty or exists
        if "folder_id" in flow_data:
            if flow_data["folder_id"] == "" or flow_data["folder_id"] is None:
                del flow_data["folder_id"]
                modified = True
                print(f"  ✓ Removed top-level folder_id")

        # Remove folder field if it exists
        if "folder" in flow_data:
            del flow_data["folder"]
            modified = True
            print(f"  ✓ Removed folder field")

        # Remove user_id if it exists
        if "user_id" in flow_data:
            del flow_data["user_id"]
            modified = True
            print(f"  ✓ Removed user_id field")

        if modified:
            with open(flow_path, 'w', encoding='utf-8') as f:
                json.dump(flow_data, f, indent=2, ensure_ascii=False)
            return True
        else:
            print(f"  • No changes needed")
            return False

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Fix all flow files."""
    flows_dir = Path("flows")

    if not flows_dir.exists():
        print("Error: flows/ directory not found")
        return 1

    flow_files = [f for f in flows_dir.glob("*.json") if f.name != "manifest.json"]

    print(f"Fixing {len(flow_files)} flow file(s)...\n")

    fixed_count = 0
    for flow_file in flow_files:
        print(f"📄 {flow_file.name}")
        if fix_flow_file(flow_file):
            fixed_count += 1

    print(f"\n{'='*60}")
    print(f"Fixed {fixed_count} flow(s)")
    print(f"{'='*60}")
    print("\nFlows are now ready to import!")
    print("Empty folder_id fields have been removed")


if __name__ == "__main__":
    exit(main())
