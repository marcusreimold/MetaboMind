class GCNEncoder(nn.Module):
    """
    Graph Convolutional Network Encoder für Knotenembeddings
    """
    def __init__(self, input_dim: int, hidden_dim: int, embedding_dim: int):
        """
        Initialisiert den GCN-Encoder
        
        Args:
            input_dim: Eingangsdimension
            hidden_dim: Dimension der versteckten Schicht
            embedding_dim: Dimension der Ausgabeembeddings
        """
        super(GCNEncoder, self).__init__()
        self.conv1 = GCNConv(input_dim, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, embedding_dim)
    
    def forward(self, x, edge_index):
        """
        Forward-Pass durch das Netzwerk
        
        Args:
            x: Knotenfeatures
            edge_index: Kantenindizes
            
        Returns:
            Knotenembeddings
        """
        pass