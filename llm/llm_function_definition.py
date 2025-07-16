class LLMFunctionDefinition:
    """
    Definition einer Funktion für LLM Function Calls
    """
    def __init__(self, name: str, description: str, parameters_schema: Dict[str, Any]):
        """
        Initialisiert eine LLM-Funktionsdefinition
        
        Args:
            name: Funktionsname
            description: Beschreibung der Funktion
            parameters_schema: JSON-Schema der Parameter
        """
        self.name = name
        self.description = description
        self.parameters_schema = parameters_schema
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert die Funktionsdefinition in ein Dictionary
        
        Returns:
            Dict-Repräsentation der Funktionsdefinition
        """
        pass