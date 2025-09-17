#!/usr/bin/env python3
"""Lightweight micro-POC runner.
Reads an ingestion manifest (YAML), creates an artifacts directory for run_id,
writes a minimal processed.json and experiments/{run_id}.yaml metadata file.
Designed to be safe and fast for PR CI (no external web crawling).
"""

import argparse
import os
import shutil
import sys
from datetime import datetime

import yaml


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def write_yaml(path, data):
    with open(path, "w") as f:
        yaml.safe_dump(data, f)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--run-id", default=None)
    args = p.parse_args()

    manifest_path = args.manifest
    out_dir = args.out
    run_id = args.run_id or datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    if not os.path.exists(manifest_path):
        print(f"Manifest not found: {manifest_path}")
        sys.exit(2)

    manifest = load_yaml(manifest_path)

    # Prepare artifact paths
    artifacts_raw = os.path.join(out_dir, "raw")
    artifacts_processed = os.path.join(out_dir, "processed")
    ensure_dir(artifacts_raw)
    ensure_dir(artifacts_processed)

    # Copy the manifest for traceability
    ensure_dir(os.path.dirname(os.path.join(out_dir, "manifest_copy")))
    shutil.copyfile(manifest_path, os.path.join(out_dir, "manifest_copy.yaml"))

    # Produce a tiny processed artifact as proof-of-run
    processed = {
        "run_id": run_id,
        "manifest_id": manifest.get("id"),
        "chunking": manifest.get("chunking", {}),
        "embedding_model": manifest.get("embedding", {}).get("model"),
        "items_processed": 0,
        "notes": "This is a smoke-run placeholder that does not perform real embedding.",
    }
    write_yaml(os.path.join(artifacts_processed, "processed.yaml"), processed)

    # Write experiment metadata to experiments/{run_id}.yaml
    experiments_dir = os.path.join("experiments")
    ensure_dir(experiments_dir)
    exp_meta = {
        "run_id": run_id,
        "manifest": manifest_path,
        "out": out_dir,
        "started_at": datetime.utcnow().isoformat() + "Z",
        "status": "success",
    }
    write_yaml(os.path.join(experiments_dir, f"{run_id}.yaml"), exp_meta)

    print(f"Completed micro-POC run {run_id}; artifacts in {out_dir}")


if __name__ == "__main__":
    main()
