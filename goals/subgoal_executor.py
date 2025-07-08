"""Execute planned subgoals by activating the first one."""
from __future__ import annotations

import logging
from typing import List

from goals.goal_manager import set_goal

logger = logging.getLogger(__name__)


def execute_first_subgoal(original_goal: str, subgoals: List[str]) -> str:
    """Activate the first subgoal and return it.

    If ``subgoals`` is empty or the first item is blank, ``original_goal`` is
    kept as the active goal. The chosen goal is returned.
    """
    new_goal = subgoals[0].strip() if subgoals else ""
    if not new_goal:
        new_goal = original_goal
    set_goal(new_goal)
    logger.info("Active goal set to: %s", new_goal)
    return new_goal
