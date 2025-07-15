from graph.nlp_parser import NLPParser
from graph.graph_utils import draw_parse_graph, draw_gnn_graph
from graph.graph_entropy_analyzer import overall_graph_entropy
from graph.gnn_graph_entropy_analyzer import overall_gnn_entropy

 
if __name__ == "__main__":
    parser = NLPParser()
    #text = "Der Mann, der gestern im Park spazieren ging, wurde von einem Hund gebissen."

    print("🧠 MetaboMind Textanalyse gestartet. Gib einen Satz ein (oder '/quit' zum Beenden):\n")
    while True:
        text = input("🗣️ > ").strip()
        if text.lower() == "/quit":
            print("👋 Tschüss!")
            break

        if not text:
            continue

        parser.parse_text(text)

        # Netzwerkgraph
        parser.parse_text(text)
        print("Graph-Entropie:", overall_graph_entropy(parser.graph))

        # GNN-Graph    
        print("GNN-Entropie:", overall_gnn_entropy(parser.gnn_graph))

        #draw_parse_graph(parser.graph, title="Parse-Graph für den Text")  # Visualisierung des Parse-Graphs
        #draw_gnn_graph(parser.gnn_graph, parser.doc, title="GNN-Graph für den Text")  # Visualisierung des GNN-Graphs
