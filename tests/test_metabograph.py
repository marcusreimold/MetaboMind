import networkx as nx
from memory.metabo_graph import MetaboGraph, extract_subgraph_by_type


def test_merge_and_extract(tmp_path):
    g1 = nx.MultiDiGraph()
    g1.add_edge("Musik", "Freude", relation="erzeugt")
    g2 = nx.MultiDiGraph()
    g2.add_edge("Musik", "Ziel", relation="fuehrt_zu")

    mg = MetaboGraph(filepath=str(tmp_path / "m.gml"))
    mg.add_graph(g1, default_typ="konzept", source="user")
    mg.add_graph(g2, default_typ="intention", source="system")

    assert "konzept" in mg.graph.nodes["Musik"]["typ"]
    assert "intention" in mg.graph.nodes["Ziel"]["typ"]

    sub = extract_subgraph_by_type(mg.graph, "intention")
    assert set(sub.nodes()) == {"Musik", "Ziel"}

    ent = mg.calculate_entropy()
    assert 0.0 <= ent <= 1.0

    assert mg.filepath.exists()
