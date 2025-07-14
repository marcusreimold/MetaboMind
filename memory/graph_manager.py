from __future__ import annotations

from typing import Iterable, Tuple, List

from memory.intention_graph import IntentionGraph
from memory.metabo_graph import MetaboGraph


class GraphManager:
    """Wrapper managing both intention and unified ``MetaboGraph``."""

    def __init__(
        self,
        filepath: str = "data/graph.gml",
        meta_path: str = "data/metabograph.gml",
    ) -> None:
        self.intention_graph = IntentionGraph(filepath)
        self.metabo_graph = MetaboGraph(meta_path)

    def snapshot(self):
        return self.metabo_graph.snapshot()

    def _edge_exists(self, subj: str, rel: str, obj: str) -> bool:
        """Return ``True`` if identical edge already exists in the MetaboGraph."""
        for _, _, data in self.metabo_graph.graph.edges(subj, obj, data=True):
            if data.get("relation") == rel:
                return True
        return False

    def add_triplets(
        self,
        triplets: Iterable[Tuple[str, str, str]],
        node_typ: str = "konzept",
        edge_typ: str = "relation",
        source: str | None = None,
    ) -> None:
        """Insert ``triplets`` into both graphs, avoiding duplicates."""
        new_triples: List[Tuple[str, str, str]] = []
        for subj, rel, obj in triplets:
            if not self._edge_exists(subj, rel, obj):
                self.metabo_graph.graph.add_node(subj, typ=node_typ, source=source)
                self.metabo_graph.graph.add_node(obj, typ=node_typ, source=source)
                self.metabo_graph.graph.add_edge(subj, obj, relation=rel, typ=edge_typ)
                new_triples.append((subj, rel, obj))

        if new_triples:
            self.intention_graph.add_triplets(new_triples)

    def save_graph(self) -> None:
        """Persist both underlying graphs."""
        self.intention_graph.save_graph()
        self.metabo_graph.save()

    @property
    def graph(self):
        """Return the underlying MetaboGraph object."""
        return self.metabo_graph.graph


_default_manager: GraphManager | None = None


def get_graph_manager() -> GraphManager:
    """Return a shared :class:`GraphManager` instance."""
    global _default_manager
    if _default_manager is None:
        _default_manager = GraphManager()
    return _default_manager
