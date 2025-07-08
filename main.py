"""Command-line interface for MetaboMind."""
from __future__ import annotations

from metabo_cycle import run_metabo_cycle
from goal_manager import set_goal, get_active_goal


def print_help() -> None:
    """Display available CLI commands."""
    print("Verfügbare Befehle:")
    print("/quit  - Programm beenden")
    print("/ziel <Text> - neues Ziel setzen")
    print("/hilfe - diese Hilfe anzeigen")


def main() -> None:
    """Interactive loop processing user input via ``run_metabo_cycle``."""
    print("[MetaboMind CLI]")
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
        if user_input == "/hilfe":
            print_help()
            continue
        if user_input.startswith("/ziel"):
            new_goal = user_input[len("/ziel"):].strip()
            if not new_goal:
                print("[Bitte ein Ziel nach '/ziel' angeben.]")
            else:
                set_goal(new_goal)
                print(f"[Neues Ziel gespeichert: {new_goal}]")
            continue

        result = run_metabo_cycle(user_input)
        print("[Zyklus abgeschlossen]")
        print(f"Ziel: {result['goal']}")
        print(f"Antwort: {result['reflection']}")
        print(f"Emotion: {result['emotion']} (Δ={result['delta']:+.2f})")
        if result['triplets']:
            print(f"Neue Tripel: {result['triplets']}")


if __name__ == "__main__":
    main()
