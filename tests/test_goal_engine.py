import os
import sys
import types
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from goals import goal_engine


def test_missing_openai(monkeypatch):
    monkeypatch.setattr(goal_engine, "get_client", lambda *a, **k: None)
    with pytest.raises(EnvironmentError):
        goal_engine.generate_next_input("Test")


def test_missing_api_key(monkeypatch):
    monkeypatch.setattr(goal_engine, "get_client", lambda *a, **k: None)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(EnvironmentError):
        goal_engine.generate_next_input("Test")


def test_fallback_default(monkeypatch):
    class Dummy:
        def __init__(self):
            self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=self.create))

        def create(self, *a, **k):
            return types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=""))])

    monkeypatch.setattr(goal_engine, "get_client", lambda *a, **k: Dummy())
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    out = goal_engine.generate_next_input("Goal")
    assert out == "Verantwortung ist der Preis der Freiheit."
