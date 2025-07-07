
import os
import networkx as nx
from typing import List, Tuple

class IntentionGraph:
    """Graph storing intention triples with persistent GML saving."""

    def __init__(self, filepath: str = "memory/graph.gml"):
        """Load existing graph from ``filepath`` or create a new one."""
        self.filepath = filepath
        self.load_graph()

    def load_graph(self):
        """Load the graph from ``self.filepath`` if it exists."""
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

    def save_graph(self):
        """Write the current graph to ``self.filepath`` in GML format."""
        try:
            nx.write_gml(self.graph, self.filepath)
            print(f"[Graph] gespeichert nach {self.filepath}")
        except Exception as exc:
            print(f"[Graph] Fehler beim Speichern: {exc}")


    def add_triplets(self, triplets: List[Tuple[str, str, str]]):
        """Add a list of (subject, relation, object) triples to the graph."""
        for subj, rel, obj in triplets:
            self.graph.add_node(subj)
            self.graph.add_node(obj)
            self.graph.add_edge(subj, obj, relation=rel)

    def snapshot(self) -> nx.MultiDiGraph:
        """Return a copy of the current graph."""
        return self.graph.copy()
