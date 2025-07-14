import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from goals import goal_updater


def test_missing_openai(monkeypatch):
    monkeypatch.setattr(goal_updater, "get_client", lambda *a, **k: None)
    res = goal_updater.update_goal("hi", "old", "", [])
    assert res == "old"


def test_missing_api_key(monkeypatch):
    monkeypatch.setattr(goal_updater, "get_client", lambda *a, **k: None)
    res = goal_updater.update_goal("hi", "old", "", [])
    assert res == "old"


def test_new_goal(monkeypatch):
    class Dummy:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(create=self.create)
            )

        def create(self, *args, **kwargs):
            return types.SimpleNamespace(
                choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="Untersuche X"), finish_reason=None)]
            )

    monkeypatch.setattr(goal_updater, "get_client", lambda *a, **k: Dummy())
    res = goal_updater.update_goal("frage", "Alt", "", [])
    assert res == "Untersuche X"


def test_explicit_command(monkeypatch):
    monkeypatch.setattr(goal_updater, "get_client", lambda *a, **k: None)
    res = goal_updater.update_goal("Beschäftige dich mit Z", "Alt", "", [])
    assert res == "Z"


def test_proposed_goal_via_llm(monkeypatch):
    monkeypatch.setattr(goal_updater, "_extract_explicit_goal", lambda t: None)
    monkeypatch.setattr(goal_updater, "propose_goal", lambda t, **kw: "Neu")
    monkeypatch.setattr(goal_updater, "check_goal_shift", lambda a, b: True)
    monkeypatch.setattr(goal_updater, "get_client", lambda *a, **k: None)
    res = goal_updater.update_goal("hi", "Alt", "", [])
    assert res == "Neu"


def test_config_prompt():
    from cfg import config
    assert goal_updater._SYSTEM_PROMPT is config.PROMPTS['goal_updater_system']

