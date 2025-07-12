import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from control import yin_yang_controller as yyc


def test_yin_decision_with_uncertainty():
    orch = yyc.YinYangOrchestrator()
    orch._history = ["yin", "yin", "yin"]
    mode = orch.decide_mode({"entropy_delta": 0.2}, "Ich weiß nicht, was vorher war", 0)
    assert mode == "yin"


def test_yin_due_to_negative_emotion():
    orch = yyc.YinYangOrchestrator()
    mode = orch.decide_mode(
        {"entropy_delta": 0.001, "emotion": "negative"}, "Ich bin durcheinander", 3
    )
    assert mode == "yin"


def test_yin_due_to_small_delta():
    orch = yyc.YinYangOrchestrator()
    mode = orch.decide_mode(
        {"entropy_delta": 0.0, "emotion": "unsicher"}, "Ich bin durcheinander", 3
    )
    assert mode == "yin"


def test_yin_due_to_confusion_phrase():
    orch = yyc.YinYangOrchestrator()
    orch._history = ["yin", "yin", "yin"]
    mode = orch.decide_mode({"entropy_delta": 0.5}, "Ich verstehe nicht", 3)
    assert mode == "yin"
