import spacy
import networkx as nx
from typing import Any
import torch
from torch_geometric.data import Data

class NLPParser:
    def __init__(self, language_model: str = "de_core_news_md"):
        self.nlp = spacy.load(language_model)
        self.doc = None
        self.graph = nx.MultiDiGraph()
        self.gnn_graph = Data()


    def parse_text(self, text: str):
        """Erzeugt eine spaCy-Repräsentation"""
        self.doc = self.nlp(text)

        self.convert_to_graph(self.doc)
        self.convert_to_gnn_graph(self.doc)

    
    def convert_to_graph(self, doc):
        """Wandelt spaCy-Dokument in NetworkX-Graph um"""
        for token in doc:
            # Token wird als Knoten hinzugefügt
            self.graph.add_node(token.i, 
                text=token.text,
                lemma=token.lemma_,
                pos=token.pos_,
                tag=token.tag_,
                dep=token.dep_,
                morph=token.morph.to_dict(),
                index=token.i
            )

            # Kante vom Head zum Token
            if token.i != token.head.i:  # kein Self-loop
                self.graph.add_edge(token.head.i, token.i, label=token.dep_)

    
    def convert_to_gnn_graph(self, doc):
        """Wandelt spaCy-Dokument in GNN-kompatiblen PyG-Graph um"""
        nodes = []
        edges = []
        edge_attrs = []

        # Vokabulare für Encoding (für Demonstration – später per Embedding lernen)
        pos_vocab = {}
        dep_vocab = {}

        def encode(vocab: dict, key: str) -> int:
            if key not in vocab:
                vocab[key] = len(vocab)
            return vocab[key]

        # Feature-Vektor pro Token (hier nur POS + DEP als Integer-Encoding)
        for token in doc:
            pos_id = encode(pos_vocab, token.pos_)
            dep_id = encode(dep_vocab, token.dep_)
            nodes.append([pos_id, dep_id])

            if token.i != token.head.i:
                edges.append([token.head.i, token.i])
                edge_attrs.append([encode(dep_vocab, token.dep_)])

        x = torch.tensor(nodes, dtype=torch.long)
        edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
        edge_attr = torch.tensor(edge_attrs, dtype=torch.long)

        self.gnn_graph = Data(x=x, edge_index=edge_index, edge_attr=edge_attr)
