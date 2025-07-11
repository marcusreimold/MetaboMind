import types
import pytest
from goals import subgoal_planner


def test_missing_openai(monkeypatch):
    monkeypatch.setattr(subgoal_planner, "get_client", lambda *a, **k: None)
    with pytest.raises(EnvironmentError):
        subgoal_planner.decompose_goal("Goal")


def test_missing_api_key(monkeypatch):
    monkeypatch.setattr(subgoal_planner, "get_client", lambda *a, **k: None)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(EnvironmentError):
        subgoal_planner.decompose_goal("Goal")


def test_json_reply(monkeypatch):
    class Dummy:
        def __init__(self):
            self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=self.create))

        def create(self, *a, **k):
            return types.SimpleNamespace(
                choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="[\"a\", \"b\"]"))]
            )

    monkeypatch.setattr(subgoal_planner, "get_client", lambda *a, **k: Dummy())
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    res = subgoal_planner.decompose_goal("Goal")
    assert res == ["a", "b"]


def test_line_reply(monkeypatch):
    class Dummy:
        def __init__(self):
            self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=self.create))

        def create(self, *a, **k):
            text = "- eins\n- zwei\n- drei"
            return types.SimpleNamespace(
                choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=text))]
            )

    monkeypatch.setattr(subgoal_planner, "get_client", lambda *a, **k: Dummy())
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    res = subgoal_planner.decompose_goal("Goal")
    assert res == ["eins", "zwei", "drei"]


def test_fallback(monkeypatch):
    dummy = types.SimpleNamespace(
        chat=types.SimpleNamespace(
            completions=types.SimpleNamespace(create=lambda **k: types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=""))]))
        )
    )
    monkeypatch.setattr(subgoal_planner, "get_client", lambda *a, **k: dummy)
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    res = subgoal_planner.decompose_goal("Goal")
    assert res == ["Goal"]


def test_config_defaults():
    import inspect
    from cfg import config

    sig = inspect.signature(subgoal_planner.decompose_goal)
    assert sig.parameters['model'].default == config.MODELS['subgoal']

