"""Utilities to run internal goal-driven actions."""

from __future__ import annotations

from goals.goal_engine import generate_next_input
from goals.goal_manager import get_active_goal, load_last_reflection


def run_next() -> str:
    """Generate the next statement towards the current goal."""
    goal = get_active_goal()
    reflection = load_last_reflection()
    return generate_next_input(goal, reflection)
