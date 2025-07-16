from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

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
        """
        Konvertiert den Knoten in ein Dictionary
        
        Returns:
            Dict-Repräsentation des Knotens
        """
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
        """
        Aktualisiert einen Metadatenwert
        
        Args:
            key: Metadatenschlüssel
            value: Neuer Wert
        """
        if key in self.metadata:
            self.metadata[key] = value
    
    def increment_access(self) -> None:
        """
        Aktualisiert Zugriffszähler und -zeitstempel
        """
        self.metadata["access_count"] += 1
        self.metadata["last_access"] = datetime.now()
        
    def __str__(self) -> str:
        """String-Repräsentation für leichtes Debugging"""
        return f"Node({self.id}, labels={self.labels}, layer={self.layer})"