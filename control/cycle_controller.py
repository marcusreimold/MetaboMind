from __future__ import annotations

import logging
from typing import Dict

from control.metabo_cycle import run_metabo_cycle
from goals.goal_manager import get_active_goal, set_goal
from memory.recall_context import recall_context
from utils import intent_detector

logger = logging.getLogger(__name__)


def run_cycle(user_input: str) -> Dict[str, object]:
    """Coordinate goal pursuit, user intention and memory access."""
    intent = intent_detector.classify(user_input)

    recalled = []
    if intent in {"recall", "meta"}:
        try:
            recalled = recall_context(scope="conversation")
        except Exception as exc:
            logger.warning("context recall failed: %s", exc)

    # handle goal setting before running the main cycle
    if intent == "ziel":
        new_goal = user_input.split(maxsplit=1)[1] if " " in user_input else ""
        try:
            set_goal(new_goal)
        except Exception as exc:
            logger.warning("setting goal failed: %s", exc)
        result = {"reflection": "Neues Ziel gesetzt.", "goal": new_goal, "triplets": []}
    elif intent == "assist":
        try:
            from goals import goal_executor
            generated = goal_executor.run_next()
        except Exception as exc:
            logger.warning("goal execution failed: %s", exc)
            generated = ""
        result = run_metabo_cycle(generated)
    else:
        result = run_metabo_cycle(user_input)

    if recalled:
        result["context_recall"] = recalled
    goal = result.get("goal", get_active_goal())

    return {
        "antwort": result.get("reflection", ""),
        "reflexion": result.get("reflection", ""),
        "emotion": {"label": result.get("emotion", "neutral"), "delta": result.get("delta", 0.0)},
        "ziel": goal,
        "triplets": result.get("triplets", []),
    }
