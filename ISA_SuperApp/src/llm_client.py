import logging
import os
import time
from typing import Any, Dict, List

import openai

from .logging_conf import setup_logging

setup_logging()
log = logging.getLogger("llm_client")


class StubLLM:
    def chat(self, messages: List[Dict[str, str]], model: str = "stub", **kw) -> Dict[str, Any]:
        user = next((m for m in messages[::-1] if m.get("role") == "user"), {"content": ""})
        c = user.get("content", "").lower()
        if "apples" in c:
            import re

            nums = list(map(int, re.findall(r"\d+", c)))
            ans = nums[0] + nums[1] - nums[2] if len(nums) >= 3 else 0
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": f"Final answer: {ans}. Thoughts: add then subtract.",
                        }
                    }
                ]
            }
        if "rfid" in c and "healthcare" in c:
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "Final answer: RFID is used in hospitals for tracking; trends: patient safety, inventory, UDI/ESG integration.",
                        }
                    }
                ]
            }
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Final answer: Stubbed offline answer.",
                    }
                }
            ]
        }


class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("ISA_API_KEY_OPENROUTER") or os.getenv("OPENROUTER_API_KEY")
        self.stub = None if self.api_key and os.getenv("ISA_TEST_MODE", "0") != "1" else StubLLM()
        log.info("LLM client mode: %s", "OPENROUTER" if not self.stub else "STUB")

    def _backoff(self, attempt: int) -> float:
        import random

        base = 0.5 * (2 ** min(attempt, 5))
        return base + random.random() * 0.2

    def chat(self, messages: List[Dict[str, str]], model: str, **kwargs) -> Dict[str, Any]:
        if self.stub:
            return self.stub.chat(messages, model=model, **kwargs)
        import requests

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://local-isa",
            "X-Title": "ISA Superdesign",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            **{k: v for k, v in kwargs.items() if v is not None},
        }
        t0 = time.time()
        attempts = 0
        while True:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            if resp.status_code == 200:
                data = resp.json()
                spent = resp.headers.get("x-openrouter-spend-cents")
                model_resp = data.get("model")
                dt = time.time() - t0
                if spent:
                    log.info(
                        "OpenRouter cost approx %s cents on model %s (%.2fs)", spent, model_resp, dt
                    )
                return data
            attempts += 1
            if attempts >= 3:
                log.error("OpenRouter error %s: %s", resp.status_code, resp.text[:200])
                raise RuntimeError("OpenRouter call failed")
            time.sleep(self._backoff(attempts))


class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=self.api_key)
        self.stub = None if self.api_key and os.getenv("ISA_TEST_MODE", "0") != "1" else StubLLM()
        log.info("LLM client mode: %s", "OPENAI" if not self.stub else "STUB")

    def chat(self, messages: List[Dict[str, str]], model: str, **kwargs) -> Dict[str, Any]:
        if self.stub:
            return self.stub.chat(messages, model=model, **kwargs)

        t0 = time.time()
        response = self.client.chat.completions.create(model=model, messages=messages, **kwargs)
        dt = time.time() - t0
        log.info("OpenAI call took %.2fs", dt)
        return response.model_dump()


def LLMClient():
    """Factory for LLM clients.

    If ISA_FORBID_DIRECT_LLM=1 is set, refuse to provide a client to enforce
    orchestrator-only policy in environments where direct calls are disallowed.
    """
    if os.getenv("ISA_FORBID_DIRECT_LLM", "0") == "1":
        raise RuntimeError("Direct LLM calls are forbidden by policy (ISA_FORBID_DIRECT_LLM=1)")
    provider = os.getenv("ISA_LLM_PROVIDER", "openrouter")
    if provider == "openai":
        return OpenAIClient()
    return OpenRouterClient()
