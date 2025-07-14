from __future__ import annotations

from typing import Dict

from goals import goal_engine
from memory.memory_manager import get_memory_manager
from memory.graph_utils import process_triples
from reflection.reflection_engine import run_llm_task


def run_metabotakt(api_key: str | None = None) -> Dict[str, object]:
    """Execute a Metabotakt without user input."""
    memory = get_memory_manager()
    current_goal = goal_engine.get_current_goal()

    before = memory.calculate_entropy()

    prompt = (
        f"Reflektiere den aktuellen Stand: Ziel war {current_goal}."
    )
    reflection = run_llm_task(prompt, api_key=api_key)

    triple_data = process_triples(reflection, source="reflection") if reflection else {
        "triplets": [], "entropy_before": before, "entropy_after": before
    }

    if reflection:
        memory.store_reflection(reflection)

    after = triple_data["entropy_after"]
    memory.store_last_entropy(after)
    delta = after - before
    emotion = memory.map_entropy_to_emotion(delta)

    new_goal = goal_engine.update_goal(
        user_input=reflection,
        last_reflection=reflection,
        triplets=triple_data["triplets"],
    )
    goal_update = ""
    if new_goal != current_goal:
        memory.graph.add_goal_transition(current_goal or None, new_goal)
        current_goal = new_goal
        goal_update = f"Neues Ziel erkannt: {new_goal}"

    return {
        "goal": current_goal,
        "goal_update": goal_update,
        "entropy": after,
        "delta": delta,
        "emotion": emotion["emotion"],
        "intensity": emotion["intensity"],
        "reflection": reflection,
    }
