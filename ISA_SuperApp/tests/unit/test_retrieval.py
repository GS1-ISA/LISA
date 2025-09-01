import os, unittest

os.environ["ISA_TEST_MODE"] = "1"
from src.retrieval import VectorIndex


class TestRetrieval(unittest.TestCase):
    def test_lexical_search(self):
        idx = VectorIndex(storage_path="tmp_index.json")
        docs = [
            (
                "RFID",
                "RFID used in hospitals for asset tracking and patient safety",
                {"type": "technology"},
            ),
            ("Barcode", "Barcodes enable inventory management", {"type": "standard"}),
            ("ESG", "ESG reporting aligns with EU directives", {"type": "esg"}),
        ]
        idx.rebuild(docs)
        hits = idx.search("hospital tracking with rfid", k=2)
        assert hits and hits[0]["id"] == "RFID"
