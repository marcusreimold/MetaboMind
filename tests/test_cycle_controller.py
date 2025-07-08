import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from control import cycle_controller


def test_run_cycle_recall(monkeypatch):
    monkeypatch.setattr(cycle_controller.intent_detector, "classify", lambda t: "recall")
    called = {}
    def fake_recall(scope="global", limit=10):
        called['scope'] = scope
        return [{"subject": "A", "predicate": "p", "object": "B"}]
    monkeypatch.setattr(cycle_controller, "recall_context", fake_recall)
    monkeypatch.setattr(cycle_controller, "run_metabo_cycle", lambda x: {"reflection": "r", "goal": "g", "triplets": [], "emotion": "neutral", "delta": 0.0})
    res = cycle_controller.run_cycle("hi")
    assert called['scope'] == "conversation"
    assert res["antwort"] == "r"
