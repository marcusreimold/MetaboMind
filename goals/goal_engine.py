"""Generate new input statements to pursue a goal."""
from __future__ import annotations

import logging
import os
from typing import List, Tuple

from goals.goal_manager import GoalManager
from goals.goal_updater import update_goal as _llm_update_goal

from utils.llm_client import get_client
from cfg.config import PROMPTS, MODELS, TEMPERATURES

logger = logging.getLogger(__name__)

_GOAL_MGR = GoalManager()

_SYSTEM_PROMPT = PROMPTS['goal_engine_system']


def generate_next_input(
    goal: str,
    previous_reflection: str = "",
    model: str = MODELS['chat'],
    temperature: float = TEMPERATURES['generate_next_input'],
    *,
    mode_hint: str | None = None,
) -> str:
    """Generate a short statement that pursues ``goal`` further."""
    client = get_client(os.getenv("OPENAI_API_KEY"))
    if client is None:
        raise EnvironmentError("OPENAI_API_KEY not set or client unavailable")

    reflection = previous_reflection.strip()[:300] if previous_reflection else ""
    content = f"Ziel: {goal}"
    if reflection:
        content += f"\nLetzte Reflexion: {reflection}"

    messages = []
    if mode_hint:
        messages.append({"role": "system", "content": mode_hint})
    messages.extend([
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": content},
    ])

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
