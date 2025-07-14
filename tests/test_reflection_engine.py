import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from reflection import reflection_engine


def setup_common(monkeypatch):
    class DummyClient:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(create=self.create)
            )
        def create(self, *a, **k):
            return types.SimpleNamespace(
                choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="resp"))]
            )
    monkeypatch.setattr(reflection_engine, "get_client", lambda *a, **k: DummyClient())
    monkeypatch.setattr(reflection_engine, "run_llm_task", lambda *a, **k: "note")
    mem = types.SimpleNamespace(
        graph=types.SimpleNamespace(
            add_goal_transition=lambda a, b: setattr(mem, "edge", (a, b)),
        )
    )
    monkeypatch.setattr(reflection_engine, "get_memory_manager", lambda: mem)
    calls = {}
    monkeypatch.setattr(reflection_engine.goal_manager, "set_goal", lambda g: calls.setdefault("goal", g))
    return mem, calls


def test_goal_switch(monkeypatch):
    mem, calls = setup_common(monkeypatch)
    monkeypatch.setattr(reflection_engine, "detect_goal_shift", lambda *a, **k: (True, "Musik"))
    res = reflection_engine.generate_reflection("Bitte beschäftige dich mit Musik", "Sport", "", [])
    assert calls["goal"] == "Musik"
    assert mem.edge == ("Sport", "Musik")
    assert res["explanation"] == "note"


def test_no_goal_switch(monkeypatch):
    mem, calls = setup_common(monkeypatch)
    monkeypatch.setattr(reflection_engine, "detect_goal_shift", lambda *a, **k: (False, None))
    res = reflection_engine.generate_reflection("Hallo", "Sport", "", [])
    assert "goal" not in calls
    assert not hasattr(mem, "edge")
    assert res["explanation"] == ""

