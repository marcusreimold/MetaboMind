"""Decompose a high-level goal into concrete subgoals."""
from __future__ import annotations

from typing import List
import logging
import os

from utils.json_utils import parse_json_safe

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    openai = None

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Du bist ein Planungsagent in einem KI-System namens MetaboMind. "
    "Zerlege das folgende Ziel in 2 bis 5 umsetzbare Teilziele. "
    "Formuliere jedes Teilziel als kurzen Satz im Klartext. "
    "Gib eine JSON-Liste der Teilziele zur\xFCck."
)


def decompose_goal(
    goal: str,
    context: str = "",
    *,
    model: str = "gpt-4o-mini",
    temperature: float = 0.3,
) -> List[str]:
    """Return a list of subgoals decomposed from ``goal``."""
    if openai is None:
        raise ImportError("openai package not installed")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set")

    user_content = f"Ziel: {goal}"
    if context:
        user_content += f"\nKontext: {context}"

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    try:
        if hasattr(openai, "OpenAI"):
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=messages,
            )
            text = response.choices[0].message.content
        else:
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model=model,
                temperature=temperature,
                messages=messages,
            )
            text = response["choices"][0]["message"]["content"]
    except Exception as exc:
        logger.error("LLM request failed: %s", exc)
        text = ""

    subgoals: List[str] = []
    data = parse_json_safe(text)
    if isinstance(data, list) and all(isinstance(s, str) for s in data):
        subgoals = [s.strip() for s in data if s.strip()]
    else:
        lines = [line.strip("-•* \t") for line in text.splitlines() if line.strip()]
        if 2 <= len(lines) <= 5:
            subgoals = lines

    if not subgoals:
        logger.info("No subgoals parsed, returning goal as single item")
        subgoals = [goal.strip()]

    return subgoals
