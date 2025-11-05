#!/usr/bin/env python3
"""
Update Progress Agent Builder component code in all flows.
"""

import json
from pathlib import Path


def get_component_code():
    """Read the latest component code."""
    with open("progress_agent_builder_v4.py", 'r', encoding='utf-8') as f:
        return f.read()


def update_flow(flow_path: Path, new_code: str) -> bool:
    """Update component code in a flow."""
    try:
        with open(flow_path, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)

        updated = False
        nodes = flow_data.get("data", {}).get("nodes", [])

        for node in nodes:
            node_data = node.get("data", {})
            if node_data.get("type") == "ProgressAgentBuilder":
                template = node_data.get("node", {}).get("template", {})
                code_field = template.get("code", {})

                # Update the code
                code_field["value"] = new_code
                updated = True
                print(f"  ✓ Updated Progress Agent Builder code")

        if updated:
            with open(flow_path, 'w', encoding='utf-8') as f:
                json.dump(flow_data, f, indent=2, ensure_ascii=False)
            return True

        return False

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    print("Reading component code...")
    code = get_component_code()
    print(f"✓ Loaded {len(code)} characters\n")

    flows_dir = Path("flows")
    flow_files = list(flows_dir.glob("*.json"))

    print(f"Updating {len(flow_files)} flow(s)...\n")

    updated = 0
    for flow_file in flow_files:
        if flow_file.name == "manifest.json":
            continue

        print(f"📄 {flow_file.name}")
        if update_flow(flow_file, code):
            updated += 1
        else:
            print(f"  • No Progress Agent Builder found")

    print(f"\n{'='*60}")
    print(f"Updated {updated} flow(s)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
