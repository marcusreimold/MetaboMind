import os
import sys
import json
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from reflection import reflection_engine


def test_detect_goal_shift_context(monkeypatch):
    messages_store = {}

    class DummyClient:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(create=self.create)
            )

        def create(self, *args, **kwargs):
            messages_store['messages'] = kwargs.get('messages')
            return types.SimpleNamespace(
                choices=[types.SimpleNamespace(
                    finish_reason="function_call",
                    message=types.SimpleNamespace(
                        function_call=types.SimpleNamespace(
                            name="goal_decision",
                            arguments=json.dumps({"change_goal": True, "new_goal": "Musik"})
                        )
                    )
                )]
            )

    monkeypatch.setattr(reflection_engine, "get_client", lambda *a, **k: DummyClient())

    change, goal = reflection_engine.detect_goal_shift(
        "lass uns über Musik reden",
        "Sport",
        previous_user_inputs=["Hallo", "Das interessiert mich nicht"],
        last_system_output="Ok"
    )

    assert change is True
    assert goal == "Musik"
    joined = "\n".join(m['content'] for m in messages_store['messages'])
    assert "Das interessiert mich nicht" in joined
    assert "Ok" in joined
