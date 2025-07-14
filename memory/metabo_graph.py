from __future__ import annotations

import os
from math import log2
from pathlib import Path
from typing import Iterable, Tuple

import networkx as nx


class MetaboGraph:
    """Unified network merging multiple knowledge sources."""

    def __init__(self, filepath: str = "data/metabograph.gml") -> None:
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    # ------------------------------------------------------------------
    def _load(self) -> None:
        """Load existing graph from disk if possible."""
        if self.filepath.exists():
            try:
                g = nx.read_gml(self.filepath)
                if not isinstance(g, nx.MultiDiGraph):
                    g = nx.MultiDiGraph(g)
                self.graph = g
                print(f"[MetaboGraph] Lade bestehenden Graph aus {self.filepath}")
                return
            except Exception:
                pass
        self.graph = nx.MultiDiGraph()

    def save(self) -> None:
        """Persist graph to ``filepath``."""
        try:
            nx.write_gml(self.graph, self.filepath)
            print(f"[MetaboGraph] gespeichert nach {self.filepath}")
        except Exception:
            pass

    # ------------------------------------------------------------------
    def _merge_node(self, node: str, typ: str | None, source: str | None) -> None:
        """Create or update ``node`` with given type and source."""
        attrs = self.graph.nodes.get(node, {})
        if typ:
            existing = attrs.get("typ")
            if existing and typ not in str(existing).split(","):
                attrs["typ"] = f"{existing},{typ}"
            elif not existing:
                attrs["typ"] = typ
        if source:
            existing = attrs.get("source")
            if existing and source not in str(existing).split(","):
                attrs["source"] = f"{existing},{source}"
            elif not existing:
                attrs["source"] = source
        self.graph.add_node(node, **attrs)

    def add_triplets(
        self,
        triplets: Iterable[Tuple[str, str, str]],
        node_typ: str = "konzept",
        edge_typ: str = "relation",
        source: str | None = None,
    ) -> None:
        """Insert ``triplets`` with node type and source information."""
        for subj, rel, obj in triplets:
            self._merge_node(subj, node_typ, source)
            self._merge_node(obj, node_typ, source)
            self.graph.add_edge(subj, obj, relation=rel, typ=edge_typ)
        self.save()

    def add_graph(
        self,
        other: nx.Graph,
        default_typ: str | None = None,
        source: str | None = None,
    ) -> None:
        """Merge another graph into this one."""
        for node, data in other.nodes(data=True):
            typ = data.get("typ", default_typ)
            self._merge_node(node, typ, data.get("source", source))
        for u, v, data in other.edges(data=True):
            self.graph.add_edge(u, v, **data)
        self.save()

    def import_intention_graph(self, path: str | Path) -> None:
        """Migrate nodes and edges from an existing intention graph."""
        p = Path(path)
        if not p.exists():
            return

        try:
            g = nx.read_gml(p)
            if not isinstance(g, nx.MultiDiGraph):
                g = nx.MultiDiGraph(g)
        except Exception:
            return

        for node, data in g.nodes(data=True):
            self._merge_node(node, "intention", "llm")
            mode = data.get("mode")
            if mode:
                self.graph.nodes[node]["mode"] = mode

        for u, v, data in g.edges(data=True):
            rel = data.get("relation")
            exists = False
            edata = self.graph.get_edge_data(u, v) or {}
            for d in edata.values() if isinstance(edata, dict) else [edata]:
                if rel is None or d.get("relation") == rel:
                    exists = True
                    break
            if not exists:
                attrs = dict(data)
                attrs.setdefault("relation", rel or "")
                attrs.setdefault("typ", "relation")
                self.graph.add_edge(u, v, **attrs)

        self.save()
        backup = p.with_suffix(p.suffix + ".bak")
        try:
            p.rename(backup)
        except Exception:
            pass

    # ------------------------------------------------------------------
    def snapshot(self) -> nx.MultiDiGraph:
        """Return a copy of the underlying graph."""
        return self.graph.copy()

    def calculate_entropy(self) -> float:
        """Return Shannon entropy over edge relations."""
        total = self.graph.number_of_edges()
        if total == 0:
            return 0.0
        counts = {}
        for _, _, data in self.graph.edges(data=True):
            rel = data.get("relation", "")
            counts[rel] = counts.get(rel, 0) + 1
        entropy = -sum((c / total) * log2(c / total) for c in counts.values())
        max_ent = log2(len(counts)) if counts else 1.0
        return entropy / max_ent if max_ent else 0.0


def extract_subgraph_by_type(G: nx.Graph, typ: str) -> nx.Graph:
    """Return subgraph containing only nodes of ``typ``."""
    nodes = [n for n, d in G.nodes(data=True) if typ in str(d.get("typ", "")).split(",")]
    return G.subgraph(nodes).copy()
