import os
import json
import sys
import types
import yaml
import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from control import metabo_engine as metabo_cycle
from goals import goal_manager, goal_updater
from memory import memory_manager
from utils import llm_client


# ---------------------------------------------------------------------------
# Helper patch setup

def setup_env(monkeypatch, tmp_path):
    # disable real OpenAI access
    monkeypatch.setattr(llm_client, "get_client", lambda *a, **k: None)

    mgr = memory_manager.MemoryManager(
        graph_path=str(tmp_path / "graph.gml"),
        emotion_log=str(tmp_path / "emo.jsonl"),
        reflection_path=str(tmp_path / "last_reflection.txt"),
        entropy_path=str(tmp_path / "last_entropy.txt"),
        meta_path=str(tmp_path / "metabograph.gml"),
    )
    memory_manager._default_manager = mgr
    monkeypatch.setattr(memory_manager, "get_memory_manager", lambda: mgr)
    monkeypatch.setattr(metabo_cycle, "get_memory_manager", lambda: mgr)

    class DummyGM(goal_manager.GoalManager):
        def __init__(self):
            super().__init__(
                path=str(tmp_path / "goal.txt"),
                reflection_path=str(tmp_path / "ref.txt"),
            )

    monkeypatch.setattr(metabo_cycle, "GoalManager", DummyGM)
    return mgr


# ---------------------------------------------------------------------------
# Dummy LLM behaviour

def dummy_propose_goal(user_input, api_key=None):
    if "klassischer Musik" in user_input:
        return "klassische Musik"
    return None


def dummy_check_goal_shift(a, b, api_key=None):
    return bool(b)


def dummy_generate_reflection(last_user_input, goal, last_reflection, triplets=None, **kwargs):
    if "erinnerst" in last_user_input:
        text = "Ich erinnere mich an fr\u00fchere Inhalte."
    elif "verwirrt" in last_user_input:
        text = "Ich sehe, dass du verwirrt bist."
    else:
        text = last_user_input
    return {"reflection": text, "explanation": "", "triplets": []}


def dummy_extract_triplets(text, model=None):
    if "K\u00fcnstliche Intelligenz" in text:
        return [("K\u00fcnstliche Intelligenz", "ver\u00e4ndert", "Arbeitswelt")]
    return []


# ---------------------------------------------------------------------------

def has_node(G, typ, label=None, text_contains=None):
    for n, data in G.nodes(data=True):
        if typ in str(data.get("typ", "")).split(","):
            if label and not n.endswith(label):
                continue
            if text_contains and text_contains not in str(data.get("text", "")):
                continue
            return True
    return False


def _norm(text: str | None) -> str:
    return (text or "").replace("\u00fc", "ue")


def has_edge(G, relation=None, source=None, target=None, source_contains=None, target_contains=None):
    for u, v, data in G.edges(data=True):
        if relation and _norm(relation) not in _norm(str(data.get("relation", ""))):
            continue
        if source and u != source:
            continue
        if target and v != target:
            continue
        if source_contains and source_contains not in u:
            continue
        if target_contains and target_contains not in v:
            continue
        return True
    return False


def read_meta(node_data):
    meta = node_data.get("meta")
    if not meta:
        return {}
    try:
        return json.loads(meta)
    except Exception:
        return {}


# ---------------------------------------------------------------------------


def test_graph_integration(monkeypatch, tmp_path):
    mgr = setup_env(monkeypatch, tmp_path)

    # patch LLM-dependent functions
    monkeypatch.setattr(goal_updater, "propose_goal", dummy_propose_goal)
    monkeypatch.setattr(goal_updater, "check_goal_shift", dummy_check_goal_shift)
    monkeypatch.setattr(metabo_cycle, "propose_goal", dummy_propose_goal)
    monkeypatch.setattr(metabo_cycle, "check_goal_shift", dummy_check_goal_shift)
    monkeypatch.setattr(metabo_cycle, "decompose_goal", lambda g, r: [g])
    monkeypatch.setattr(metabo_cycle, "execute_first_subgoal", lambda g, s: g)
    monkeypatch.setattr(metabo_cycle, "load_context", lambda g, goal: [])
    monkeypatch.setattr(metabo_cycle, "recall_context", lambda *a, **k: [])
    monkeypatch.setattr(metabo_cycle, "generate_reflection", dummy_generate_reflection)
    monkeypatch.setattr(metabo_cycle, "extract_triplets_via_llm", dummy_extract_triplets)
    monkeypatch.setattr(metabo_cycle, "decide_mode", lambda *a, **k: "yang")
    monkeypatch.setattr(metabo_cycle, "decide_yin_yang_mode", lambda *a, **k: {})

    with open(os.path.join("tests", "llm", "test_graph_integration.yaml"), "r", encoding="utf-8") as fh:
        cases = yaml.safe_load(fh) or []

    for case in cases:
        metabo_cycle.run_metabo_cycle(case["input"], source_type="user")
        G = nx.read_gml(mgr.metabo_graph.filepath)

        for subj, rel, obj in case.get("expected_graph_triples", []):
            assert has_edge(G, relation=rel, source=subj, target=obj)

        for item in case.get("expected_graph_contains", []):
            typ = item.get("type")
            if typ == "relation":
                assert has_edge(
                    G,
                    relation=item.get("relation"),
                    source=item.get("source"),
                    target=item.get("target"),
                    source_contains=item.get("source_contains"),
                    target_contains=item.get("target_contains"),
                )
            else:
                assert has_node(
                    G,
                    typ,
                    label=item.get("label"),
                    text_contains=item.get("text_contains"),
                )

        for meta in case.get("expected_graph_metadata", []):
            found = False
            for _, data in G.nodes(data=True):
                m = read_meta(data)
                if meta["key"] in m:
                    val = m[meta["key"]]
                    if "value" in meta and val != meta["value"]:
                        continue
                    if "value_in" in meta and val not in meta["value_in"]:
                        continue
                    if meta.get("value_type") == "float" and not isinstance(val, float):
                        continue
                    found = True
                    break
            assert found
