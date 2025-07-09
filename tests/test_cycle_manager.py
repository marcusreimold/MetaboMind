import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from control.cycle_manager import CycleManager


def test_is_new_topic():
    assert CycleManager.is_new_topic("Hallo Welt", "anderes Thema")
    assert not CycleManager.is_new_topic("Hallo Welt", "hallo welt und mehr")


def test_goal_switch(monkeypatch):
    cm = CycleManager(api_key=None, logger=None)
    monkeypatch.setattr(cm.graph, "_save_goal_graph", lambda: None)
    monkeypatch.setattr(cm.graph, "save_graph", lambda: None)
    cm.current_goal = "Alt"
    res = cm.run_cycle("Neu")
    assert cm.current_goal == "Neu"
    assert res["goal"] == "Neu"
    assert "Neues Ziel" in res["goal_update"]
