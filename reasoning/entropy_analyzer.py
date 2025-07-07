import math
from collections import Counter
import networkx as nx


def entropy_of_graph(graph: nx.Graph) -> float:
    """Compute Shannon entropy of node degree distribution."""
    degrees = [d for _, d in graph.degree()]
    if not degrees:
        return 0.0
    count = Counter(degrees)
    total = sum(count.values())
    entropy = 0.0
    for freq in count.values():
        p = freq / total
        entropy -= p * math.log(p, 2)
    return entropy
