import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from goals import goal_updater as goal_selector
from goals.goal_manager import GoalManager
from memory.intention_graph import IntentionGraph


def test_propose_goal_no_openai(monkeypatch):
    monkeypatch.setattr(goal_selector, "openai", None)
    assert goal_selector.propose_goal("hi") is None


def test_check_goal_shift_basic(monkeypatch):
    monkeypatch.setattr(goal_selector, "openai", None)
    assert goal_selector.check_goal_shift("A", "B")
    assert not goal_selector.check_goal_shift("Goal", "Goal")


def test_apply_goal_shift(tmp_path, monkeypatch):
    gm = GoalManager(path=str(tmp_path / "goal.txt"))
    ig = IntentionGraph(filepath=str(tmp_path / "g.gml"))
    called = {}
    monkeypatch.setattr(ig, "add_goal_transition", lambda a, b: called.setdefault("edge", (a, b)))
    goal_selector.apply_goal_shift("Old", "New", gm, ig)
    assert gm.get_goal() == "New"
    assert called["edge"] == ("Old", "New")
