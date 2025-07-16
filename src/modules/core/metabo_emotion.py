@dataclass
class MetaboEmotion:
    """Repräsentation einer MetaboMind-'Emotion'"""
    name: str                  # Name der Emotion
    valence: float             # Positiv/Negativ (-1.0 bis 1.0)
    intensity: float           # Intensität (0.0 bis 1.0)
    source: str                # Quelle/Grund für die Emotion
    timestamp: datetime        # Zeitpunkt der Emotion