from __future__ import annotations

from typing import Dict

from goals import goal_engine
from memory.memory_manager import get_memory_manager
from reflection.reflection_engine import run_llm_task
from cfg.config import PROMPTS


def run_metabotakt(api_key: str | None = None) -> Dict[str, object]:
    """Execute a Metabotakt without user input."""
    memory = get_memory_manager()
    current_goal = goal_engine.get_current_goal()

    last_entropy = memory.load_last_entropy()
    current_entropy = memory.calculate_entropy()
    delta = current_entropy - last_entropy
    memory.store_last_entropy(current_entropy)

    emotion = memory.map_entropy_to_emotion(delta)

    prompt = PROMPTS['takt_reflection'].format(goal=current_goal, delta=delta)
    reflection = run_llm_task(prompt, api_key=api_key)
    if reflection:
        memory.store_reflection(reflection)

    new_goal = goal_engine.update_goal(
        user_input=reflection,
        last_reflection=reflection,
        triplets=[],
    )
    goal_update = ""
    if new_goal != current_goal:
        memory.graph.add_goal_transition(current_goal, new_goal)
        current_goal = new_goal
        goal_update = f"Neues Ziel erkannt: {new_goal}"

    return {
        "goal": current_goal,
        "goal_update": goal_update,
        "entropy": current_entropy,
        "delta": delta,
        "emotion": emotion["emotion"],
        "intensity": emotion["intensity"],
        "reflection": reflection,
    }
