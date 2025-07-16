class LinkPredictor(nn.Module):
    """
    Link-Prediction-Modell für die Vorhersage fehlender Verbindungen
    """
    def __init__(self, embedding_dim: int):
        """
        Initialisiert den Link Predictor
        
        Args:
            embedding_dim: Dimension der Knotenembeddings
        """
        super(LinkPredictor, self).__init__()
        self.fc1 = nn.Linear(embedding_dim * 2, embedding_dim)
        self.fc2 = nn.Linear(embedding_dim, 1)
    
    def forward(self, z, edge_index_i, edge_index_j):
        """
        Forward-Pass durch das Netzwerk
        
        Args:
            z: Knotenembeddings
            edge_index_i: Quellknotenindizes
            edge_index_j: Zielknotenindizes
            
        Returns:
            Link-Wahrscheinlichkeiten
        """
        pass