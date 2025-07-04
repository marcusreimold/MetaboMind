"""Verwaltet Aufgaben und speichert Fortschritt."""

import json
import time


class GoalManager:
    """Simple goal tracking for MetaboMind."""

    def __init__(self):
        # open goals yet to be completed
        self.goals = []
        # finished goals for history
        self.completed = []
        self.last_save = time.time()

    def add_goal(self, text: str):
        """Add a new goal with current timestamp."""
        self.goals.append({"text": text, "timestamp": time.time()})

    def complete_goal(self, index: int = 0):
        """Mark the given goal as finished."""
        if index < len(self.goals):
            goal = self.goals.pop(index)
            goal["completed"] = time.time()
            self.completed.append(goal)

    def remove_goal(self, index: int):
        """Delete a goal without completing it."""
        if index < len(self.goals):
            self.goals.pop(index)

    def active_goal(self):
        """Return text of the first active goal or ``None``."""
        return self.goals[0]["text"] if self.goals else None

    def save(self, path: str):
        """Write goals to JSON file."""
        data = {"goals": self.goals, "completed": self.completed}
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)

    def load(self, path: str):
        """Load goals from a JSON file."""
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.goals = data.get("goals", [])
        self.completed = data.get("completed", [])

    def autosave(self, path: str, interval: float = 60.0):
        """Periodically save to ``path`` every ``interval`` seconds."""
        now = time.time()
        if now - self.last_save >= interval:
            self.last_save = now
            self.save(path)
