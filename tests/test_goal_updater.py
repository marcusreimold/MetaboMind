import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from goals import goal_updater


def test_missing_openai(monkeypatch):
    monkeypatch.setattr(goal_updater, "openai", None)
    res = goal_updater.update_goal("hi", "old", "", [])
    assert res == "old"


def test_missing_api_key(monkeypatch):
    dummy = types.SimpleNamespace(ChatCompletion=types.SimpleNamespace(create=lambda **k: None))
    monkeypatch.setattr(goal_updater, "openai", dummy)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    res = goal_updater.update_goal("hi", "old", "", [])
    assert res == "old"


def test_new_goal(monkeypatch):
    dummy = types.SimpleNamespace()
    def create(model, temperature, messages):
        return {"choices": [{"message": {"content": "Untersuche X"}}]}
    dummy.ChatCompletion = types.SimpleNamespace(create=create)
    monkeypatch.setattr(goal_updater, "openai", dummy)
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    res = goal_updater.update_goal("frage", "Alt", "", [])
    assert res == "Untersuche X"


def test_explicit_command(monkeypatch):
    monkeypatch.setattr(goal_updater, "openai", None)
    res = goal_updater.update_goal("Beschäftige dich mit Z", "Alt", "", [])
    assert res == "Z"
