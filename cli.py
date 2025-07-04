"""Kommandozeilenschnittstelle für MetaboMind.

Dieses Modul lädt den vorhandenen Speicher und Ziele und stellt dann eine
einfache Input‑Schleife bereit. Die Benutzereingaben werden an den
``MetaboKernel`` weitergereicht und die Antworten ausgegeben.
"""

from metabo_kernel import MetaboKernel
from graph_memory import GraphMemory
from llm_interface import LLMInterface
from emotion_engine import EmotionEngine
from prompt_manager import PromptManager
from goal_manager import GoalManager
from git_manager import GitManager
from repo_manager import RepoManager


def main():
    # persistent graph memory with optional archive for ausgelagerte Knoten
    memory = GraphMemory(archive_path="memory_archive.jsonl")
    try:
        memory.load("memory.json")
    except FileNotFoundError:
        pass
    # initialise subsystems
    emotion = EmotionEngine(memory)
    llm = LLMInterface()
    goals = GoalManager()
    try:
        goals.load("goals.json")
    except FileNotFoundError:
        pass
    prompt_manager = PromptManager(memory, emotion, goals)
    git_mgr = GitManager()
    repo_mgr = RepoManager()
    kernel = MetaboKernel(memory, llm, prompt_manager, goals, git_mgr, repo_mgr)

    # simple read‑eval‑print loop
    while True:
        try:
            msg = input("Du: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if msg.lower() in ("exit", "quit", "bye"):
            break
        # delegate message handling to the kernel
        resp = kernel.process_user_message(msg)
        if resp:
            print("Bot:", resp)
        # tick once per loop to allow autonomous messages
        tick_msg = kernel.tick()
        if tick_msg:
            print("Bot:", tick_msg)

    # persist current state on exit
    memory.save("memory.json")
    goals.save("goals.json")


if __name__ == "__main__":
    main()
