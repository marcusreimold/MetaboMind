"""Utilities for LLM-driven goal selection and application."""
from __future__ import annotations

import json
import logging
import os
from difflib import SequenceMatcher
from typing import Optional

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    openai = None

from goals.goal_manager import GoalManager
from memory.metabo_graph import MetaboGraph
from cfg.config import PROMPTS

logger = logging.getLogger(__name__)


_SYSTEM_PROMPT = PROMPTS['goal_selector_system']


def _build_client(api_key: str | None):
    if openai is None or not api_key:
        return None
    if hasattr(openai, "OpenAI"):
        return openai.OpenAI(api_key=api_key)
    openai.api_key = api_key
    return openai


def propose_goal(
    user_input: str,
    api_key: str | None = None,
    *,
    mode_hint: str | None = None,
) -> Optional[str]:
    """Ask the LLM to suggest a new goal based on ``user_input``."""
    client = _build_client(api_key or os.getenv("OPENAI_API_KEY"))
    if client is None:
        return None

    messages = []
    if mode_hint:
        messages.append({"role": "system", "content": mode_hint})
    messages.extend(
        [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ]
    )
    functions = [
        {
            "name": "propose_goal",
            "description": "Schlage ein neues Ziel vor",
            "parameters": {
                "type": "object",
                "properties": {"goal": {"type": "string"}},
                "required": ["goal"],
            },
        }
    ]

    try:
        if hasattr(client, "chat"):
            resp = client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                messages=messages,
                functions=functions,
                function_call="auto",
            )
            choice = resp.choices[0]
            if choice.finish_reason == "function_call":
                fc = choice.message.function_call
                if fc and fc.name == "propose_goal":
                    data = json.loads(fc.arguments)
                    return data.get("goal", "").strip()
        else:
            resp = client.ChatCompletion.create(
                model="gpt-4o",
                temperature=0,
                messages=messages,
                functions=functions,
                function_call="auto",
            )
            choice = resp["choices"][0]
            if choice.get("finish_reason") == "function_call":
                fc = choice["message"]["function_call"]
                if fc["name"] == "propose_goal":
                    data = json.loads(fc["arguments"])
                    return data.get("goal", "").strip()
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("LLM propose_goal failed: %s", exc)
    return None


def check_goal_shift(current_goal: str, proposed_goal: str, api_key: str | None = None) -> bool:
    """Return ``True`` if ``proposed_goal`` differs significantly from ``current_goal``."""
    proposed_goal = proposed_goal.strip()
    if not proposed_goal:
        return False
    if not current_goal.strip():
        return True
    if proposed_goal.lower() == current_goal.strip().lower():
        return False

    key = api_key or os.getenv("OPENAI_API_KEY")
    if openai is not None and key:
        try:
            if hasattr(openai, "OpenAI"):
                client = openai.OpenAI(api_key=key)
                resp = client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=[current_goal, proposed_goal],
                )
                vec1 = resp.data[0].embedding
                vec2 = resp.data[1].embedding
            else:
                openai.api_key = key
                resp = openai.Embedding.create(
                    model="text-embedding-ada-002",
                    input=[current_goal, proposed_goal],
                )
                vec1 = resp["data"][0]["embedding"]
                vec2 = resp["data"][1]["embedding"]
            from numpy import dot
            from numpy.linalg import norm

            sim = dot(vec1, vec2) / (norm(vec1) * norm(vec2))
            return sim < 0.8
        except Exception as exc:  # pragma: no cover - network errors
            logger.error("embedding similarity failed: %s", exc)

    ratio = SequenceMatcher(None, current_goal.lower(), proposed_goal.lower()).ratio()
    return ratio < 0.6


def apply_goal_shift(current_goal: str, new_goal: str, goal_manager: GoalManager, graph: MetaboGraph) -> None:
    """Persist the shift from ``current_goal`` to ``new_goal`` using ``MetaboGraph``."""
    if current_goal.strip():
        graph.add_goal_transition(current_goal, new_goal)
    else:
        graph.goal_graph.add_node(new_goal)
        graph._save_goal_graph()
    goal_manager.set_goal(new_goal)

