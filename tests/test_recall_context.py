import networkx as nx
import types
from memory import recall_context


def test_recall_context_global(monkeypatch):
    G = nx.MultiDiGraph()
    G.add_edge("A", "B", relation="ab")
    G.add_edge("B", "C", relation="bc")

    class DummyMem:
        def __init__(self):
            self.graph = types.SimpleNamespace(graph=G)

    monkeypatch.setattr(recall_context, "get_memory_manager", lambda: DummyMem())
    res = recall_context.recall_context(limit=2)
    assert {
        (d["subject"], d["predicate"], d["object"]) for d in res
    } == {
        ("A", "ab", "B"),
        ("B", "bc", "C"),
    }


def test_recall_context_goal(monkeypatch):
    G = nx.MultiDiGraph()
    G.add_edge("goal", "X", relation="r1")
    G.add_edge("Y", "goal", relation="r2")

    class DummyMem:
        def __init__(self):
            self.graph = types.SimpleNamespace(graph=G)

    monkeypatch.setattr(recall_context, "get_memory_manager", lambda: DummyMem())
    monkeypatch.setattr(recall_context, "get_active_goal", lambda: "goal")
    res = recall_context.recall_context(scope="goal")
    assert {tuple(d.values())[:3] for d in res} == {
        ("goal", "r1", "X"),
        ("Y", "r2", "goal"),
    }
