from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Tuple

from parsing.triplet_parser_llm import extract_triplets_via_llm
from memory.metabo_graph import MetaboGraph


def _validate(triple: Tuple[str, str, str]) -> bool:
    return all(isinstance(p, str) and p.strip() for p in triple)


def extract_triplets(text: str, source: str) -> List[Dict]:
    """Extract triplets via LLM and attach metadata."""
    raw = extract_triplets_via_llm(text)
    seen = set()
    cleaned: List[Tuple[str, str, str]] = []
    for t in raw:
        if not _validate(t):
            continue
        if t not in seen:
            seen.add(t)
            cleaned.append(t)
    timestamp = datetime.utcnow().isoformat(timespec="seconds")
    return [
        {
            "subject": s.strip(),
            "predicate": r.strip(),
            "object": o.strip(),
            "source": source,
            "timestamp": timestamp,
        }
        for s, r, o in cleaned
    ]


def add_triplets_to_graph(
    triplets: List[Dict],
    graph_path: str | None = None,
    mg: MetaboGraph | None = None,
) -> None:
    """Persist ``triplets`` to the global MetaboGraph."""
    mg = mg or MetaboGraph(graph_path or "data/metabograph.gml")
    for t in triplets:
        triple = [(t["subject"], t["predicate"], t["object"])]
        mg.add_triplets(
            triple,
            node_typ="konzept",
            edge_typ="relation",
            source=t.get("source"),
            edge_attrs={"source": t.get("source"), "timestamp": t.get("timestamp")},
        )
    mg.save()
