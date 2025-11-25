#!/usr/bin/env python3
"""
Cleanup script to remove all flows from the flows/ directory except for specific preserved files.
"""

import os
from pathlib import Path

def cleanup_flows():
    flows_dir = Path("flows")
    
    if not flows_dir.exists():
        print(f"Directory {flows_dir} does not exist.")
        return

    # Files to preserve
    PRESERVED_FILES = {
        "Basic Agent Blue Print_76c0c376-55c4-4da3-979a-5a541a97db24.json",
        "README.md",
        "manifest.json"
    }

    print(f"Cleaning up {flows_dir}...")
    
    deleted_count = 0
    preserved_count = 0

    for file_path in flows_dir.iterdir():
        if file_path.is_file():
            if file_path.name in PRESERVED_FILES:
                print(f"  Skipping (preserved): {file_path.name}")
                preserved_count += 1
            else:
                try:
                    file_path.unlink()
                    print(f"  Deleted: {file_path.name}")
                    deleted_count += 1
                except Exception as e:
                    print(f"  Error deleting {file_path.name}: {e}")

    print("\n" + "="*40)
    print(f"Cleanup Complete")
    print(f"Deleted: {deleted_count}")
    print(f"Preserved: {preserved_count}")
    print("="*40)

if __name__ == "__main__":
    cleanup_flows()
