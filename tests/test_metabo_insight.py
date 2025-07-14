import json
from memory.memory_manager import MemoryManager


def test_add_metabo_insight(tmp_path):
    mem = MemoryManager(
        emotion_log=str(tmp_path / "e.jsonl"),
        reflection_path=str(tmp_path / "r.txt"),
        entropy_path=str(tmp_path / "ent.txt"),
        meta_path=str(tmp_path / "m.gml"),
    )
    triplets = [("A", "rel", "B")]
    mem.add_metabo_insight_to_graph(
        user_input="hi",
        triplets=triplets,
        goal="Goal",
        reflection="text",
        emotion={"emotion": "negativ", "delta": 0.1},
    )

    mg = mem.metabo_graph.graph
    assert "eingabe:hi" in mg.nodes
    assert mg.nodes["eingabe:hi"]["typ"] == "eingabe"
    assert "ziel:Goal" in mg.nodes
    assert mg.has_edge("eingabe:hi", "ziel:Goal")

    # one reflection node with metadata
    refl_nodes = [n for n, d in mg.nodes(data=True) if d.get("typ") == "reflexion"]
    assert len(refl_nodes) == 1
    refl = refl_nodes[0]
    assert json.loads(mg.nodes[refl]["meta"])["emotion"] == "negativ"
    # triplet preserved with edge type
    assert mg.has_edge("A", "B")
    data = list(mg.get_edge_data("A", "B").values())[0]
    assert data.get("typ") == "relation"
