"""Determine if the active goal should change based on new context."""
from __future__ import annotations

import json
import logging
import os
from difflib import SequenceMatcher
from typing import List, Tuple, Optional
import re

from llm_client import get_client

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Du bist ein Ziel-Update-Modul im KI-System MetaboMind. "
    "Analysiere die Nutzereingabe, das bisherige Ziel, die letzte Reflexion und "
    "die Tripel aus dem Ged\u00e4chtnis. Erkennst du einen thematischen Fokuswechsel, "
    "dann formuliere ein neues, klares Ziel im Stil 'Untersuche X'. "
    "Ist kein deutlicher Wechsel vorhanden, gib exakt das alte Ziel wieder. "
    "Gib ausschlie\u00dflich das Ziel zur\u00fcck."
)

# ---------------------------------------------------------------------------
# Goal proposal and shift utilities

def propose_goal(user_input: str, api_key: str | None = None) -> Optional[str]:
    """Ask the LLM to propose a new goal based on ``user_input``."""
    client = get_client(api_key or os.getenv("OPENAI_API_KEY"))
    if client is None:
        return None

    messages = [
        {"role": "system", "content": "Pr\u00fcfe, ob der Nutzer ein neues Thema vorschl\u00e4gt."},
        {"role": "user", "content": user_input},
    ]
    functions = [
        {
            "name": "propose_goal",
            "description": "Neues Ziel extrahieren",
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
        logger.error("propose_goal failed: %s", exc)
    return None


def check_goal_shift(current_goal: str, proposed_goal: str, api_key: str | None = None) -> bool:
    """Return ``True`` if ``proposed_goal`` represents a significant change."""
    proposed_goal = proposed_goal.strip()
    if not proposed_goal:
        return False
    if not current_goal.strip():
        return True
    if proposed_goal.lower() == current_goal.lower():
        return False

    key = api_key or os.getenv("OPENAI_API_KEY")
    client = get_client(key)
    if client is not None:
        try:
            if hasattr(client, "embeddings"):
                resp = client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=[current_goal, proposed_goal],
                )
                vec1 = resp.data[0].embedding
                vec2 = resp.data[1].embedding
            else:
                resp = client.Embedding.create(
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


def apply_goal_shift(current_goal: str, new_goal: str, goal_manager, graph) -> None:
    """Persist ``new_goal`` and record transition from ``current_goal``."""
    if current_goal.strip():
        graph.add_goal_transition(current_goal, new_goal)
    else:
        graph.goal_graph.add_node(new_goal)
        graph._save_goal_graph()
    goal_manager.set_goal(new_goal)


def _extract_explicit_goal(text: str) -> Optional[str]:
    """Return an explicit goal mentioned in ``text``."""

    patterns = [
        r"besch[aä]ftige dich mit\s+(.+)",
        r"konzentriere dich auf\s+(.+)",
        r"fokussiere dich auf\s+(.+)",
        r"untersuche\s+(.+)",
        r"analysiere\s+(.+)",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def update_goal(
    user_input: str,
    last_goal: str,
    last_reflection: str,
    triplets: List[Tuple[str, str, str]],
) -> str:
    """Return a new goal if the focus changed, otherwise ``last_goal``."""
    explicit = _extract_explicit_goal(user_input)
    if explicit and explicit.lower() not in last_goal.lower():
        return explicit

    client = get_client(os.getenv("OPENAI_API_KEY"))
    if client is None:
        logger.error("No OpenAI client available")
        return last_goal

    facts = "; ".join([f"{s} {p} {o}" for s, p, o in triplets])

    user_content = f"Eingabe: {user_input}\nAktuelles Ziel: {last_goal}"
    if last_reflection.strip():
        user_content += f"\nLetzte Reflexion: {last_reflection.strip()}"
    if facts:
        user_content += f"\nTripel: {facts}"

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    try:
        if hasattr(client, "chat"):
            response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                messages=messages,
            )
            text = response.choices[0].message.content
        else:
            response = client.ChatCompletion.create(
                model="gpt-4o",
                temperature=0,
                messages=messages,
            )
            text = response["choices"][0]["message"]["content"]
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("LLM request failed: %s", exc)
        return last_goal

    new_goal = text.strip()
    if not new_goal:
        return last_goal
    return new_goal

