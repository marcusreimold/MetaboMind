class MetaboRESTAPI:
    """
    REST-API für MetaboMind
    """
    def __init__(self, metabo_api: MetaboAPI, config: MetaboConfig, logger: MetaboLogger):
        """
        Initialisiert die REST-API
        
        Args:
            metabo_api: MetaboAPI-Instanz
            config: MetaboMind-Konfiguration
            logger: Logger
        """
        self.api = metabo_api
        self.config = config
        self.logger = logger
    
    def start_server(self, host: str = "localhost", port: int = 8000) -> None:
        """
        Startet den REST-API-Server
        
        Args:
            host: Hostname
            port: Port
        """
        pass
    
    def stop_server(self) -> None:
        """Stoppt den REST-API-Server"""
        pass