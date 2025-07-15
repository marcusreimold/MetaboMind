import math
from collections import Counter
import networkx as nx

def shannon_entropy(values: list[str]) -> float:
    counter = Counter(values)
    total = sum(counter.values())
    probs = [count / total for count in counter.values()]
    return -sum(p * math.log2(p) for p in probs if p > 0)

def dependency_entropy(G: nx.MultiDiGraph) -> float:
    dep_labels = [data["label"] for _, _, data in G.edges(data=True) if "label" in data]
    return shannon_entropy(dep_labels)

def pos_entropy(G: nx.MultiDiGraph) -> float:
    pos_tags = [data["pos"] for _, data in G.nodes(data=True) if "pos" in data]
    return shannon_entropy(pos_tags)

def degree_entropy(G: nx.MultiDiGraph) -> float:
    degrees = [G.degree(n) for n in G.nodes()]
    return shannon_entropy(degrees)

def overall_graph_entropy(G: nx.MultiDiGraph) -> dict:
    return {
        "pos_entropy": pos_entropy(G),
        "dep_entropy": dependency_entropy(G),
        "degree_entropy": degree_entropy(G)
    }
