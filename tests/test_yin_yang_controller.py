import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from control import yin_yang_controller as yyc


def test_yin_decision_with_uncertainty():
    orch = yyc.YinYangOrchestrator()
    orch._history = ["yin", "yin", "yin"]
    mode = orch.decide_mode({"entropy_delta": 0.2}, "Ich weiß nicht, was vorher war", 0)
    assert mode == "yin"
