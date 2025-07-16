class MetaboAPI:
    """
    Öffentliche API für externe Interaktion mit MetaboMind
    """
    def __init__(self, metabo_core: 'MetaboCore', config: MetaboConfig, logger: MetaboLogger):
        """
        Initialisiert die MetaboMind-API
        
        Args:
            metabo_core: MetaboCore-Instanz
            config: MetaboMind-Konfiguration
            logger: Logger
        """
        self.core = metabo_core
        self.config = config
        self.logger = logger
    
    def query(self, query_text: str) -> Dict[str, Any]:
        """
        Führt eine natürlichsprachliche Abfrage aus
        
        Args:
            query_text: Abfragetext
            
        Returns:
            Abfrageergebnisse
        """
        pass
    
    def add_knowledge(self, knowledge_text: str) -> Dict[str, Any]:
        """
        Fügt Wissen zum System hinzu
        
        Args:
            knowledge_text: Wissenstext
            
        Returns:
            Ergebnis der Wissensintegration
        """
        pass
    
    def get_concept_info(self, concept: str) -> Dict[str, Any]:
        """
        Holt Informationen zu einem Konzept
        
        Args:
            concept: Konzeptname
            
        Returns:
            Konzeptinformationen
        """
        pass
    
    def find_relationships(self, source: str, target: Optional[str] = None, max_depth: int = 3) -> Dict[str, Any]:
        """
        Findet Beziehungen zwischen Konzepten
        
        Args:
            source: Quellkonzept
            target: Optional, Zielkonzept
            max_depth: Maximale Suchtiefe
            
        Returns:
            Gefundene Beziehungen
        """
        pass
    
    def get_yin_yang_state(self) -> Dict[str, Any]:
        """
        Gibt den aktuellen Yin-Yang-Zustand zurück
        
        Returns:
            Yin-Yang-Statusinformationen
        """
        pass
    
    def get_entropy_info(self) -> Dict[str, Any]:
        """
        Gibt Entropieinformationen zurück
        
        Returns:
            Entropiestatistiken
        """
        pass
    
    def get_meta_reflection(self) -> Dict[str, Any]:
        """
        Gibt die aktuelle Meta-Bewusstseinsreflexion zurück
        
        Returns:
            Meta-Bewusstseinsreflexion
        """
        pass