import os, unittest

os.environ["ISA_TEST_MODE"] = "1"
from src.memory import KnowledgeGraphMemory


class TestMemory(unittest.TestCase):
    def test_crud(self):
        m = KnowledgeGraphMemory(path="tmp_mem.json")
        m.create_entity("RFID", "technology", ["Used in supply chain"])
        assert m.get_entity("RFID") is not None
        m.add_observations("RFID", ["HF/UHF bands"])
        assert "HF/UHF bands" in m.get_entity("RFID").observations
