from typing import Dict, Any, Optional
from datetime import datetime
import uuid

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
                 properties: Optional[Dict[str, Any]] = None,
                 bidirectional: bool = False):
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
        self.bidirectional = bidirectional
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert die Relation in ein Dictionary
        
        Returns:
            Dict-Repräsentation der Relation
        """
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
        """
        Erstellt eine Relation aus einem Dictionary
        
        Args:
            data: Dictionary mit Relationsdaten
            
        Returns:
            Erstellte MetaboRelation
        """
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
        """
        Aktualisiert einen Metadatenwert
        
        Args:
            key: Metadatenschlüssel
            value: Neuer Wert
        """
        if key in self.metadata:
            self.metadata[key] = value
    
    def reinforce(self, amount: float = 0.1) -> None:
        """
        Verstärkt die Relation durch Erhöhung des Gewichts und Aktualisierung der Metadaten
        
        Args:
            amount: Verstärkungsintensität
        """
        self.weight = min(1.0, self.weight + amount)
        self.metadata["reinforcement_count"] += 1
        self.metadata["last_reinforced"] = datetime.now()
    
    def decay(self, amount: float = 0.05) -> None:
        """
        Schwächt die Relation durch Verringerung des Gewichts
        
        Args:
            amount: Abschwächungsintensität
        """
        self.weight = max(0.01, self.weight - amount)
        
    def __str__(self) -> str:
        """String-Repräsentation für leichtes Debugging"""
        return f"Relation({self.id}, {self.source_id} -[{self.type}]-> {self.target_id}, weight={self.weight})"