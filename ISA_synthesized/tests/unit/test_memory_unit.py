import os

os.environ["ISA_TEST_MODE"] = "1"
from src.memory import KnowledgeGraphMemory


def test_memory_unit(tmp_path):
    p = tmp_path / "mem.json"
    m = KnowledgeGraphMemory(path=str(p))
    m.create_entity("Barcode", "standard", ["EAN-13", "GTIN"])
    assert m.get_entity("Barcode").type == "standard"
