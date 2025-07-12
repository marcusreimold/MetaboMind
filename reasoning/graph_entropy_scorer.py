import networkx as nx


def _to_simple_undirected(graph: nx.Graph) -> nx.Graph:
    """Return a simple undirected version of ``graph``.

    ``networkx`` functions such as clustering do not support MultiGraphs. This
    helper collapses parallel edges and drops direction to avoid related
    exceptions.
    """
    if isinstance(graph, (nx.MultiGraph, nx.MultiDiGraph)):
        g = nx.Graph()
        g.add_nodes_from(graph.nodes())
        g.add_edges_from(graph.edges())
    else:
        g = graph.to_undirected() if graph.is_directed() else graph
    return g


def _analyse_graph(graph: nx.Graph) -> dict:
    """Return basic structural metrics for ``graph``."""
    n = graph.number_of_nodes()
    isolates = len(list(nx.isolates(graph))) if n else 0
    if graph.is_directed():
        components = list(nx.weakly_connected_components(graph))
    else:
        components = list(nx.connected_components(graph))
    num_components = len(components)
    avg_degree = sum(d for _, d in graph.degree()) / n if n else 0.0
    undirected_simple = _to_simple_undirected(graph)
    clustering = nx.average_clustering(undirected_simple) if n > 1 else 0.0
    largest = max(components, key=len) if components else set()
    avg_path_len = None
    if len(largest) > 1:
        try:
            sub = _to_simple_undirected(graph.subgraph(largest))
            avg_path_len = nx.average_shortest_path_length(sub)
        except Exception:
            avg_path_len = None
    return {
        "nodes": n,
        "isolates": isolates,
        "components": num_components,
        "avg_degree": avg_degree,
        "clustering": clustering,
        "largest_size": len(largest),
        "avg_path_len": avg_path_len,
    }


def calculate_entropy(graph: nx.Graph) -> float:
    """Return a normalized entropy score for ``graph`` (0.0–1.0)."""
    data = _analyse_graph(graph)
    n = max(data["nodes"], 1)
    iso_frac = data["isolates"] / n
    comp_frac = (data["components"] - 1) / max(n - 1, 1)
    avg_degree_norm = 1 - min(data["avg_degree"] / 4, 1)
    clustering_norm = 1 - data["clustering"]
    if data["avg_path_len"] and data["largest_size"] > 1:
        path_norm = min((data["avg_path_len"] - 1) / max(data["largest_size"] - 1, 1), 1)
    else:
        path_norm = 1.0 if data["nodes"] > 1 else 0.0
    weights = [0.25, 0.2, 0.2, 0.2, 0.15]
    metrics = [iso_frac, comp_frac, avg_degree_norm, clustering_norm, path_norm]
    score = sum(w * m for w, m in zip(weights, metrics))
    return max(0.0, min(score, 1.0))


def explain_entropy(graph: nx.Graph) -> str:
    """Return a human readable explanation for the entropy score."""
    data = _analyse_graph(graph)
    score = calculate_entropy(graph)
    parts = [
        f"Der Graph besitzt {data['nodes']} Knoten.",
        f"Durchschnittlicher Knotendegree: {data['avg_degree']:.2f}.",
        f"{data['isolates']} isolierte Knoten.",
        f"{data['components']} verbundene Komponenten.",
        f"Clustering-Koeffizient: {data['clustering']:.2f}.",
    ]
    if data["avg_path_len"]:
        parts.append(f"Mittlere Pfadlänge in größter Komponente: {data['avg_path_len']:.2f}.")
    explanation = " ".join(parts)
    return explanation + f" Ergebnis-Entropie: {score:.2f}."

