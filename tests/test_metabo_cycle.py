import os
import sys
import types
import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from control import metabo_engine as metabo_cycle


def setup(monkeypatch, tmp_path, goal=""):
    class DummyGraph:
        def __init__(self):
            self.goal_graph = nx.DiGraph()
        def snapshot(self):
            return nx.MultiDiGraph()
        def add_triplets(self, t):
            pass
        def add_goal_transition(self, a, b):
            self.goal_graph.add_edge(a, b)
        def _save_goal_graph(self):
            pass
        def get_goal_path(self):
            return list(self.goal_graph.nodes())

    class DummyMem:
        def __init__(self):
            self.metabo_graph = DummyGraph()
            self.graph = self.metabo_graph
            self.ent = 0.0

        def load_last_entropy(self):
            return self.ent

        def store_last_entropy(self, val):
            self.ent = val

        def add_metabo_insight_to_graph(self, **kwargs):
            pass

    mem = DummyMem()
    monkeypatch.setattr(metabo_cycle, "get_memory_manager", lambda: mem)
    monkeypatch.setattr(metabo_cycle, "MetaboLogger", lambda *a, **k: types.SimpleNamespace(log_cycle=lambda **kw: None))
    monkeypatch.setattr(metabo_cycle, "decompose_goal", lambda g, r: [g])
    monkeypatch.setattr(metabo_cycle, "execute_first_subgoal", lambda g, s: g)
    monkeypatch.setattr(metabo_cycle, "load_context", lambda g, goal: [])
    monkeypatch.setattr(metabo_cycle, "recall_context", lambda scope="goal", limit=5: [])
    monkeypatch.setattr(metabo_cycle, "generate_reflection", lambda **k: {"reflection": ""})
    monkeypatch.setattr(metabo_cycle, "process_triples", lambda text, source="user_input": [])

    path = tmp_path / "goal.txt"
    refl = tmp_path / "ref.txt"
    class DummyGM(metabo_cycle.GoalManager):
        def __init__(self):
            super().__init__(path=str(path), reflection_path=str(refl))
    monkeypatch.setattr(metabo_cycle, "GoalManager", DummyGM)
    if goal:
        DummyGM().set_goal(goal)


def test_goal_switch(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path, goal="Alt")
    monkeypatch.setattr(metabo_cycle, "propose_goal", lambda ui, **kw: "Neu")
    monkeypatch.setattr(metabo_cycle, "check_goal_shift", lambda a, b: True)
    res = metabo_cycle.run_metabo_cycle("User input", source_type="user")
    assert res["goal"] == "Neu"


def test_llm_mode_override(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    monkeypatch.setattr(metabo_cycle, "decide_yin_yang_mode", lambda *a, **k: {"mode": "yin", "rationale": "test"})
    monkeypatch.setattr(metabo_cycle, "decide_mode", lambda *a, **k: "yang")
    res = metabo_cycle.run_metabo_cycle("Hallo", source_type="user")
    assert res["mode"] == "yin"

