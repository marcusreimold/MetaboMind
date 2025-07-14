import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from control.cycle_manager import CycleManager


def setup_common(monkeypatch, cm):
    monkeypatch.setattr(cm.memory.metabo_graph, "_save_goal_graph", lambda: None)
    monkeypatch.setattr(cm.memory.metabo_graph, "save", lambda: None)
    monkeypatch.setattr("control.cycle_manager.extract_triplets", lambda text, source="user_input": [])
    monkeypatch.setattr("control.cycle_manager.generate_reflection", lambda **k: {"reflection": ""})
    monkeypatch.setattr(cm.memory, "save_emotion", lambda *a, **k: {"delta": 0.0, "emotion": "neutral", "intensity": "low"})
    monkeypatch.setattr(cm.memory, "store_reflection", lambda text: None)


def test_goal_switch(monkeypatch):
    cm = CycleManager(api_key=None, logger=None)
    setup_common(monkeypatch, cm)
    monkeypatch.setattr(
        "control.cycle_manager.goal_engine.update_goal",
        lambda user_input, last_reflection, triplets, **kw: "Neu",
    )
    cm.current_goal = "Alt"
    res = cm.run_cycle("irgendwas")
    assert cm.current_goal == "Neu"
    assert res["goal"] == "Neu"
    assert "Neues Ziel" in res["goal_update"]


def test_no_goal_switch(monkeypatch):
    cm = CycleManager(api_key=None, logger=None)
    setup_common(monkeypatch, cm)
    monkeypatch.setattr(
        "control.cycle_manager.goal_engine.update_goal",
        lambda *args, **kw: cm.current_goal,
    )
    cm.current_goal = "Alt"
    res = cm.run_cycle("etwas")
    assert cm.current_goal == "Alt"
    assert res["goal_update"] == ""


def test_first_goal(monkeypatch):
    cm = CycleManager(api_key=None, logger=None)
    setup_common(monkeypatch, cm)
    monkeypatch.setattr(
        "control.cycle_manager.goal_engine.update_goal",
        lambda *args, **kw: "Start",
    )
    cm.current_goal = ""
    res = cm.run_cycle("hey")
    assert cm.current_goal == "Start"
    assert res["goal"] == "Start"
    assert "Neues Ziel" in res["goal_update"]
