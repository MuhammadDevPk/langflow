#!/usr/bin/env python3
"""
Remove component version metadata from flow files to prevent update notifications.

This script strips version-specific metadata from all components in flow files,
ensuring they use the latest component versions when imported on any machine.
"""

import json
from pathlib import Path
from typing import Dict, Any


def remove_metadata_from_flow(flow_data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove component version metadata from a flow."""
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
                            fields_removed = []
                            for field in ["frozen", "is_input", "is_output", "official"]:
                                if field in component:
                                    component.pop(field)
                                    fields_removed.append(field)

                            if fields_removed:
                                component_name = component.get("display_name", "unknown")
                                print(f"      Removed {', '.join(fields_removed)} from {component_name}")

    return flow_data


def process_flow_file(flow_path: Path) -> bool:
    """Process a single flow file to remove component metadata."""
    try:
        with open(flow_path, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)

        # Remove metadata
        cleaned_data = remove_metadata_from_flow(flow_data)

        # Write back
        with open(flow_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Remove component metadata from all flows."""
    flows_dir = Path("flows")

    if not flows_dir.exists():
        print("Error: flows/ directory not found")
        return 1

    flow_files = [f for f in flows_dir.glob("*.json") if f.name != "manifest.json"]

    print(f"Processing {len(flow_files)} flow file(s)...\n")

    success_count = 0
    for flow_file in flow_files:
        print(f"📄 {flow_file.name}")
        if process_flow_file(flow_file):
            print(f"  ✓ Cleaned")
            success_count += 1

    print(f"\n{'='*60}")
    print(f"Successfully processed {success_count}/{len(flow_files)} files")
    print(f"{'='*60}")
    print("\nComponent metadata removed!")
    print("Flows will now use latest component versions on import.")

    return 0


if __name__ == "__main__":
    exit(main())
