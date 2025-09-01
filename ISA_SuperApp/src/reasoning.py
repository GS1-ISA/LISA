import logging
from typing import List

from .llm_client import LLMClient
from .logging_conf import setup_logging
from .utils.routing import choose_model
from .utils.types import ReasoningResult, Thought

setup_logging()
log = logging.getLogger("reasoning")
SYSTEM_PROMPT = "You are a careful analyst. Think step-by-step. End with 'Final answer:' line."


class SequentialReasoner:
    def __init__(self, client=None):
        self.client = client or LLMClient()

    def run(self, question: str, context: str = "", max_steps: int = 5) -> ReasoningResult:
        thoughts: List[Thought] = []
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context: {context}\nQuestion: {question}"},
        ]
        for step in range(1, max_steps + 1):
            resp = self.client.chat(messages, model=choose_model("reason"), temperature=0.2)
            content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
            thoughts.append(Thought(content=content, number=step))
            messages.append({"role": "assistant", "content": content})
            if "Final answer:" in content:
                idx = content.lower().find("final answer:")
                ans = content[idx + 13 :].strip()
                return ReasoningResult(thoughts=thoughts, final_answer=ans)
        return ReasoningResult(
            thoughts=thoughts, final_answer=thoughts[-1].content if thoughts else "No answer."
        )
