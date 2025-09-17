# Vector Store Schema

This document defines the canonical schema, chunking strategy, and metadata fields for vector store entries used by the ISA project.

Last updated: 2025-09-04

## Embedding Model

- Embedding model: record exact model name and version used to encode text (e.g., `text-embedding-3-large@2025-08-01`).
- Changing the embedding model invalidates existing vectors; migrations must be recorded in `docs/CHANGELOG.md` and accompanied by reindexing guidance.

## Chunking Strategy

- Chunk size: default 1000 characters (configurable per source).
- Overlap: default 200 characters to preserve context across chunks.
- Split method: recursive character splitter prioritizing sentence boundaries.
- Store the original `chunk_text` verbatim for provenance and debugging.

## Metadata Schema

Each vector entry MUST include the following metadata fields (example JSON schema snippet):

- `document_id` (string): opaque id of the source document
- `document_version` (string|null): version tag or timestamp of the source document
- `source` (string): canonical source name (e.g., `iso-27001`, `internal-policy-hr`)
- `page` (int|null): page number if applicable
- `chunk_id` (string): unique id for the chunk (e.g., `{document_id}--chunk-{n}`)
- `chunk_text` (string): original chunk text
- `created_at` (string, ISO8601): ingestion timestamp
- `embedding_model` (string): embedding model used to produce this vector
- `language` (string): ISO language code, e.g., `en`
- `checksum` (string): SHA256 of the `chunk_text` for integrity checks
- `provenance` (object|null): optional structured provenance (e.g., `{ "source_uri": "https://...", "harvested_by": "scraper-2025-09-01" }`)

## Provenance & Lineage

- Every ingestion run must produce a manifest (JSON) linking `document_id` → source URI → ingestion timestamp → digest of raw document.
- Manifests are stored under `data/ingestion_manifests/` and referenced in the Data Source Catalog (`data/data_catalog.yaml`).
- Helper: `scripts/ingest_text.py` ingests a local UTF‑8 text and writes a manifest. Example:

```bash
python scripts/ingest_text.py --doc-id iso27001-v2023-01 \
  --source iso-27001 \
  --file docs/examples/iso27001_excerpt.txt
```

## Backwards Compatibility

- When metadata fields are extended, use optional fields with clear migration notes.
- Provide a migration script for reindexing when changing `embedding_model` or `chunking` strategy.

## Security & Privacy

- Do not store PII in `chunk_text` unless explicitly permitted; if stored, mark the entry with `sensitive: true` and encrypt storage per `docs/SECURITY.md`.

## Example entry (YAML)

```yaml
- document_id: "iso27001-v2023-01"
  document_version: "2023-01"
  source: "iso-27001"
  page: 12
  chunk_id: "iso27001-v2023-01--chunk-42"
  chunk_text: |
    ...chunk content...
  created_at: "2025-09-04T12:00:00Z"
  embedding_model: "text-embedding-3-large@2025-08-01"
  language: "en"
  checksum: "sha256:..."
  provenance:
    source_uri: "https://example.org/iso27001.pdf"
    harvested_by: "harvester-2025-09-03"
```

Current Implementation (this repository)
- Vector store: ChromaDB `PersistentClient` at `storage/vector_store/research_db` (see `src/agent_core/memory/rag_store.py`).
- Embeddings: SentenceTransformers `all-MiniLM-L6-v2` via Chroma’s `SentenceTransformerEmbeddingFunction`.
- RAGMemory binding (live): `RAGMemory.add(text, source, doc_id, page=None, extra_metadata=None)` now:
  - Chunks text at 1000 chars with 200-char overlap and writes one row per chunk.
  - Populates canonical metadata per chunk: `document_id`, `document_version` (None), `source`, `page`, `chunk_id`, `chunk_text`, `created_at` (ISO8601, UTC), `embedding_model`, `language` (default `en`), `checksum` (sha256 of `chunk_text`), `provenance` (None).
  - `extra_metadata` (dict) is merged into each chunk’s metadata for extensibility.

Validation Tool
- Run `python scripts/inspect_vector_store.py` to preview entries and validate required metadata fields exist. The tool connects to the default persistent directory and prints a short report.
