from pathlib import Path

from src.memory_store import KnowledgeGraphMemory
from src.memory.logs import MemoryEventLogger


def test_memory_deletion_audited(tmp_path: Path):
    log_dir = tmp_path / "memlog"
    logger = MemoryEventLogger(log_dir)
    kg = KnowledgeGraphMemory(event_logger=logger)
    kg.create_entity("user:123", "person", ["sensitive:email"])
    assert kg.get_entity("user:123") is not None
    ok = kg.delete_entity("user:123", reason="dsr-delete")
    assert ok and kg.get_entity("user:123") is None
    # Verify log contains deletion event
    log_path = logger.path
    assert log_path.exists()
    lines = [l for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert any('"delete_entity"' in l or 'delete_entity' in l for l in lines)

