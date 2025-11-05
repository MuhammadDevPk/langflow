#!/usr/bin/env python3
"""
List all flows in Langflow to verify they're actually there.
"""

import requests
import sys

def list_flows(api_key: str, base_url: str = "http://localhost:7860"):
    """List all flows in Langflow."""
    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }

    try:
        response = requests.get(f"{base_url}/api/v1/flows/", headers=headers, timeout=10)

        if response.status_code == 200:
            flows = response.json()
            print(f"Total flows in database: {len(flows)}\n")

            for i, flow in enumerate(flows, 1):
                print(f"{i}. {flow.get('name', 'Unnamed')}")
                print(f"   ID: {flow.get('id')}")
                print(f"   Folder: {flow.get('folder_id', 'root')}")
                print()

        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python list_flows.py YOUR_API_KEY")
        sys.exit(1)

    list_flows(sys.argv[1])
