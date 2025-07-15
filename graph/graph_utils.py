import matplotlib.pyplot as plt
import networkx as nx
from torch_geometric.utils import to_networkx
from torch_geometric.data import Data
import spacy

# -------------------------------
# 1. Visualisiere spaCy-Parse-Graph (MultiDiGraph)
# -------------------------------
def draw_parse_graph(G: nx.MultiDiGraph, title: str = "Parse-Graph"):
    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, arrows=True,
            node_color='lightblue', node_size=1500, font_size=10)

    labels = nx.get_node_attributes(G, 'text')
    nx.draw_networkx_labels(G, pos, labels, font_size=12)

    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.title(title)
    plt.axis('off')
    plt.show()

# -------------------------------
# 2. Visualisiere PyG-Graph (Data-Objekt) mit Textlabels
# -------------------------------
def draw_gnn_graph(data: Data, doc: spacy.tokens.Doc, title: str = "GNN-Graph (PyG)"):
    G = to_networkx(data, to_undirected=False)

    # Token-Text aus spaCy als Label holen
    labels = {i: token.text for i, token in enumerate(doc)}

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, arrows=True,
            node_color='lightgreen', node_size=1000, font_size=10)

    nx.draw_networkx_labels(G, pos, labels=labels, font_size=12)

    plt.title(title)
    plt.axis('off')
    plt.show()
