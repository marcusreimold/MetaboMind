import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from control.cycle_manager import CycleManager


def setup_common(monkeypatch, cm):
    monkeypatch.setattr(cm.graph, "_save_goal_graph", lambda: None)
    monkeypatch.setattr(cm.graph, "save_graph", lambda: None)
    monkeypatch.setattr("control.cycle_manager.extract_triplets_via_llm", lambda text: [])
    monkeypatch.setattr("control.cycle_manager.generate_reflection", lambda **k: {"reflection": ""})


def test_goal_switch(monkeypatch):
    cm = CycleManager(api_key=None, logger=None)
    setup_common(monkeypatch, cm)
    monkeypatch.setattr("control.cycle_manager.propose_goal", lambda t, api_key=None: "Neu")
    monkeypatch.setattr("control.cycle_manager.check_goal_shift", lambda cur, new, api_key=None: True)
    called = {}
    def fake_apply(cur, new, gm, graph):
        called["args"] = (cur, new)
        gm.set_goal(new)
    monkeypatch.setattr("control.cycle_manager.apply_goal_shift", fake_apply)
    cm.current_goal = "Alt"
    res = cm.run_cycle("irgendwas")
    assert cm.current_goal == "Neu"
    assert res["goal"] == "Neu"
    assert called["args"] == ("Alt", "Neu")
    assert "Neues Ziel" in res["goal_update"]


def test_no_goal_switch(monkeypatch):
    cm = CycleManager(api_key=None, logger=None)
    setup_common(monkeypatch, cm)
    monkeypatch.setattr("control.cycle_manager.propose_goal", lambda t, api_key=None: None)
    cm.current_goal = "Alt"
    res = cm.run_cycle("etwas")
    assert cm.current_goal == "Alt"
    assert res["goal_update"] == ""


def test_first_goal(monkeypatch):
    cm = CycleManager(api_key=None, logger=None)
    setup_common(monkeypatch, cm)
    monkeypatch.setattr("control.cycle_manager.propose_goal", lambda t, api_key=None: "Start")
    cm.current_goal = ""
    res = cm.run_cycle("hey")
    assert cm.current_goal == "Start"
    assert res["goal"] == "Start"
    assert res["goal_update"] == ""
