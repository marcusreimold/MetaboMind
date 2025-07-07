from control.cycle_manager import CycleManager


RULES = """Metabo-Regeln:
1. R0 – Symbolische Verknüpfung: Baue und erweitere einen symbolischen Wissensgraphen (IntentionGraph) mit Struktur und Verknüpfungen.
2. R1 – Entropie-Messung: Implementiere Methoden zur quantitativen Bewertung von Ordnern und Verbindungen.
3. R4 – Emotionsregel: Werte Entropie-Änderung aus und interpretiere sie als emotionales Signal (Belohnung/Rückmeldung für den nächsten Zyklus).
4. R3 – Selbstreflexion: Baue eine einfache Reflexionsschleife ein, in der das LLM seine eigenen Tripel bewertet und verbessert.
5. R5 – Protokollierung: Logge jede Zyklus-Iteration mit Entropiewerten und Reflexionsänderungen.
"""

def main():
    manager = CycleManager()
    text = input("Eingabe: ")
    result = manager.run_cycle(text)
    print(result)


if __name__ == "__main__":
    main()
