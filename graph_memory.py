"""Graphbasierter Speicher mit einfachen Embeddings."""

import networkx as nx
import math
import json
import time
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EMBEDDING_SIZE = 20

def _text_embedding(text: str) -> list:
    """Very small bag-of-words hash embedding."""
    vec = [0] * EMBEDDING_SIZE
    for word in text.split():
        idx = hash(word) % EMBEDDING_SIZE
        vec[idx] += 1
    return vec

def _avg(vecs):
    if not vecs:
        return [0] * EMBEDDING_SIZE
    res = [0] * EMBEDDING_SIZE
    for v in vecs:
        for i, val in enumerate(v):
            res[i] += val
    return [r / len(vecs) for r in res]

def _cosine(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1)) or 1.0
    n2 = math.sqrt(sum(b * b for b in v2)) or 1.0
    return dot / (n1 * n2)

class GraphMemory:
    """Simple directed graph memory using networkx."""

    def __init__(self, link_k: int = 2, max_nodes: int = 1000, archive_path: str | None = None):
        # underlying directed graph storing all messages
        self.graph = nx.DiGraph()
        self.next_id = 0
        # how many similar nodes a new message should connect to
        self.link_k = link_k
        # maximum number of nodes to keep in memory
        self.max_nodes = max_nodes
        self.last_save = time.time()
        self.archive_path = archive_path
        # store entropy over time for plotting
        self._entropy_history = []

    def add_message(self, text: str, role: str) -> int:
        """Insert a new message into the graph and link it to similar nodes."""
        node_id = self.next_id
        # compute simple word-hash embedding for later similarity search
        emb = _text_embedding(text)
        self.graph.add_node(
            node_id,
            text=text,
            role=role,
            embedding=emb,
            timestamp=time.time(),
        )
        if node_id > 0:
            self.graph.add_edge(node_id - 1, node_id, weight=1.0)

        # link to the ``link_k`` most similar past nodes
        if self.graph.number_of_nodes() > 1:
            sims = []
            for n, data in self.graph.nodes(data=True):
                if n == node_id:
                    continue
                sim = _cosine(emb, data.get("embedding", [0] * EMBEDDING_SIZE))
                sims.append((sim, n))
            sims.sort(reverse=True, key=lambda x: x[0])
            for sim, n in sims[: self.link_k]:
                self.graph.add_edge(n, node_id, weight=float(sim))

        self.next_id += 1
        self.propagate_embeddings()
        self.prune()
        # record entropy development
        self._entropy_history.append((time.time(), self.entropy()))
        # keep history reasonably small
        if len(self._entropy_history) > self.max_nodes:
            self._entropy_history = self._entropy_history[-self.max_nodes :]
        return node_id

    def entropy(self) -> float:
        """Calculate simple Shannon entropy over degree distribution."""
        degrees = [d for _, d in self.graph.degree()]
        if not degrees:
            return 0.0
        total = sum(degrees)
        if total == 0:
            return 0.0
        probs = [d / total for d in degrees if d > 0]
        return -sum(p * math.log(p) for p in probs)

    def get_last_messages(self, limit: int = 5):
        """Return the last ``limit`` messages as list of dicts."""
        nodes = list(self.graph.nodes())[-limit:]
        return [self.graph.nodes[n] for n in nodes]

    def get_recent_messages(self, limit: int = 5):
        """Return most recent messages by timestamp."""
        nodes = sorted(
            self.graph.nodes(data=True),
            key=lambda x: x[1].get("timestamp", 0),
            reverse=True,
        )
        return [data for _id, data in nodes[:limit]]

    def search_messages(self, keyword: str):
        """Search for messages containing ``keyword``."""
        return [
            (n, data)
            for n, data in self.graph.nodes(data=True)
            if keyword.lower() in data.get("text", "").lower()
        ]

    def conversation(self, limit: int = 10):
        """Return last messages as ChatCompletion-style dicts."""
        nodes = list(self.graph.nodes())[-limit:]
        msgs = []
        for n in nodes:
            data = self.graph.nodes[n]
            msgs.append({"role": data.get("role", "user"), "content": data.get("text", "")})
        return msgs

    def propagate_embeddings(self):
        """One-step mean aggregation of neighbour embeddings."""
        # compute new embeddings by averaging predecessors with edge weights
        new_embeds = {}
        for node in self.graph.nodes():
            neigh_embs = []
            for n in self.graph.predecessors(node):
                w = self.graph.edges[n, node].get("weight", 1.0)
                emb = [e * w for e in self.graph.nodes[n]["embedding"]]
                neigh_embs.append(emb)
            own = self.graph.nodes[node]["embedding"]
            new_embeds[node] = _avg([own] + neigh_embs)
        for node, emb in new_embeds.items():
            self.graph.nodes[node]["embedding"] = emb

    def prune(self):
        """Remove oldest nodes if graph exceeds ``max_nodes``."""
        # keeps memory size in check and optionally archives removed nodes
        while self.graph.number_of_nodes() > self.max_nodes:
            # remove node with oldest timestamp
            oldest = min(
                self.graph.nodes(data=True),
                key=lambda x: x[1].get("timestamp", 0),
            )[0]
            if self.archive_path:
                data = self.graph.nodes[oldest]
                line = json.dumps(
                    {
                        "id": oldest,
                        "text": data.get("text"),
                        "role": data.get("role"),
                        "embedding": data.get("embedding"),
                        "timestamp": data.get("timestamp"),
                    }
                )
                with open(self.archive_path, "a", encoding="utf-8") as fh:
                    fh.write(line + "\n")
            self.graph.remove_node(oldest)

    def centrality(self, limit: int = 5):
        """Return nodes with highest betweenness centrality."""
        if self.graph.number_of_nodes() == 0:
            return []
        central = nx.betweenness_centrality(self.graph, weight="weight")
        ranked = sorted(central.items(), key=lambda x: x[1], reverse=True)
        return [(n, self.graph.nodes[n], c) for n, c in ranked[:limit]]

    def save(self, path: str):
        """Save graph to JSON."""
        data = {
            "nodes": [
                {
                    "id": n,
                    "text": d.get("text"),
                    "role": d.get("role"),
                    "embedding": d.get("embedding"),
                    "timestamp": d.get("timestamp"),
                }
                for n, d in self.graph.nodes(data=True)
            ],
            "edges": [
                {
                    "source": u,
                    "target": v,
                    "weight": data.get("weight", 1.0),
                }
                for u, v, data in self.graph.edges(data=True)
            ],
            "history": self._entropy_history,
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)

    def autosave(self, path: str, interval: float = 60.0):
        now = time.time()
        if now - self.last_save >= interval:
            self.last_save = now
            self.save(path)

    def load(self, path: str):
        """Load graph from JSON."""
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.graph.clear()
        self._entropy_history = data.get("history", [])
        for n in data.get("nodes", []):
            self.graph.add_node(
                n["id"],
                text=n.get("text"),
                role=n.get("role"),
                embedding=n.get("embedding", [0] * EMBEDDING_SIZE),
                timestamp=n.get("timestamp", time.time()),
            )
        for e in data.get("edges", []):
            if isinstance(e, list) or isinstance(e, tuple):
                u, v = e
                w = 1.0
            else:
                u = e.get("source")
                v = e.get("target")
                w = e.get("weight", 1.0)
            self.graph.add_edge(u, v, weight=w)
        self.next_id = max(self.graph.nodes(), default=-1) + 1
        self.prune()
        if not self._entropy_history:
            self._entropy_history.append((time.time(), self.entropy()))

    def stats(self) -> dict:
        """Return simple statistics about the graph."""
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "entropy": self.entropy(),
        }

    def entropy_history(self, limit: int = 100) -> list:
        """Return the last ``limit`` entropy values as ``(timestamp, entropy)``."""
        return self._entropy_history[-limit:]

    def top_words(self, limit: int = 10) -> list:
        """Return the most common words stored in the graph."""
        counts = {}
        for _, data in self.graph.nodes(data=True):
            text = data.get("text", "").lower()
            for word in text.split():
                counts[word] = counts.get(word, 0) + 1
        ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return ranked[:limit]

    def search_archive(self, keyword: str) -> list:
        """Search the archive file for a keyword if available."""
        if not self.archive_path or not os.path.exists(self.archive_path):
            return []
        results = []
        with open(self.archive_path, "r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if keyword.lower() in str(entry.get("text", "")).lower():
                    results.append(entry)
        return results

    def export_png(self, path: str = "graph.png") -> str:
        """Export the current memory graph to a PNG image."""
        # create a minimal empty figure if there are no nodes yet
        if self.graph.number_of_nodes() == 0:
            fig = plt.figure()
            fig.savefig(path)
            plt.close(fig)
            return path
        pos = nx.spring_layout(self.graph)
        plt.figure(figsize=(6, 4))
        nx.draw_networkx(
            self.graph,
            pos,
            node_color="#1f78b4",
            edge_color="#888888",
            font_size=8,
            font_color="#ffffff",
        )
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        return path

    def shortest_path(self, word1: str, word2: str) -> list:
        """Return the shortest path between two messages containing the given words."""
        nodes1 = [n for n, d in self.graph.nodes(data=True) if word1.lower() in d.get("text", "").lower()]
        nodes2 = [n for n, d in self.graph.nodes(data=True) if word2.lower() in d.get("text", "").lower()]
        if not nodes1 or not nodes2:
            return []
        best = None
        best_path = []
        for a in nodes1:
            for b in nodes2:
                try:
                    path = nx.shortest_path(self.graph, a, b)
                except nx.NetworkXNoPath:
                    continue
                if best is None or len(path) < best:
                    best = len(path)
                    best_path = path
        return [(n, self.graph.nodes[n].get("text", "")) for n in best_path]
