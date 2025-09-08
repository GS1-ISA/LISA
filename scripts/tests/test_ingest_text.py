from __future__ import annotations

import hashlib
import sys
from importlib import import_module
from pathlib import Path


def test_ingest_text_writes_manifest(tmp_path, monkeypatch):
    # Work in a temp directory so vector store persistence is isolated
    monkeypatch.chdir(tmp_path)

    # Prepare input
    content = "This is a small test document for ingestion.\n" * 50
    infile = tmp_path / "doc.txt"
    infile.write_text(content, encoding="utf-8")
    checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()

    # Run CLI main via module import to avoid subprocess
    mod = import_module("scripts.ingest_text")
    argv_bak = sys.argv[:]
    out_dir = tmp_path / "manifests"
    sys.argv = [
        "ingest_text",
        "--doc-id",
        "doc-xyz",
        "--source",
        "unit-test",
        "--file",
        str(infile),
        "--out-dir",
        str(out_dir),
    ]
    try:
        rc = mod.main()
    finally:
        sys.argv = argv_bak
    assert rc == 0

    # Verify manifest
    manifest = out_dir / "doc-xyz.json"
    assert manifest.exists()
    import json

    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["document_id"] == "doc-xyz"
    assert data["source_uri"] == "unit-test"
    assert data["raw_checksum"].endswith(checksum)
    assert data["chunking"] == {"size": 1000, "overlap": 200}
