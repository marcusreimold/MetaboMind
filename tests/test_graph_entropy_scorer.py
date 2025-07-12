import networkx as nx

from reasoning.graph_entropy_scorer import calculate_entropy, explain_entropy


def test_ordered_graph_entropy():
    g = nx.complete_graph(5)
    score = calculate_entropy(g)
    assert 0 <= score <= 1
    assert score < 0.3


def test_chaotic_graph_entropy():
    g = nx.Graph()
    g.add_nodes_from(range(5))
    g.add_edge(0, 1)
    score = calculate_entropy(g)
    assert score > 0.5
    explanation = explain_entropy(g)
    assert "Knoten" in explanation


def test_multidigraph_entropy():
    g = nx.MultiDiGraph()
    g.add_edge("a", "b")
    score = calculate_entropy(g)
    assert 0 <= score <= 1

