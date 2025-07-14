from __future__ import annotations

from pathlib import Path


class GoalManager:
    """Simple file-based goal management."""

    def __init__(
        self,
        path: str = "data/goal.txt",
        reflection_path: str = "data/last_reflection.txt",
    ) -> None:
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
        """Persist ``goal`` and mark it in the MetaboGraph."""
        self.goal_path.write_text(goal, encoding="utf-8")
        try:
            from memory.memory_manager import get_memory_manager

            mem = get_memory_manager()
            node = f"ziel:{goal}"
            G = mem.metabo_graph.graph
            G.add_node(node, typ="ziel", text=goal)
            G.nodes[node]["goal"] = True
            mem.metabo_graph.save()
        except Exception:
            pass

    def load_reflection(self) -> str:
        """Return the last reflection text if available."""
        try:
            return self.reflection_path.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            return ""

    def save_reflection(self, reflection: str) -> None:
        """Store the most recent reflection text."""
        self.reflection_path.write_text(reflection, encoding="utf-8")


_DEFAULT_MANAGER = GoalManager()


def set_goal(goal: str) -> None:
    """Convenience wrapper to store ``goal`` using the default manager."""
    _DEFAULT_MANAGER.set_goal(goal)


def get_active_goal() -> str:
    """Return the currently active goal using the default manager."""
    return _DEFAULT_MANAGER.get_goal()


def load_last_reflection() -> str:
    """Return the last saved reflection."""
    return _DEFAULT_MANAGER.load_reflection()


def save_last_reflection(text: str) -> None:
    """Persist ``text`` as the latest reflection."""
    _DEFAULT_MANAGER.save_reflection(text)
