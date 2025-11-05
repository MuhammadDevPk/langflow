#!/usr/bin/env python3
"""
Fix flows where custom component code was accidentally replaced with placeholders.

This script restores the Progress Agent Builder component code in flows
where it was mistakenly replaced with "YOUR_API_KEY_HERE" during secret scrubbing.
"""

import json
from pathlib import Path


def get_progress_agent_builder_code():
    """Return the correct Progress Agent Builder component code."""
    # Try to read from the latest version file
    for version_file in ["progress_agent_builder_v4.py", "progress_agent_builder_v3.py",
                         "progress_agent_builder_v2.py", "progress_agent_builder_final.py"]:
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            continue

    return None


def fix_flow_file(flow_path: Path, component_code: str) -> bool:
    """Fix a single flow file by restoring component code."""
    try:
        with open(flow_path, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)

        fixed = False
        nodes = flow_data.get("data", {}).get("nodes", [])

        for node in nodes:
            node_data = node.get("data", {})
            if node_data.get("type") == "ProgressAgentBuilder":
                template = node_data.get("node", {}).get("template", {})
                code_field = template.get("code", {})

                # Check if code was corrupted
                if code_field.get("value") == "YOUR_API_KEY_HERE":
                    code_field["value"] = component_code
                    fixed = True
                    print(f"  ✓ Fixed Progress Agent Builder code")

        if fixed:
            # Save the fixed flow
            with open(flow_path, 'w', encoding='utf-8') as f:
                json.dump(flow_data, f, indent=2, ensure_ascii=False)
            return True

        return False

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Fix all flows in the flows/ directory."""
    print("Looking for Progress Agent Builder component code...")

    component_code = get_progress_agent_builder_code()

    if not component_code:
        print("✗ Error: Could not find Progress Agent Builder code files")
        print("  Please ensure progress_agent_builder_v*.py files exist in the current directory")
        return 1

    print(f"✓ Found component code ({len(component_code)} characters)\n")

    flows_dir = Path("flows")
    if not flows_dir.exists():
        print("✗ Error: flows/ directory not found")
        return 1

    flow_files = list(flows_dir.glob("*.json"))
    if not flow_files:
        print("✗ No flow files found in flows/ directory")
        return 1

    print(f"Checking {len(flow_files)} flow file(s)...\n")

    fixed_count = 0
    for flow_file in flow_files:
        if flow_file.name == "manifest.json":
            continue

        print(f"📄 {flow_file.name}")

        if fix_flow_file(flow_file, component_code):
            fixed_count += 1
        else:
            print(f"  • No issues found")

    print(f"\n{'='*60}")
    print(f"Fixed {fixed_count} flow(s)")
    print(f"{'='*60}")

    if fixed_count > 0:
        print("\n✓ Flows have been repaired!")
        print("  You can now commit and push the fixed flows")

    return 0


if __name__ == "__main__":
    exit(main())
