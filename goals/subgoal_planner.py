"""Decompose a high-level goal into concrete subgoals."""
from __future__ import annotations

from typing import List
import logging
import os

from utils.json_utils import parse_json_safe
from llm_client import get_client
from cfg.config import PROMPTS, MODELS, TEMPERATURES

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = PROMPTS['subgoal_planner_system']


def decompose_goal(
    goal: str,
    context: str = "",
    *,
    model: str = MODELS['subgoal'],
    temperature: float = TEMPERATURES['subgoal'],
) -> List[str]:
    """Return a list of subgoals decomposed from ``goal``."""
    client = get_client(os.getenv("OPENAI_API_KEY"))
    if client is None:
        raise EnvironmentError("OPENAI_API_KEY not set or client unavailable")

    user_content = f"Ziel: {goal}"
    if context:
        user_content += f"\nKontext: {context}"

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    try:
        if hasattr(client, "chat"):
            response = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=messages,
            )
            text = response.choices[0].message.content
        else:
            response = client.ChatCompletion.create(
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
