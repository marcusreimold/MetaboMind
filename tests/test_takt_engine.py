import os
import sys
import types
import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from control import takt_engine, metabo_engine


class DummyMem:
    def __init__(self):
        self.val = 0.0
        class DummyGraph:
            def __init__(self):
                self.goal_graph = nx.DiGraph()
                self.graph = nx.MultiDiGraph()
            def snapshot(self):
                return nx.MultiDiGraph()
            def add_triplets(self, t):
                pass
            def add_goal_transition(self, a, b):
                pass
            def _save_goal_graph(self):
                pass
            def get_goal_path(self):
                return []

        self.graph = DummyGraph()
        self.metabo_graph = self.graph

    def calculate_entropy(self):
        return 0.4

    def load_last_entropy(self):
        return 0.2

    def store_last_entropy(self, value):
        self.val = value

    def map_entropy_to_emotion(self, delta):
        return {"delta": delta, "emotion": "neutral", "intensity": "low"}

    def store_reflection(self, reflection):
        self.reflection = reflection

    def load_reflection(self):
        return ""

    def add_metabo_insight_to_graph(self, **kwargs):
        pass


def setup(monkeypatch, change_goal=False):
    mem = DummyMem()
    monkeypatch.setattr(metabo_engine, "get_memory_manager", lambda: mem)
    path = os.path.join(os.getcwd(), "goal.txt")
    refl = os.path.join(os.getcwd(), "ref.txt")
    class DummyGM(metabo_engine.GoalManager):
        def __init__(self):
            super().__init__(path=path, reflection_path=refl)
    monkeypatch.setattr(metabo_engine, "GoalManager", DummyGM)
    DummyGM().set_goal("A")
    monkeypatch.setattr(metabo_engine, "propose_goal", lambda ui: None)
    monkeypatch.setattr(metabo_engine, "check_goal_shift", lambda a, b: False)
    monkeypatch.setattr(metabo_engine, "is_new_topic", lambda u, g: False)
    monkeypatch.setattr(metabo_engine, "run_llm_task", lambda *a, **k: "ref")
    return mem


def test_metabotakt_no_change(monkeypatch):
    setup(monkeypatch, change_goal=False)
    res = takt_engine.run_metabotakt(api_key=None)
    assert "goal" in res


def test_metabotakt_goal_change(monkeypatch):
    mem = setup(monkeypatch, change_goal=True)
    res = takt_engine.run_metabotakt(api_key=None)
    assert "goal_update" in res
