from __future__ import annotations
import os, json
from typing import Dict, Any


class LLMResult(dict): ...


def _coerce_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        return {
            "decision": "reflect",
            "files": [],
            "patches": [],
            "notes": "non-json response",
            "next_action": "fix-output",
        }


class LLMClient:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.openai_base = os.getenv("OPENAI_BASE_URL", "").strip() or None
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = os.getenv("MODEL_NAME", "gpt-4o-mini")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2000"))
        self.backend = None
        if self.openai_key:
            from openai import OpenAI

            self.backend = ("openai", OpenAI(api_key=self.openai_key, base_url=self.openai_base))
        elif self.gemini_key:
            import google.generativeai as genai

            genai.configure(api_key=self.gemini_key)
            self.backend = ("gemini", genai.GenerativeModel(self.model))
        else:
            self.backend = ("dry", None)

    def complete_json(self, system: str, user: str) -> LLMResult:
        kind, client = self.backend
        if kind == "openai":
            resp = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=0,
                response_format={"type": "json_object"},
                max_tokens=self.max_tokens,
            )
            return LLMResult(_coerce_json(resp.choices[0].message.content))
        if kind == "gemini":
            prompt = f"SYSTEM:\n{system}\nUSER:\n{user}\nReturn pure JSON only."
            resp = client.generate_content(
                prompt,
                generation_config={"temperature": 0, "max_output_tokens": self.max_tokens},
                safety_settings=[],
            )
            text = resp.text or "{}"
            return LLMResult(_coerce_json(text))
        return LLMResult(
            {
                "decision": "plan",
                "files": [{"path": "out/dry_run.txt", "content": "dry run"}],
                "patches": [],
                "notes": "dry",
                "next_action": "implement",
            }
        )
