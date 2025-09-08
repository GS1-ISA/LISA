"""Compatibility shim for tests importing `llm_runtime`.

Delegates to the canonical implementation under `src.llm.src.llm_runtime`.
"""
from src.llm.src.llm_runtime import (  # noqa: F401
    LlmRuntime,
    OpenAIResponsesStub,
    BedrockAgentsStub,
)

