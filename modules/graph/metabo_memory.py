import networkx as nx
from torch_geometric.data import Data
from graph.nlp_parser import NLPParser
from graph.graph_entropy_analyzer import overall_graph_entropy
from graph.gnn_graph_entropy_analyzer import overall_gnn_entropy

class MetaboMemory:
    def __init__(self):
        self.syntax_graph = nx.MultiDiGraph()
        self.gnn_graphs = []
        self.texts = []
        self.parser = NLPParser()

    def add_text(self, text: str):
        self.texts.append(text)

        # Parse zu syntaktischem Netzwerkgraph
        self.parser.parse_text(text)
        offset = len(self.syntax_graph.nodes)
        self._merge_graph(self.syntax_graph, self.parser.graph, offset=offset)

        # PyG-Graph separat für spätere Verarbeitung
        self.gnn_graphs.append(self.parser.gnn_graph)

    def get_graph_entropy(self) -> dict:
        return overall_graph_entropy(self.syntax_graph)

    def get_gnn_entropy(self) -> dict:
        if not self.gnn_graphs:
            return {}
        combined = self._combine_gnn_graphs()
        return overall_gnn_entropy(combined)

    def _merge_graph(self, target: nx.MultiDiGraph, source: nx.MultiDiGraph, offset: int = 0):
        for n, data in source.nodes(data=True):
            target.add_node(n + offset, **data)
        for u, v, data in source.edges(data=True):
            target.add_edge(u + offset, v + offset, **data)

    def _combine_gnn_graphs(self) -> Data:
        """Kombiniert alle GNN-Graphen in einen großen PyG.Data-Graph"""
        from torch_geometric.data import Batch
        return Batch.from_data_list(self.gnn_graphs)
