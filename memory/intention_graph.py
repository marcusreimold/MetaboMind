from __future__ import annotations

import os
from typing import List, Tuple, Optional

import networkx as nx


class IntentionGraph:
    """Persisted knowledge graph storing triples and goal transitions."""

    def __init__(self, filepath: str = "data/metabograph.gml") -> None:
        self.filepath = filepath
        self.load_graph()

    # ------------------------------------------------------------------
    # Persistence helpers
    def load_graph(self) -> None:
        """Load ``self.filepath`` if available or create a new graph."""
        if os.path.exists(self.filepath):
            try:
                self.graph = nx.read_gml(self.filepath)
                if not isinstance(self.graph, nx.MultiDiGraph):
                    self.graph = nx.MultiDiGraph(self.graph)
                print(f"[Graph] Lade bestehenden Graph aus {self.filepath}")
            except Exception as exc:
                print(f"[Graph] Fehler beim Laden, erstelle neuen Graph: {exc}")
                self.graph = nx.MultiDiGraph()
        else:
            print("[Graph] Erzeuge neuen, leeren Graph")
            self.graph = nx.MultiDiGraph()

    def save_graph(self) -> None:
        """Persist the current graph in GML format."""
        try:
            nx.write_gml(self.graph, self.filepath)
            print(f"[Graph] gespeichert nach {self.filepath}")
        except Exception as exc:
            print(f"[Graph] Fehler beim Speichern: {exc}")

    # ------------------------------------------------------------------
    # Triplet operations
    def add_triplets(self, triplets: List[Tuple[str, str, str]]) -> None:
        """Add ``triplets`` to the knowledge graph."""
        for subj, rel, obj in triplets:
            self.graph.add_node(subj)
            self.graph.add_node(obj)
            self.graph.add_edge(subj, obj, relation=rel)

    def snapshot(self) -> nx.MultiDiGraph:
        """Return a copy of the current graph."""
        return self.graph.copy()

    # ------------------------------------------------------------------
    # Goal handling
    def add_goal_transition(self, previous_goal: Optional[str], new_goal: str) -> None:
        """Record a goal change from ``previous_goal`` to ``new_goal``."""
        self.graph.add_node(new_goal)
        self.graph.nodes[new_goal]["goal"] = True
        if previous_goal:
            self.graph.add_node(previous_goal)
            self.graph.nodes[previous_goal].pop("goal", None)
            if not self.graph.has_edge(previous_goal, new_goal):
                self.graph.add_edge(previous_goal, new_goal, relation="goal_transition")
