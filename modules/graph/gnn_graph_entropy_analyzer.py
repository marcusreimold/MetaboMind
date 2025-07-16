import math
from collections import Counter
import torch
from torch_geometric.data import Data

def shannon_entropy_tensor(tensor: torch.Tensor) -> float:
    values = tensor.tolist()
    counter = Counter(values)
    total = sum(counter.values())
    probs = [count / total for count in counter.values()]
    return -sum(p * math.log2(p) for p in probs if p > 0)

def node_feature_entropy(data: Data) -> float:
    """Berechnet Entropie über Knotenfeatures (x) – nur für diskrete Werte"""
    entropies = []
    for i in range(data.x.shape[1]):
        col = data.x[:, i]
        entropies.append(shannon_entropy_tensor(col))
    return sum(entropies) / len(entropies)

def degree_entropy(data: Data) -> float:
    degrees = torch.bincount(data.edge_index[1])
    return shannon_entropy_tensor(degrees)

def edge_label_entropy(data: Data) -> float:
    if not hasattr(data, "edge_attr"):
        return 0.0
    flat = data.edge_attr.view(-1)
    return shannon_entropy_tensor(flat)

def overall_gnn_entropy(data: Data) -> dict:
    return {
        "node_feature_entropy": node_feature_entropy(data),
        "edge_label_entropy": edge_label_entropy(data),
        "degree_entropy": degree_entropy(data)
    }
