from __future__ import annotations

from typing import Any


class OpenAIResponsesStub:
    def chat(self, messages: list[dict[str, str]], model: str, **kw) -> dict[str, Any]:
        return {
            "model": model,
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Final answer: stub-openai",
                    }
                }
            ],
        }


class BedrockAgentsStub:
    def chat(self, messages: list[dict[str, str]], model: str, **kw) -> dict[str, Any]:
        return {
            "model": model,
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Final answer: stub-bedrock",
                    }
                }
            ],
        }


class LlmRuntime:
    def __init__(self, backend: str = "openai") -> None:
        self.backend = backend
        self._openai = OpenAIResponsesStub()
        self._bedrock = BedrockAgentsStub()

    def chat(self, messages: list[dict[str, str]], model: str, **kw) -> dict[str, Any]:
        if self.backend == "bedrock":
            return self._bedrock.chat(messages, model, **kw)
        return self._openai.chat(messages, model, **kw)
