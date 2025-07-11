import os
import os
import sys
import types
import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from control import metabo_cycle


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

    mem = types.SimpleNamespace(graph=DummyGraph())
    monkeypatch.setattr(metabo_cycle, "get_memory_manager", lambda: mem)
    monkeypatch.setattr(metabo_cycle, "MetaboLogger", lambda *a, **k: types.SimpleNamespace(log_cycle=lambda **kw: None))
    monkeypatch.setattr(metabo_cycle, "decompose_goal", lambda g, r: [g])
    monkeypatch.setattr(metabo_cycle, "execute_first_subgoal", lambda g, s: g)
    monkeypatch.setattr(metabo_cycle, "load_context", lambda g, goal: [])
    monkeypatch.setattr(metabo_cycle, "recall_context", lambda scope="goal", limit=5: [])
    monkeypatch.setattr(metabo_cycle, "generate_reflection", lambda **k: {"reflection": ""})
    monkeypatch.setattr(metabo_cycle, "extract_triplets_via_llm", lambda text: [])

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
    monkeypatch.setattr(metabo_cycle, "propose_goal", lambda ui: "Neu")
    monkeypatch.setattr(metabo_cycle, "check_goal_shift", lambda a, b: True)
    res = metabo_cycle.run_metabo_cycle("User input")
    assert res["goal"] == "Neu"

