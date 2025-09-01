import os, unittest

os.environ["ISA_TEST_MODE"] = "1"
from src.reasoning import SequentialReasoner


class TestReasoning(unittest.TestCase):
    def test_math(self):
        r = SequentialReasoner()
        res = r.run("Alice has 5 apples and buys 3 more, then gives 2 away. How many apples?")
        assert "6" in res.final_answer
