from graph.nlp_parser import NLPParser

import matplotlib.pyplot as plt
import networkx as nx

from torch_geometric.utils import to_networkx
from torch_geometric.data import Data

from graph.graph_utils import draw_parse_graph, draw_gnn_graph

 
if __name__ == "__main__":
    parser = NLPParser()
    text = "Der Mann, der gestern im Park spazieren ging, wurde von einem Hund gebissen."
    parser.parse_text(text)

    draw_parse_graph(parser.graph, title="Parse-Graph für den Text")  # Visualisierung des Parse-Graphs
    draw_gnn_graph(parser.gnn_graph, parser.doc, title="GNN-Graph für den Text")  # Visualisierung des GNN-Graphs
