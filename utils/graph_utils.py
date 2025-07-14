from __future__ import annotations

from datetime import datetime
from difflib import SequenceMatcher
from typing import List, Tuple

from parsing.triplet_pipeline import extract_triplets, add_triplets_to_graph
from memory.memory_manager import get_memory_manager


def _merge_label(label: str, existing_nodes: list[str]) -> str:
    """Return existing node with high similarity or ``label``."""
    for node in existing_nodes:
        if SequenceMatcher(None, label.lower(), node.lower()).ratio() > 0.85:
            return node
    return label


def process_triples(text: str, source: str = "reflection") -> List[Tuple[str, str, str]]:
    """Extract triples from ``text`` and integrate them into the :class:`MetaboGraph`."""
    triples = extract_triplets(text, source=source)
    if not triples:
        return []

    mem = get_memory_manager()
    existing = list(mem.metabo_graph.graph.nodes())

    merged: List[Tuple[str, str, str]] = []
    prepared = []
    for t in triples:
        s = _merge_label(t["subject"], existing)
        o = _merge_label(t["object"], existing)
        merged.append((s, t["predicate"], o))
        prepared.append(
            {
                "subject": s,
                "predicate": t["predicate"],
                "object": o,
                "source": source,
                "timestamp": t.get("timestamp") or datetime.utcnow().isoformat(timespec="seconds"),
            }
        )
        existing.extend([s, o])

    add_triplets_to_graph(prepared, mg=mem.metabo_graph)
    mem.metabo_graph.save()
    return merged
