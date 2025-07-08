from __future__ import annotations

import logging
from typing import Dict

from control.metabo_cycle import run_metabo_cycle
from goals.goal_manager import get_active_goal
from goals import subgoal_planner
from memory.recall_context import recall_context
from utils import intent_detector

logger = logging.getLogger(__name__)


def run_cycle(user_input: str) -> Dict[str, object]:
    """Coordinate goal pursuit, user intention and reflection."""
    intent = intent_detector.classify(user_input)

    recalled = []
    if intent in {"recall", "frage"}:
        try:
            recalled = recall_context(scope="conversation")
        except Exception as exc:
            logger.warning("context recall failed: %s", exc)

    goal = get_active_goal()
    if intent == "ziel":
        try:
            subgoal_planner.decompose_goal(goal)
        except Exception as exc:
            logger.warning("subgoal planning failed: %s", exc)

    if intent == "aktion":
        try:
            from goals import goal_executor
            user_input = goal_executor.run_next()
        except Exception as exc:
            logger.warning("goal execution failed: %s", exc)

    result = run_metabo_cycle(user_input)
    result["context_recall"] = recalled
    return {
        "antwort": result.get("reflection", ""),
        "ziel": result.get("goal", goal),
        "reflexion": result.get("reflection", ""),
        "triplets": result.get("triplets", []),
        "emotion": {"label": result.get("emotion", "neutral"), "delta": result.get("delta", 0.0)},
    }
