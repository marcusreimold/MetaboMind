"""Determine if the active goal should change based on new context."""
from __future__ import annotations

import logging
import os
from typing import List, Tuple, Optional
import re

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    openai = None

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Du bist ein Ziel-Update-Modul im KI-System MetaboMind. "
    "Analysiere die Nutzereingabe, das bisherige Ziel, die letzte Reflexion und "
    "die Tripel aus dem Ged\u00e4chtnis. Erkennst du einen thematischen Fokuswechsel, "
    "dann formuliere ein neues, klares Ziel im Stil 'Untersuche X'. "
    "Ist kein deutlicher Wechsel vorhanden, gib exakt das alte Ziel wieder. "
    "Gib ausschlie\u00dflich das Ziel zur\u00fcck."
)


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

    if openai is None:
        logger.error("openai package not installed")
        return last_goal

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("No OpenAI API key provided")
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
        if hasattr(openai, "OpenAI"):
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                messages=messages,
            )
            text = response.choices[0].message.content
        else:
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
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

