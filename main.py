"""Entry point for MetaboMind launching the Tkinter GUI."""
from __future__ import annotations

from control.metabo_cycle import run_metabo_cycle
from control.takt_engine import run_metabotakt
from goals.goal_manager import set_goal
from goals.goal_updater import update_goal
from interface.metabo_gui import MetaboGUI
import llm_client
from memory_manager import get_memory_manager


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
        if user_input == "/takt":
            result = run_metabotakt()
            print("[Metabotakt ausgeführt]")
            if result["goal_update"]:
                print(result["goal_update"])
            print(f"ΔE: {result['delta']:+.2f} -> {result['emotion']} ({result['intensity']})")
            print(f"Reflexion: {result['reflection']}")
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
        new_goal = update_goal(
            user_input=user_input,
            last_goal=result.get("goal", ""),
            last_reflection=result.get("reflection", ""),
            triplets=result.get("triplets", []),
        )
        set_goal(new_goal)
        print("[Zyklus abgeschlossen]")
        print(f"Aktuelles Ziel: {new_goal}")
        print(f"Antwort: {result['reflection']}")
        print(f"Emotion: {result['emotion']} (Δ={result['delta']:+.2f})")
        if result['triplets']:
            print(f"Neue Tripel: {result['triplets']}")


if __name__ == "__main__":
    llm_client.init_client()
    get_memory_manager()
    gui = MetaboGUI()
    gui.run()
