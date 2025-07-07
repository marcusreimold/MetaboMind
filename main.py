from control.cycle_manager import CycleManager
from logs.logger import MetaboLogger


def main() -> None:
    """Interactive command loop for MetaboMind."""
    manager = CycleManager(logger=MetaboLogger())
    pending_input = ""
    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[MetaboMind wird beendet.]")
            break

        if not user_input:
            continue

        if user_input == "/quit":
            print("[MetaboMind wird beendet.]")
            break

        if user_input == "/takt":
            if not pending_input:
                print("[Keine Eingabe gespeichert.]")
                continue
            print("[Zyklus gestartet...]")
            res = manager.run_cycle(pending_input)
            print(f"Entropie vorher: {res['entropy_before']:.2f}")
            print(f"Entropie nachher: {res['entropy_after']:.2f}")
            print(
                f"Δ: {res['delta']:+.2f} → Emotion: {res['emotion']} ({res['intensity']})"
            )
            print(f"Reflexion: {res['reflection']}")
            if res["triplets"]:
                print(f"Triplets: {res['triplets']}")
            pending_input = ""
            continue

        pending_input = user_input
        print("[Eingabe gespeichert. Verwende '/takt' für Analyse.]")


if __name__ == "__main__":
    main()
