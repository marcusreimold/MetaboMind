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
        """
        Konvertiert die Relation in ein Dictionary
        
        Returns:
            Dict-Repräsentation der Relation
        """
        pass
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetaboRelation':
        """
        Erstellt eine Relation aus einem Dictionary
        
        Args:
            data: Dictionary mit Relationsdaten
            
        Returns:
            Erstellte MetaboRelation
        """
        pass
    
    def update_metadata(self, key: str, value: Any) -> None:
        """
        Aktualisiert einen Metadatenwert
        
        Args:
            key: Metadatenschlüssel
            value: Neuer Wert
        """
        pass
    
    def reinforce(self, amount: float = 0.1) -> None:
        """
        Verstärkt die Relation durch Erhöhung des Gewichts und Aktualisierung der Metadaten
        
        Args:
            amount: Verstärkungsintensität
        """
        pass
    
    def decay(self, amount: float = 0.05) -> None:
        """
        Schwächt die Relation durch Verringerung des Gewichts
        
        Args:
            amount: Abschwächungsintensität
        """
        pass