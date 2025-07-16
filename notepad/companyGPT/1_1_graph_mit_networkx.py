"""
MetaboMind Graph Module - Kernimplementierung der Graphfunktionalitäten mit NetworkX
"""

import networkx as nx
import uuid
import json
import pickle
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from datetime import datetime
import logging

# Logging-Setup
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MetaboGraph")


class MetaboNode:
    """
    Repräsentation eines Knotens im MetaboMind-Wissensgraphen
    """
    def __init__(self, 
                 node_id: Optional[str] = None,
                 labels: Optional[List[str]] = None,
                 properties: Optional[Dict[str, Any]] = None,
                 layer: str = "instance"):
        """
        Initialisiert einen Knoten im Wissensgraphen
        
        Args:
            node_id: Eindeutige ID (wird automatisch generiert, wenn nicht angegeben)
            labels: Liste von Labels/Typen für den Knoten
            properties: Eigenschaften des Knotens
            layer: Hierarchieebene des Knotens (meta, concept, instance, temporal)
        """
        self.id = node_id if node_id else str(uuid.uuid4())
        self.labels = labels or []
        self.properties = properties or {}
        self.layer = layer
        self.metadata = {
            "confidence": 1.0,
            "creation_time": datetime.now(),
            "last_access": datetime.now(),
            "access_count": 0,
            "entropy_contribution": 0.0,
            "yin_yang_state": 0.5,
            "source": None,
            "validation_status": None
        }
        self.embeddings = {}  # Verschiedene Embedding-Räume
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert den Knoten in ein Dictionary"""
        return {
            "id": self.id,
            "labels": self.labels,
            "properties": self.properties,
            "layer": self.layer,
            "metadata": {
                **self.metadata,
                "creation_time": self.metadata["creation_time"].isoformat(),
                "last_access": self.metadata["last_access"].isoformat()
            },
            "embeddings": self.embeddings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetaboNode':
        """Erstellt einen Knoten aus einem Dictionary"""
        node = cls(
            node_id=data["id"],
            labels=data["labels"],
            properties=data["properties"],
            layer=data["layer"]
        )
        
        # Metadata wiederherstellen
        node.metadata = data["metadata"]
        # Datumsfelder konvertieren
        node.metadata["creation_time"] = datetime.fromisoformat(node.metadata["creation_time"])
        node.metadata["last_access"] = datetime.fromisoformat(node.metadata["last_access"])
        
        node.embeddings = data.get("embeddings", {})
        
        return node
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Aktualisiert einen Metadatenwert"""
        if key in self.metadata:
            self.metadata[key] = value
    
    def increment_access(self) -> None:
        """Aktualisiert Zugriffszähler und -zeitstempel"""
        self.metadata["access_count"] += 1
        self.metadata["last_access"] = datetime.now()

    def __str__(self) -> str:
        """String-Repräsentation für leichtes Debugging"""
        return f"Node({self.id}, labels={self.labels}, layer={self.layer})"
    

class MetaboRelation:
    """
    Repräsentation einer Relation im MetaboMind-Wissensgraphen
    """
    def __init__(self,
                 source_id: str,
                 target_id: str,
                 rel_type: str,
                 rel_id: Optional[str] = None,
                 weight: float = 1.0,
                 properties: Optional[Dict[str, Any]] = None):
        """
        Initialisiert eine Relation im Wissensgraphen
        
        Args:
            source_id: ID des Quellknotens
            target_id: ID des Zielknotens
            rel_type: Typ der Relation
            rel_id: Eindeutige ID (wird automatisch generiert, wenn nicht angegeben)
            weight: Gewichtung der Relation (0.0 bis 1.0)
            properties: Zusätzliche Eigenschaften der Relation
        """
        self.id = rel_id if rel_id else str(uuid.uuid4())
        self.source_id = source_id
        self.target_id = target_id
        self.type = rel_type
        self.weight = weight
        self.properties = properties or {}
        self.metadata = {
            "confidence": 1.0,
            "creation_time": datetime.now(),
            "last_reinforced": datetime.now(),
            "reinforcement_count": 0,
            "entropy_contribution": 0.0,
            "source": None
        }
        self.bidirectional = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert die Relation in ein Dictionary"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
            "weight": self.weight,
            "properties": self.properties,
            "metadata": {
                **self.metadata,
                "creation_time": self.metadata["creation_time"].isoformat(),
                "last_reinforced": self.metadata["last_reinforced"].isoformat()
            },
            "bidirectional": self.bidirectional
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetaboRelation':
        """Erstellt eine Relation aus einem Dictionary"""
        relation = cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            rel_type=data["type"],
            rel_id=data["id"],
            weight=data["weight"],
            properties=data["properties"]
        )
        
        # Metadata wiederherstellen
        relation.metadata = data["metadata"]
        # Datumsfelder konvertieren
        relation.metadata["creation_time"] = datetime.fromisoformat(relation.metadata["creation_time"])
        relation.metadata["last_reinforced"] = datetime.fromisoformat(relation.metadata["last_reinforced"])
        
        relation.bidirectional = data["bidirectional"]
        
        return relation
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Aktualisiert einen Metadatenwert"""
        if key in self.metadata:
            self.metadata[key] = value
    
    def reinforce(self, amount: float = 0.1) -> None:
        """Verstärkt die Relation durch Erhöhung des Gewichts"""
        self.weight = min(1.0, self.weight + amount)
        self.metadata["reinforcement_count"] += 1
        self.metadata["last_reinforced"] = datetime.now()
    
    def decay(self, amount: float = 0.05) -> None:
        """Schwächt die Relation durch Verringerung des Gewichts"""
        self.weight = max(0.01, self.weight - amount)

    def __str__(self) -> str:
        """String-Repräsentation für leichtes Debugging"""
        return f"Relation({self.id}, {self.source_id} -[{self.type}]-> {self.target_id}, weight={self.weight})"


class MetaboGraph:
    """
    Hauptklasse für den MetaboMind-Wissensgraphen
    """
    def __init__(self):
        """Initialisiert den Wissensgraphen"""
        # NetworkX MultiDiGraph für mehrere gerichtete Kanten zwischen Knoten
        self.graph = nx.MultiDiGraph()
        
        # Hierarchie-Lookup für schnellen Zugriff auf Ebenen
        self.hierarchies = {
            "meta": set(),      # Meta-Bewusstseinsebene
            "concept": set(),   # Konzeptebene 
            "instance": set(),  # Instanzebene
            "temporal": set()   # Temporale Ebene
        }
        
        # Lookup für schnellen Zugriff auf Knoten und Relationen
        self._node_lookup = {}  # id -> MetaboNode
        self._relation_lookup = {}  # id -> MetaboRelation
        
        # Mapping von Relation-IDs zu NetworkX-Kanten
        self._relation_to_edge = {}  # relation_id -> (source_id, target_id, key)
        
        logger.info("Initialized new MetaboGraph")
    
    def add_node(self, node: MetaboNode) -> str:
        """
        Fügt einen Knoten zum Graphen hinzu
        
        Args:
            node: Hinzuzufügender Knoten
            
        Returns:
            ID des hinzugefügten Knotens
        """
        # Knoten zum NetworkX-Graph hinzufügen
        self.graph.add_node(node.id, **node.to_dict())
        
        # Knoten im Lookup speichern
        self._node_lookup[node.id] = node
        
        # Zur entsprechenden Hierarchie hinzufügen
        if node.layer in self.hierarchies:
            self.hierarchies[node.layer].add(node.id)
        else:
            logger.warning(f"Unknown layer type '{node.layer}' for node {node.id}")
            # Standardmäßig zur Instance-Ebene hinzufügen
            self.hierarchies["instance"].add(node.id)
        
        logger.debug(f"Added node: {node}")
        return node.id
    
    def add_relation(self, relation: MetaboRelation) -> str:
        """
        Fügt eine Relation zum Graphen hinzu
        
        Args:
            relation: Hinzuzufügende Relation
            
        Returns:
            ID der hinzugefügten Relation
        """
        # Prüfen, ob Quell- und Zielknoten existieren
        if relation.source_id not in self.graph:
            logger.warning(f"Source node {relation.source_id} does not exist. Relation not added.")
            return None
        
        if relation.target_id not in self.graph:
            logger.warning(f"Target node {relation.target_id} does not exist. Relation not added.")
            return None
        
        # Relation zum NetworkX-Graph hinzufügen (key ist die relation.id)
        self.graph.add_edge(
            relation.source_id, 
            relation.target_id, 
            key=relation.id, 
            **relation.to_dict()
        )
        
        # Relation im Lookup speichern
        self._relation_lookup[relation.id] = relation
        self._relation_to_edge[relation.id] = (relation.source_id, relation.target_id, relation.id)
        
        # Bei bidirektionalen Beziehungen auch die umgekehrte Richtung hinzufügen
        if relation.bidirectional:
            reverse_relation = MetaboRelation(
                source_id=relation.target_id,
                target_id=relation.source_id,
                rel_type=relation.type,
                rel_id=f"{relation.id}_reverse",
                weight=relation.weight,
                properties=relation.properties.copy()
            )
            reverse_relation.metadata = relation.metadata.copy()
            reverse_relation.bidirectional = True
            
            self.graph.add_edge(
                reverse_relation.source_id, 
                reverse_relation.target_id, 
                key=reverse_relation.id, 
                **reverse_relation.to_dict()
            )
            
            self._relation_lookup[reverse_relation.id] = reverse_relation
            self._relation_to_edge[reverse_relation.id] = (reverse_relation.source_id, reverse_relation.target_id, reverse_relation.id)
        
        logger.debug(f"Added relation: {relation}")
        return relation.id
    
    def get_node(self, node_id: str) -> Optional[MetaboNode]:
        """
        Holt einen Knoten aus dem Graphen
        
        Args:
            node_id: ID des Knotens
            
        Returns:
            Der Knoten oder None, wenn nicht gefunden
        """
        if node_id in self._node_lookup:
            node = self._node_lookup[node_id]
            node.increment_access()
            return node
        
        return None
    
    def get_relations(self, source_id: str, target_id: Optional[str] = None, rel_type: Optional[str] = None) -> List[MetaboRelation]:
        """
        Holt Relationen aus dem Graphen
        
        Args:
            source_id: ID des Quellknotens
            target_id: Optional, ID des Zielknotens
            rel_type: Optional, Typ der Relation
            
        Returns:
            Liste von passenden Relationen
        """
        relations = []
        
        # Wenn kein Zielknoten angegeben, alle ausgehenden Kanten prüfen
        if target_id is None:
            for _, t, key, data in self.graph.out_edges(source_id, keys=True, data=True):
                if rel_type is None or data.get("type") == rel_type:
                    relation_id = key
                    if relation_id in self._relation_lookup:
                        relations.append(self._relation_lookup[relation_id])
        else:
            # Spezifische Kante zwischen zwei Knoten
            if self.graph.has_edge(source_id, target_id):
                for key, data in self.graph[source_id][target_id].items():
                    if rel_type is None or data.get("type") == rel_type:
                        relation_id = key
                        if relation_id in self._relation_lookup:
                            relations.append(self._relation_lookup[relation_id])
        
        return relations
    
    def remove_node(self, node_id: str) -> bool:
        """
        Entfernt einen Knoten aus dem Graphen
        
        Args:
            node_id: ID des zu entfernenden Knotens
            
        Returns:
            True, wenn der Knoten erfolgreich entfernt wurde
        """
        if node_id not in self.graph:
            logger.warning(f"Node {node_id} does not exist. Cannot remove.")
            return False
        
        # Aus Hierarchien entfernen
        for layer_nodes in self.hierarchies.values():
            if node_id in layer_nodes:
                layer_nodes.remove(node_id)
        
        # Alle mit diesem Knoten verbundenen Relationen finden und entfernen
        relations_to_remove = []
        
        # Ausgehende Relationen
        for _, target, key in list(self.graph.out_edges(node_id, keys=True)):
            relations_to_remove.append(key)
        
        # Eingehende Relationen
        for source, _, key in list(self.graph.in_edges(node_id, keys=True)):
            relations_to_remove.append(key)
        
        # Relationen aus Lookups entfernen
        for rel_id in relations_to_remove:
            if rel_id in self._relation_lookup:
                del self._relation_lookup[rel_id]
            
            if rel_id in self._relation_to_edge:
                del self._relation_to_edge[rel_id]
        
        # Knoten aus Graph entfernen
        self.graph.remove_node(node_id)
        
        # Aus Lookup entfernen
        if node_id in self._node_lookup:
            del self._node_lookup[node_id]
        
        logger.debug(f"Removed node: {node_id}")
        return True
    
    def remove_relation(self, rel_id: str) -> bool:
        """
        Entfernt eine Relation aus dem Graphen
        
        Args:
            rel_id: ID der zu entfernenden Relation
            
        Returns:
            True, wenn die Relation erfolgreich entfernt wurde
        """
        if rel_id not in self._relation_lookup:
            logger.warning(f"Relation {rel_id} does not exist. Cannot remove.")
            return False
        
        # Edge-Informationen holen
        if rel_id in self._relation_to_edge:
            source_id, target_id, key = self._relation_to_edge[rel_id]
            
            # Kante aus dem Graph entfernen
            if self.graph.has_edge(source_id, target_id, key=key):
                self.graph.remove_edge(source_id, target_id, key=key)
            
            # Bei bidirektionalen Beziehungen auch die Umkehrrelation prüfen und entfernen
            reverse_rel_id = f"{rel_id}_reverse"
            if reverse_rel_id in self._relation_lookup:
                # Umkehrrelation aus Lookups entfernen
                if reverse_rel_id in self._relation_to_edge:
                    rev_source, rev_target, rev_key = self._relation_to_edge[reverse_rel_id]
                    if self.graph.has_edge(rev_source, rev_target, key=rev_key):
                        self.graph.remove_edge(rev_source, rev_target, key=rev_key)
                    del self._relation_to_edge[reverse_rel_id]
                
                del self._relation_lookup[reverse_rel_id]
            
            # Aus Lookups entfernen
            del self._relation_to_edge[rel_id]
        
        # Aus Relation-Lookup entfernen
        del self._relation_lookup[rel_id]
        
        logger.debug(f"Removed relation: {rel_id}")
        return True
    
    def get_neighbors(self, node_id: str, rel_type: Optional[str] = None) -> List[str]:
        """
        Findet alle Nachbarn eines Knotens
        
        Args:
            node_id: ID des Knotens
            rel_type: Optional, Typ der Relation
            
        Returns:
            Liste von Nachbarknoten-IDs
        """
        neighbors = set()
        
        # Alle ausgehenden Nachbarn überprüfen
        for _, target, data in self.graph.out_edges(node_id, data=True):
            if rel_type is None or data.get("type") == rel_type:
                neighbors.add(target)
        
        # Alle eingehenden Nachbarn überprüfen
        for source, _, data in self.graph.in_edges(node_id, data=True):
            if rel_type is None or data.get("type") == rel_type:
                neighbors.add(source)
        
        return list(neighbors)
    
    def get_shortest_path(self, source_id: str, target_id: str) -> List[Tuple[str, str]]:
        """
        Findet den kürzesten Pfad zwischen zwei Knoten
        
        Args:
            source_id: Start-Knoten
            target_id: Ziel-Knoten
            
        Returns:
            Liste von (Knoten-ID, Relation-ID) Tupeln, die den Pfad bilden
        """
        try:
            # NetworkX-Pfad finden
            path_nodes = nx.shortest_path(self.graph, source_id, target_id)
            
            # Pfad in (Knoten, Relation) Tupel umwandeln
            path = []
            for i in range(len(path_nodes) - 1):
                node_id = path_nodes[i]
                next_node_id = path_nodes[i + 1]
                
                # Alle Relationen zwischen diesen Knoten finden
                relations = self.get_relations(node_id, next_node_id)
                if relations:
                    # Einfach die erste Relation verwenden
                    relation_id = relations[0].id
                    path.append((node_id, relation_id))
                else:
                    # Sollte nicht passieren, wenn der Pfad gültig ist
                    logger.warning(f"No relation found between {node_id} and {next_node_id}")
                    path.append((node_id, None))
            
            # Letzten Knoten hinzufügen
            path.append((path_nodes[-1], None))
            
            return path
        
        except nx.NetworkXNoPath:
            logger.info(f"No path found between {source_id} and {target_id}")
            return []
    
    def search_by_property(self, property_key: str, property_value: Any) -> List[str]:
        """
        Sucht Knoten basierend auf Eigenschaften
        
        Args:
            property_key: Eigenschaftsschlüssel
            property_value: Zu suchender Wert
            
        Returns:
            Liste von passenden Knoten-IDs
        """
        matching_nodes = []
        
        for node_id in self.graph.nodes:
            node = self.get_node(node_id)
            if node and property_key in node.properties:
                # Unterstützung für verschiedene Vergleichstypen
                if isinstance(property_value, str) and isinstance(node.properties[property_key], str):
                    # Teilstring-Suche für Strings
                    if property_value.lower() in node.properties[property_key].lower():
                        matching_nodes.append(node_id)
                else:
                    # Exakter Vergleich für andere Typen
                    if node.properties[property_key] == property_value:
                        matching_nodes.append(node_id)
        
        return matching_nodes
    
    def get_subgraph_by_layer(self, layer: str) -> nx.MultiDiGraph:
        """
        Extrahiert einen Teilgraphen basierend auf der Hierarchieebene
        
        Args:
            layer: Hierarchieebene (meta, concept, instance, temporal)
            
        Returns:
            Teilgraph mit Knoten der angegebenen Ebene
        """
        if layer not in self.hierarchies:
            logger.warning(f"Unknown layer: {layer}")
            return nx.MultiDiGraph()
        
        # Teilgraph mit den Knoten der angegebenen Ebene extrahieren
        return self.graph.subgraph(self.hierarchies[layer])
    
    def save_to_file(self, filepath: str) -> bool:
        """
        Speichert den Graphen in einer Pickle-Datei
        
        Args:
            filepath: Pfad zum Speichern des Graphen
            
        Returns:
            True bei erfolgreichem Speichern
        """
        try:
            # Graphen und Zusatzdaten in Dictionary speichern
            data_to_save = {
                "graph": self.graph,
                "hierarchies": self.hierarchies,
                "node_lookup": self._node_lookup,
                "relation_lookup": self._relation_lookup,
                "relation_to_edge": self._relation_to_edge
            }
            
            # In Datei speichern
            with open(filepath, 'wb') as f:
                pickle.dump(data_to_save, f)
            
            logger.info(f"Graph successfully saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving graph to file: {e}")
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """
        Lädt einen Graphen aus einer Pickle-Datei
        
        Args:
            filepath: Pfad zur Graphendatei
            
        Returns:
            True bei erfolgreichem Laden
        """
        try:
            # Aus Datei laden
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            # Daten wiederherstellen
            self.graph = data["graph"]
            self.hierarchies = data["hierarchies"]
            self._node_lookup = data["node_lookup"]
            self._relation_lookup = data["relation_lookup"]
            self._relation_to_edge = data["relation_to_edge"]
            
            logger.info(f"Graph successfully loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading graph from file: {e}")
            return False
    
    def export_to_json(self, filepath: str) -> bool:
        """
        Exportiert den Graphen als JSON-Datei
        
        Args:
            filepath: Pfad zum Speichern des JSON
            
        Returns:
            True bei erfolgreichem Export
        """
        try:
            # Knoten und Relationen extrahieren
            nodes_data = [node.to_dict() for node in self._node_lookup.values()]
            relations_data = [rel.to_dict() for rel in self._relation_lookup.values()]
            
            # In JSON-Format umwandeln
            json_data = {
                "nodes": nodes_data,
                "relations": relations_data,
                "metadata": {
                    "node_count": len(nodes_data),
                    "relation_count": len(relations_data),
                    "export_time": datetime.now().isoformat(),
                    "hierarchies": {k: list(v) for k, v in self.hierarchies.items()}
                }
            }
            
            # In Datei speichern
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Graph successfully exported to JSON: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting graph to JSON: {e}")
            return False
    
    def import_from_json(self, filepath: str) -> bool:
        """
        Importiert einen Graphen aus einer JSON-Datei
        
        Args:
            filepath: Pfad zur JSON-Datei
            
        Returns:
            True bei erfolgreichem Import
        """
        try:
            # Aus Datei laden
            with open(filepath, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Bestehenden Graphen löschen
            self.graph = nx.MultiDiGraph()
            self._node_lookup = {}
            self._relation_lookup = {}
            self._relation_to_edge = {}
            self.hierarchies = {
                "meta": set(),
                "concept": set(),
                "instance": set(),
                "temporal": set()
            }
            
            # Knoten hinzufügen
            for node_data in json_data["nodes"]:
                node = MetaboNode.from_dict(node_data)
                self.add_node(node)
            
            # Relationen hinzufügen
            for rel_data in json_data["relations"]:
                relation = MetaboRelation.from_dict(rel_data)
                self.add_relation(relation)
            
            # Optional: Hierarchien aus Metadaten wiederherstellen
            if "metadata" in json_data and "hierarchies" in json_data["metadata"]:
                for layer, nodes in json_data["metadata"]["hierarchies"].items():
                    self.hierarchies[layer] = set(nodes)
            
            logger.info(f"Graph successfully imported from JSON: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing graph from JSON: {e}")
            return False
    
    def visualize(self, figsize=(12, 10), max_nodes=100, title="MetaboMind Graph") -> None:
        """
        Visualisiert den Graphen mit matplotlib
        
        Args:
            figsize: Größe der Abbildung als Tuple (Breite, Höhe)
            max_nodes: Maximale Anzahl von anzuzeigenden Knoten
            title: Titel der Visualisierung
        """
        # Wenn der Graph zu groß ist, nur eine Teilmenge anzeigen
        if len(self.graph) > max_nodes:
            logger.info(f"Graph has {len(self.graph)} nodes, showing only {max_nodes}")
            # Wichtigste Knoten auswählen (z.B. basierend auf Grad)
            nodes = sorted(self.graph.nodes, key=lambda n: self.graph.degree(n), reverse=True)[:max_nodes]
            subgraph = self.graph.subgraph(nodes)
        else:
            subgraph = self.graph
        
        plt.figure(figsize=figsize)
        plt.title(title)
        
        # Knotenpositionen berechnen
        pos = nx.spring_layout(subgraph, seed=42)
        
        # Farben nach Layer
        layer_colors = {
            "meta": "red",
            "concept": "blue",
            "instance": "green",
            "temporal": "purple"
        }
        
        # Knoten nach Layern gruppieren
        layer_nodes = {}
        for layer in self.hierarchies:
            layer_nodes[layer] = [n for n in subgraph.nodes if n in self.hierarchies[layer]]
        
        # Knoten zeichnen
        for layer, nodes in layer_nodes.items():
            nx.draw_networkx_nodes(
                subgraph, pos, 
                nodelist=nodes, 
                node_color=layer_colors.get(layer, "gray"),
                node_size=300, 
                alpha=0.8,
                label=f"{layer} layer"
            )
        
        # Kanten zeichnen
        nx.draw_networkx_edges(
            subgraph, pos, 
            width=1.0, 
            alpha=0.5, 
            arrows=True,
            arrowstyle='-|>'
        )
        
        # Knotenbeschriftungen
        node_labels = {node: self.get_node(node).properties.get("name", node) 
                       for node in subgraph.nodes}
        nx.draw_networkx_labels(subgraph, pos, labels=node_labels, font_size=10)
        
        # Legende hinzufügen
        plt.legend(loc="best")
        plt.axis('off')
        plt.tight_layout()
        plt.show()


# Beispielverwendung
if __name__ == "__main__":
    # Erstelle einen neuen Graphen
    graph = MetaboGraph()
    
    # Einige Knoten hinzufügen
    metabomind = MetaboNode(
        labels=["System", "AI"], 
        properties={"name": "MetaboMind", "description": "Self-optimizing knowledge system"},
        layer="concept"
    )
    graph.add_node(metabomind)
    
    yin_yang = MetaboNode(
        labels=["Principle", "Philosophy"],
        properties={"name": "Yin-Yang", "description": "Balance of opposites"},
        layer="concept"
    )
    graph.add_node(yin_yang)
    
    entropy = MetaboNode(
        labels=["Principle", "Physics"],
        properties={"name": "Entropy", "description": "Measure of disorder or randomness"},
        layer="concept"
    )
    graph.add_node(entropy)
    
    knowledge_graph = MetaboNode(
        labels=["Component", "Technology"],
        properties={"name": "Knowledge Graph", "description": "Structured knowledge representation"},
        layer="concept"
    )
    graph.add_node(knowledge_graph)
    
    # Einige Relationen hinzufügen
    uses_relation = MetaboRelation(
        source_id=metabomind.id,
        target_id=yin_yang.id,
        rel_type="USES",
        properties={"context": "As regulatory principle"}
    )
    graph.add_relation(uses_relation)
    
    minimizes_relation = MetaboRelation(
        source_id=metabomind.id,
        target_id=entropy.id,
        rel_type="MINIMIZES",
        properties={"context": "For system optimization"}
    )
    graph.add_relation(minimizes_relation)
    
    has_component_relation = MetaboRelation(
        source_id=metabomind.id,
        target_id=knowledge_graph.id,
        rel_type="HAS_COMPONENT",
        properties={}
    )
    graph.add_relation(has_component_relation)
    
    regulates_relation = MetaboRelation(
        source_id=yin_yang.id,
        target_id=entropy.id,
        rel_type="REGULATES",
        properties={},
        bidirectional=True
    )
    graph.add_relation(regulates_relation)
    
    # Graph visualisieren
    print("Visualizing graph...")
    graph.visualize(title="MetaboMind Concept Graph")
    
    # Graph speichern
    print("Saving graph...")
    graph.save_to_file("metabomind_graph.pkl")
    graph.export_to_json("metabomind_graph.json")
    
    # Graph aus Datei laden
    print("Loading graph...")
    new_graph = MetaboGraph()
    new_graph.load_from_file("metabomind_graph.pkl")
    
    # Demo für einige Funktionen
    print("\nFinding neighbors of MetaboMind node:")
    neighbors = new_graph.get_neighbors(metabomind.id)
    for neighbor_id in neighbors:
        neighbor = new_graph.get_node(neighbor_id)
        print(f"- {neighbor.properties.get('name', neighbor.id)}")
    
    print("\nSearching for nodes with 'knowledge' in their description:")
    knowledge_nodes = new_graph.search_by_property("description", "knowledge")
    for node_id in knowledge_nodes:
        node = new_graph.get_node(node_id)
        print(f"- {node.properties.get('name', node.id)}: {node.properties.get('description', '')}")
    
    print("\nFinding shortest path from Yin-Yang to Knowledge Graph:")
    path = new_graph.get_shortest_path(yin_yang.id, knowledge_graph.id)
    if path:
        for node_id, relation_id in path:
            node = new_graph.get_node(node_id)
            node_name = node.properties.get("name", node.id)
            
            if relation_id:
                relation = new_graph.get_relations(node_id, target_id=path[path.index((node_id, relation_id))+1][0])
                if relation:
                    rel_type = relation[0].type
                    print(f"{node_name} -[{rel_type}]-> ", end="")
                else:
                    print(f"{node_name} -> ", end="")
            else:
                print(f"{node_name}")
    else:
        print("No path found.")