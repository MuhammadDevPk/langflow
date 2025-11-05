#!/usr/bin/env python3
"""
Re-scrub flows to use empty strings instead of placeholders.

This ensures flows import cleanly without showing dots or placeholder text.
"""

import json
from pathlib import Path
from typing import Any, Dict


def scrub_flow_properly(flow_data: Dict[str, Any], parent_key: str = None) -> Dict[str, Any]:
    """Scrub secrets properly - use empty strings, not placeholders."""
    if isinstance(flow_data, dict):
        for key, value in flow_data.items():
            # Skip scrubbing if this is component code
            if parent_key == "code" and key == "value":
                continue

            # Clear value fields for API keys
            if key == "value" and parent_key in ["api_key", "openai_api_key", "langflow_api_key", "folder_id"]:
                if isinstance(value, str) and len(value) > 0:
                    flow_data[key] = ""  # Empty string!
            elif isinstance(value, (dict, list)):
                flow_data[key] = scrub_flow_properly(value, parent_key=key)
    elif isinstance(flow_data, list):
        return [scrub_flow_properly(item, parent_key=parent_key) for item in flow_data]

    return flow_data


def rescrub_flow_file(flow_path: Path) -> bool:
    """Re-scrub a single flow file."""
    try:
        with open(flow_path, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)

        # Scrub the flow
        cleaned_data = scrub_flow_properly(flow_data)

        # Write back
        with open(flow_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Re-scrub all flows."""
    flows_dir = Path("flows")

    if not flows_dir.exists():
        print("Error: flows/ directory not found")
        return 1

    flow_files = [f for f in flows_dir.glob("*.json") if f.name != "manifest.json"]

    print(f"Re-scrubbing {len(flow_files)} flow file(s)...\n")

    success_count = 0
    for flow_file in flow_files:
        print(f"📄 {flow_file.name}")
        if rescrub_flow_file(flow_file):
            print(f"  ✓ Cleaned")
            success_count += 1

    print(f"\n{'='*60}")
    print(f"Successfully re-scrubbed {success_count}/{len(flow_files)} files")
    print(f"{'='*60}")
    print("\nFlows now have:")
    print("  • Empty API key fields (not placeholders)")
    print("  • Empty folder IDs (injected during import)")
    print("\nFlows are ready to commit!")


if __name__ == "__main__":
    exit(main())
