import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from control import takt_engine


class DummyMem:
    def __init__(self):
        self.val = 0.0
        self.graph = types.SimpleNamespace(add_goal_transition=lambda a,b: None)

    def calculate_entropy(self):
        return 0.4

    def load_last_entropy(self):
        return 0.2

    def store_last_entropy(self, value):
        self.val = value

    def map_entropy_to_emotion(self, delta):
        return {"delta": delta, "emotion": "neutral", "intensity": "low"}

    def store_reflection(self, reflection):
        self.reflection = reflection

    def load_reflection(self):
        return ""


def setup(monkeypatch, change_goal=False):
    mem = DummyMem()
    monkeypatch.setattr(takt_engine, "MemoryManager", lambda: mem)
    monkeypatch.setattr(takt_engine.goal_engine, "get_current_goal", lambda: "A")
    if change_goal:
        monkeypatch.setattr(takt_engine.goal_engine, "update_goal", lambda **k: "B")
    else:
        monkeypatch.setattr(takt_engine.goal_engine, "update_goal", lambda **k: "A")
    monkeypatch.setattr(takt_engine, "run_llm_task", lambda *a, **k: "ref")
    return mem


def test_metabotakt_no_change(monkeypatch):
    mem = setup(monkeypatch, change_goal=False)
    res = takt_engine.run_metabotakt(api_key=None)
    assert res["goal"] == "A"
    assert res["goal_update"] == ""
    assert mem.val == 0.4


def test_metabotakt_goal_change(monkeypatch):
    mem = setup(monkeypatch, change_goal=True)
    res = takt_engine.run_metabotakt(api_key=None)
    assert res["goal"] == "B"
    assert "Neues Ziel" in res["goal_update"]
