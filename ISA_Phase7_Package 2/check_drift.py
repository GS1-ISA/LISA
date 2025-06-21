#!/usr/bin/env python3
# check_drift.py

import os
import yaml

def load_version(path="VERSION.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)

def check_templates():
    # Simulate a placeholder logic
    missing = []
    for template in ["phase7.md", "phase6.md"]:
        if not os.path.exists(f"docs/phases/{template}"):
            missing.append(template)
    return missing

def main():
    print("=== ISA Drift Detector ===")
    config = load_version()
    print("Target version:", config["version"])
    missing_files = check_templates()
    if missing_files:
        print("Missing templates:", missing_files)
        print("Drift detected. Expansion halted.")
    else:
        print("All templates found. Expansion safe.")

if __name__ == "__main__":
    main()
