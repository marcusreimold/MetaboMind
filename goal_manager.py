from __future__ import annotations

from pathlib import Path


class GoalManager:
    """Simple file-based goal management."""

    def __init__(self, path: str = "goals/current_goal.txt", reflection_path: str = "goals/last_reflection.txt") -> None:
        self.goal_path = Path(path)
        self.goal_path.parent.mkdir(parents=True, exist_ok=True)
        self.reflection_path = Path(reflection_path)
        self.reflection_path.parent.mkdir(parents=True, exist_ok=True)

    def get_goal(self) -> str:
        """Return the current goal or empty string if none exists."""
        try:
            return self.goal_path.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            return ""

    def set_goal(self, goal: str) -> None:
        """Persist ``goal`` for later retrieval."""
        self.goal_path.write_text(goal, encoding="utf-8")

    def load_reflection(self) -> str:
        """Return the last reflection text if available."""
        try:
            return self.reflection_path.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            return ""

    def save_reflection(self, reflection: str) -> None:
        """Store the most recent reflection text."""
        self.reflection_path.write_text(reflection, encoding="utf-8")
