#!/usr/bin/env python3
"""
Remove sensitive data (API keys, secrets) from exported Langflow flows.

This script processes all flow JSON files and replaces actual API keys
with placeholder values, making them safe to commit to version control.
"""

import json
from pathlib import Path
from typing import Any, Dict


def scrub_secrets_from_value(value: Any) -> Any:
    """Replace API keys and secrets with placeholders."""
    if isinstance(value, str):
        # Check if it looks like an OpenAI key
        if value.startswith("sk-") and len(value) > 20:
            return "sk-YOUR_OPENAI_API_KEY_HERE"
        # Check for other common API key patterns
        elif "api" in str(value).lower() and len(value) > 30:
            return "YOUR_API_KEY_HERE"
    return value


def scrub_flow_secrets(flow_data: Dict[str, Any], parent_key: str = None) -> Dict[str, Any]:
    """Recursively scrub secrets from flow data.

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

            # Check specific fields that might contain secrets
            if key in ["api_key", "openai_api_key", "value"] and isinstance(value, str):
                flow_data[key] = scrub_secrets_from_value(value)
            elif isinstance(value, (dict, list)):
                flow_data[key] = scrub_flow_secrets(value, parent_key=key)
    elif isinstance(flow_data, list):
        return [scrub_flow_secrets(item, parent_key=parent_key) for item in flow_data]

    return flow_data


def scrub_flow_file(file_path: Path) -> bool:
    """Scrub secrets from a single flow file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)

        # Scrub secrets
        cleaned_data = scrub_flow_secrets(flow_data)

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def scrub_all_flows(flows_dir: str = "flows") -> None:
    """Scrub secrets from all flow files."""
    flows_path = Path(flows_dir)

    if not flows_path.exists():
        print(f"Error: {flows_dir} directory not found")
        return

    # Get all JSON files except manifest
    flow_files = [f for f in flows_path.glob("*.json") if f.name != "manifest.json"]

    print(f"Scrubbing secrets from {len(flow_files)} flow files...")

    success_count = 0
    for flow_file in flow_files:
        if scrub_flow_file(flow_file):
            print(f"  ✓ {flow_file.name}")
            success_count += 1
        else:
            print(f"  ✗ {flow_file.name}")

    print(f"\n{'='*60}")
    print(f"Successfully scrubbed {success_count}/{len(flow_files)} files")
    print(f"{'='*60}")
    print("\nFlows are now safe to commit to Git!")


if __name__ == "__main__":
    scrub_all_flows()
