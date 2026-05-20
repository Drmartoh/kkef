"""Lightweight GPT helpers guarded by OPENAI_* environment variables."""

from __future__ import annotations

import json

import environ
import requests

env = environ.Env()


class AIClient:
    """OpenAI-compatible JSON chat helper."""

    def __init__(self) -> None:
        self.token = env("OPENAI_API_KEY", default="")
        self.base_url = env("OPENAI_BASE_URL", default="https://api.openai.com/v1").rstrip("/")

    def is_configured(self) -> bool:
        return bool(self.token)

    def complete(self, system_prompt: str, user_prompt: str) -> str | None:
        if not self.is_configured():
            return None
        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": env("OPENAI_MODEL", default="gpt-4.1-mini"),
            "temperature": float(env("OPENAI_TEMPERATURE", default=0.2)),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        resp = requests.post(endpoint, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        body = resp.json()
        choices = body.get("choices") or []
        if not choices:
            return None
        return choices[0]["message"]["content"]


CLIENT = AIClient()


def summarize_text(long_text: str) -> tuple[str | None, bool]:
    """Returns (markdown, sourced_from_ai)."""

    system = (
        "You summarise county-level social impact dossiers "
        "for dignitaries. Keep tone factual, humane, bilingual friendly."
    )
    user_prompt = json.dumps({"source": long_text[:12000]}, ensure_ascii=False)
    completion = CLIENT.complete(system_prompt=system, user_prompt=user_prompt)
    return completion, CLIENT.is_configured()
