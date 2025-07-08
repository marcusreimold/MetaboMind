import os
import sys
import types
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import goal_engine


def test_missing_openai(monkeypatch):
    monkeypatch.setattr(goal_engine, "openai", None)
    with pytest.raises(ImportError):
        goal_engine.generate_next_input("Test")


def test_missing_api_key(monkeypatch):
    dummy = types.SimpleNamespace(ChatCompletion=types.SimpleNamespace(create=lambda **k: None))
    monkeypatch.setattr(goal_engine, "openai", dummy)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(EnvironmentError):
        goal_engine.generate_next_input("Test")


def test_fallback_default(monkeypatch):
    dummy = types.SimpleNamespace()
    def create(model, temperature, messages):
        return {"choices": [{"message": {"content": ""}}]}
    dummy.ChatCompletion = types.SimpleNamespace(create=create)
    monkeypatch.setattr(goal_engine, "openai", dummy)
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    out = goal_engine.generate_next_input("Goal")
    assert out == "Verantwortung ist der Preis der Freiheit."
