import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from control import metabo_engine


class DummyGraph:
    def __init__(self):
        self.goal_graph = types.SimpleNamespace()
    def snapshot(self):
        import networkx as nx
        return nx.MultiDiGraph()
    def add_triplets(self, t):
        pass
    def add_goal_transition(self, a, b):
        pass
    def _save_goal_graph(self):
        pass
    def get_goal_path(self):
        return []

class DummyMem:
    def __init__(self):
        self.val = 0.0
        self.metabo_graph = DummyGraph()
        self.graph = self.metabo_graph

    def load_last_entropy(self):
        return self.val

    def store_last_entropy(self, val):
        self.val = val

    def add_metabo_insight_to_graph(self, **kwargs):
        pass


def setup(monkeypatch):
    mem = DummyMem()
    monkeypatch.setattr(metabo_engine, "get_memory_manager", lambda: mem)
    monkeypatch.setattr(metabo_engine, "MetaboLogger", lambda *a, **k: types.SimpleNamespace(log_cycle=lambda **kw: None))
    monkeypatch.setattr(metabo_engine, "decompose_goal", lambda g, r: [g])
    monkeypatch.setattr(metabo_engine, "execute_first_subgoal", lambda g, s: g)
    monkeypatch.setattr(metabo_engine, "load_context", lambda g, goal: [])
    monkeypatch.setattr(metabo_engine, "recall_context", lambda *a, **k: [])
    monkeypatch.setattr(metabo_engine, "generate_reflection", lambda **k: {"reflection": ""})
    monkeypatch.setattr(metabo_engine, "process_triples", lambda text, source="reflection": [])
    monkeypatch.setattr(metabo_engine, "propose_goal", lambda ui, **kw: None)
    monkeypatch.setattr(metabo_engine, "check_goal_shift", lambda a, b: False)
    path = os.path.join(os.getcwd(), "tmp_goal.txt")
    refl = os.path.join(os.getcwd(), "tmp_ref.txt")
    class DummyGM(metabo_engine.GoalManager):
        def __init__(self):
            super().__init__(path=path, reflection_path=refl)
    monkeypatch.setattr(metabo_engine, "GoalManager", DummyGM)
    return mem


def test_cycle_user(monkeypatch):
    setup(monkeypatch)
    res = metabo_engine.run_metabo_cycle("hi", source_type="user")
    assert res["source_type"] == "user"


def test_cycle_system(monkeypatch):
    setup(monkeypatch)
    res = metabo_engine.run_metabo_cycle("system", source_type="system")
    assert res["source_type"] == "system"
