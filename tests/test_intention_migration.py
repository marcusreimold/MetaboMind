import networkx as nx
from memory.memory_manager import MemoryManager


def test_intention_graph_migration(tmp_path):
    intent_path = tmp_path / "intent_graph.gml"
    G = nx.MultiDiGraph()
    G.add_node("eingabe:hi")
    G.add_node("intent1", mode="yang")
    G.add_node("ziel:Musik")
    G.add_edge("eingabe:hi", "intent1", relation="fuehrt_zu")
    G.add_edge("intent1", "ziel:Musik", relation="zielt_auf")
    nx.write_gml(G, intent_path)

    mem = MemoryManager(
        graph_path=str(tmp_path / "graph.gml"),
        emotion_log=str(tmp_path / "emo.jsonl"),
        reflection_path=str(tmp_path / "ref.txt"),
        entropy_path=str(tmp_path / "ent.txt"),
        meta_path=str(tmp_path / "meta.gml"),
        intent_graph_path=str(intent_path),
    )

    mg = nx.read_gml(mem.metabo_graph.filepath)

    assert "intent1" in mg.nodes
    data = mg.nodes["intent1"]
    assert data.get("typ") == "intention"
    assert data.get("source") == "llm"
    assert data.get("mode") == "yang"

    assert mg.has_edge("eingabe:hi", "intent1")
    assert mg.has_edge("intent1", "ziel:Musik")

    # original file archived
    assert not intent_path.exists()
    assert intent_path.with_suffix(intent_path.suffix + ".bak").exists()
