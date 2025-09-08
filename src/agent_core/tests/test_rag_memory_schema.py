from __future__ import annotations

from pathlib import Path

from src.agent_core.memory.rag_store import RAGMemory


def test_rag_memory_add_schema(tmp_path: Path) -> None:
    rag = RAGMemory(collection_name="test_collection", persist_directory=str(tmp_path))
    text = "x" * 2500  # ensures multiple chunks with 1000/200 chunking

    rag.add(text=text, source="unit-test", doc_id="doc-1")
    count = rag.get_collection_count()
    assert count >= 2  # at least two chunks expected

    # Peek into collection and validate required metadata fields
    try:
        data = rag.collection.peek(5)
    except Exception:
        data = rag.collection.get(limit=5)

    mds = data.get("metadatas", []) or []
    assert mds, "Expected metadata entries in collection"
    md0 = mds[0]

    required = [
        "document_id",
        "source",
        "chunk_id",
        "chunk_text",
        "created_at",
        "embedding_model",
        "language",
        "checksum",
    ]
    for k in required:
        assert k in md0, f"missing field: {k}"

    assert md0["document_id"] == "doc-1"
    assert md0["source"] == "unit-test"
    assert isinstance(md0["chunk_id"], str) and md0["chunk_id"].startswith("doc-1--chunk-")
    assert md0["embedding_model"] == rag.embedding_model_name

