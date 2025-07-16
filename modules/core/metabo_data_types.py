from enum import Enum


class MetaboState(Enum):
    """Diskrete Zustände des MetaboMind-Systems"""
    STRONG_YANG = 0
    YANG = 1
    BALANCED = 2
    YIN = 3
    STRONG_YIN = 4


class MetaboEvent(Enum):
    """Ereignistypen im MetaboMind-System"""
    ENTROPY_CHANGE = "entropy_change"
    YIN_YANG_CHANGE = "yin_yang_change"
    KNOWLEDGE_ADDED = "knowledge_added"
    KNOWLEDGE_REMOVED = "knowledge_removed"
    GRAPH_CONSOLIDATED = "graph_consolidated"
    GRAPH_EXPANDED = "graph_expanded"
    REFLECTION_COMPLETE = "reflection_complete"
    ERROR = "error"