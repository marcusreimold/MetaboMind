"""Entry point for MetaboMind launching the Tkinter GUI."""
from __future__ import annotations

from control.metabo_engine import run_metabo_cycle, metabo_tick
from goals.goal_manager import set_goal
from goals.goal_updater import update_goal
from interface.metabo_gui import MetaboGUI
import utils.llm_client as llm_client
from memory.memory_manager import get_memory_manager
from control.yin_yang_controller import current_mode


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
            result = metabo_tick()
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

        result = run_metabo_cycle(user_input, source_type="user")
        new_goal = update_goal(
            user_input=user_input,
            last_goal=result.get("goal", ""),
            last_reflection=result.get("reflection", ""),
            triplets=result.get("triplets", []),
        )
        set_goal(new_goal)
        print("[Zyklus abgeschlossen]")
        print(f"[Modus: {current_mode().upper()}]")
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
