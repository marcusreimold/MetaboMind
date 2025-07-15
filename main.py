from graph.metabo_memory import MetaboMemory
from graph.graph_utils import draw_parse_graph, draw_gnn_graph
from graph.graph_entropy_analyzer import overall_graph_entropy
from graph.gnn_graph_entropy_analyzer import overall_gnn_entropy

 
if __name__ == "__main__":
    memory = MetaboMemory()
    #text = "Der Mann, der gestern im Park spazieren ging, wurde von einem Hund gebissen."

    print("🧠 MetaboMind Textanalyse gestartet. Gib einen Satz ein (oder '/quit' zum Beenden):\n")
    while True:
        text = input("🗣️ > ").strip()
        if text.lower() == "/quit":
            print("👋 Tschüss!")
            break

        if not text:
            continue

        memory.add_text(text)

        print("\n📊 Aktuelle Netzwerk-Entropie:")
        for k, v in memory.get_graph_entropy().items():
            print(f"  {k}: {v:.4f}")

        print("\n🧬 Aktuelle GNN-Entropie:")
        for k, v in memory.get_gnn_entropy().items():
            print(f"  {k}: {v:.4f}")

        print("\n🔁 Nächster Satz oder '/quit'\n")
        #draw_parse_graph(parser.graph, title="Parse-Graph für den Text")  # Visualisierung des Parse-Graphs
        #draw_gnn_graph(parser.gnn_graph, parser.doc, title="GNN-Graph für den Text")  # Visualisierung des GNN-Graphs
