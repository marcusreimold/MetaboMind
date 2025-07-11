"""Shared OpenAI client utilities."""
from __future__ import annotations

import os

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    openai = None

_CLIENT = None


def get_client(api_key: str | None = None):
    """Return a cached OpenAI client or ``None`` if unavailable."""
    global _CLIENT
    if openai is None:
        return None
    if _CLIENT is None:
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            return None
        if hasattr(openai, "OpenAI"):
            _CLIENT = openai.OpenAI(api_key=key)
        else:
            openai.api_key = key
            _CLIENT = openai
    return _CLIENT



def init_client() -> None:
    """Initialize the global client if possible."""
    get_client(os.getenv("OPENAI_API_KEY"))
