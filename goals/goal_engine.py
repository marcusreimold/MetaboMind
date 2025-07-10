"""Generate new input statements to pursue a goal."""
from __future__ import annotations

import logging
import os
from typing import List, Tuple

from goals.goal_manager import GoalManager
from goals.goal_updater import update_goal as _llm_update_goal

from llm_client import get_client

logger = logging.getLogger(__name__)

_GOAL_MGR = GoalManager()

_SYSTEM_PROMPT = (
    "Du bist ein Denkagent in einem KI-System namens MetaboMind. "
    "Deine Aufgabe ist es, eine kurze, neue Aussage zu formulieren, "
    "die das folgende Ziel inhaltlich weiterverfolgt. Nutze dazu auch "
    "die letzte Reflexion, wenn vorhanden. Formuliere die Aussage in "
    "natürlicher Sprache, als würdest du einen neuen Gedanken entwickeln. "
    "Gib nur den einen Satz zurück – keine Erklärung, keine Wiederholung des Ziels."
)


def generate_next_input(
    goal: str,
    previous_reflection: str = "",
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
) -> str:
    """Generate a short statement that pursues ``goal`` further."""
    client = get_client(os.getenv("OPENAI_API_KEY"))
    if client is None:
        raise EnvironmentError("OPENAI_API_KEY not set or client unavailable")

    reflection = previous_reflection.strip()[:300] if previous_reflection else ""
    content = f"Ziel: {goal}"
    if reflection:
        content += f"\nLetzte Reflexion: {reflection}"

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": content},
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

    if not text or not text.strip():
        return "Verantwortung ist der Preis der Freiheit."
    return text.strip()


def get_current_goal() -> str:
    """Return the currently stored goal."""
    return _GOAL_MGR.get_goal()


def update_goal(
    user_input: str,
    last_reflection: str,
    triplets: List[Tuple[str, str, str]],
) -> str:
    """Determine and persist a new goal based on ``user_input``."""
    current = _GOAL_MGR.get_goal()
    new_goal = _llm_update_goal(
        user_input=user_input,
        last_goal=current,
        last_reflection=last_reflection,
        triplets=triplets,
    )
    if new_goal != current:
        _GOAL_MGR.set_goal(new_goal)
    return new_goal


if __name__ == "__main__":
    example = generate_next_input(
        "Was bedeutet Freiheit?",
        "Freiheit ist Selbstbestimmung.",
    )
    print(example)
