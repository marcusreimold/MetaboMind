import types
import pytest
import subgoal_planner


def test_missing_openai(monkeypatch):
    monkeypatch.setattr(subgoal_planner, "openai", None)
    with pytest.raises(ImportError):
        subgoal_planner.decompose_goal("Goal")


def test_missing_api_key(monkeypatch):
    dummy = types.SimpleNamespace(ChatCompletion=types.SimpleNamespace(create=lambda **k: None))
    monkeypatch.setattr(subgoal_planner, "openai", dummy)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(EnvironmentError):
        subgoal_planner.decompose_goal("Goal")


def test_json_reply(monkeypatch):
    dummy = types.SimpleNamespace()
    def create(model, temperature, messages):
        return {"choices": [{"message": {"content": "[\"a\", \"b\"]"}}]}
    dummy.ChatCompletion = types.SimpleNamespace(create=create)
    monkeypatch.setattr(subgoal_planner, "openai", dummy)
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    res = subgoal_planner.decompose_goal("Goal")
    assert res == ["a", "b"]


def test_line_reply(monkeypatch):
    dummy = types.SimpleNamespace()
    def create(model, temperature, messages):
        text = "- eins\n- zwei\n- drei"
        return {"choices": [{"message": {"content": text}}]}
    dummy.ChatCompletion = types.SimpleNamespace(create=create)
    monkeypatch.setattr(subgoal_planner, "openai", dummy)
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    res = subgoal_planner.decompose_goal("Goal")
    assert res == ["eins", "zwei", "drei"]


def test_fallback(monkeypatch):
    dummy = types.SimpleNamespace(ChatCompletion=types.SimpleNamespace(create=lambda **k: {"choices": [{"message": {"content": ""}}]}))
    monkeypatch.setattr(subgoal_planner, "openai", dummy)
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    res = subgoal_planner.decompose_goal("Goal")
    assert res == ["Goal"]
