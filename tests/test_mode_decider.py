import json
import types
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from control import mode_decider


def test_no_client(monkeypatch):
    monkeypatch.setattr(mode_decider, "get_client", lambda *a, **k: None)
    assert mode_decider.decide_yin_yang_mode("hi", {"entropy_delta": 0}) is None


def test_basic_call(monkeypatch):
    class Dummy:
        def __init__(self):
            self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=self.create))
        def create(self, *a, **k):
            return types.SimpleNamespace(choices=[types.SimpleNamespace(
                finish_reason="function_call",
                message=types.SimpleNamespace(function_call=types.SimpleNamespace(
                    name="decide_yin_yang_mode",
                    arguments=json.dumps({"mode": "yang", "rationale": "ok"})
                ))
            )])
    monkeypatch.setattr(mode_decider, "get_client", lambda *a, **k: Dummy())
    res = mode_decider.decide_yin_yang_mode("hi", {"entropy_delta": 0})
    assert res["mode"] == "yang"
