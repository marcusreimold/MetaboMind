from __future__ import annotations

from difflib import SequenceMatcher
from typing import List, Tuple

from parsing.triplet_parser_llm import extract_triplets_via_llm
from memory.memory_manager import get_memory_manager


def _find_similar_node(name: str, nodes: list[str], threshold: float = 0.8) -> str:
    """Return an existing node name with high similarity to ``name`` if found."""
    best = name
    best_score = threshold
    for node in nodes:
        score = SequenceMatcher(None, node.lower(), name.lower()).ratio()
        if score >= best_score:
            best = node
            best_score = score
    return best


def process_triples(text: str, source: str = "reflection") -> dict:
    """Extract triples from ``text`` and integrate them into the metabograph."""
    triples = extract_triplets_via_llm(text)
    memory = get_memory_manager()
    graph = memory.graph
    existing = list(graph.graph.nodes)
    processed: List[Tuple[str, str, str]] = []
    for subj, rel, obj in triples:
        s = _find_similar_node(subj, existing)
        o = _find_similar_node(obj, existing)
        processed.append((s, rel, o))
        existing.extend([s, o])
    before, after = memory.store_triplets(processed)
    graph.save_graph()
    return {"triplets": processed, "entropy_before": before, "entropy_after": after}

