"""Tkinter-based GUI for MetaboMind.

The GUI spawns worker threads so that expensive MetaboMind operations do not
block the Tk event loop.  Only user messages and the final LLM answer appear in
the chat window.  All intermediate data and debug output are organised in tabs.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from control.metabo_cycle import run_metabo_cycle
from control.takt_engine import run_metabotakt
from goals.goal_manager import get_active_goal, set_goal
from memory.memory_manager import get_memory_manager
import utils.llm_client as llm_client
from control.yin_yang_controller import current_mode


class MetaboGUI:
    """Simple interface wrapping the CLI functionality."""

    def __init__(self) -> None:
        llm_client.init_client()
        self.memory = get_memory_manager()

        self.root = tk.Tk()
        self.root.title("MetaboMind GUI")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_menu()

        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TButton", padding=6)

        self._build_layout()

    # Layout helpers -----------------------------------------------------
    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Graph speichern", command=self._save_graph)
        menubar.add_cascade(label="Datei", menu=file_menu)
        self.root.config(menu=menubar)

    # Layout helpers -----------------------------------------------------
    def _build_layout(self) -> None:
        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # Left: chat
        left_frame = tk.Frame(main_pane)
        main_pane.add(left_frame, width=500)

        self.chat = ScrolledText(left_frame, state=tk.DISABLED, wrap=tk.WORD)
        self.chat.pack(fill=tk.BOTH, expand=True)
        self.chat.tag_config("user", foreground="blue")
        self.chat.tag_config("system", foreground="green")

        input_frame = tk.Frame(left_frame)
        input_frame.pack(fill=tk.X)

        self.entry = tk.Entry(input_frame)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self._on_send)

        send_btn = tk.Button(input_frame, text="Senden", command=self._on_send)
        send_btn.pack(side=tk.RIGHT)

        # Right: notebook with tabs
        right_frame = tk.Frame(main_pane)
        main_pane.add(right_frame)

        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self._build_goals_tab()
        self._build_reflection_tab()
        self._build_status_tab()
        self._build_graph_tab()
        self._build_log_tab()
        self._build_takt_tab()

    def _build_goals_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Ziele")

        tk.Label(frame, text="Aktuelles Ziel:").pack(anchor=tk.W)
        self.goal_var = tk.StringVar(value=get_active_goal())
        tk.Label(frame, textvariable=self.goal_var, wraplength=200).pack(anchor=tk.W)

        tk.Label(frame, text="Subgoals:").pack(anchor=tk.W, pady=(10, 0))
        self.subgoal_box = ScrolledText(frame, height=5, state=tk.DISABLED)
        self.subgoal_box.pack(fill=tk.BOTH, expand=True)

        goal_entry = tk.Entry(frame)
        goal_entry.pack(fill=tk.X, pady=(5, 0))
        goal_entry.bind("<Return>", lambda e: self._set_goal(goal_entry.get()))

        set_btn = tk.Button(frame, text="Ziel setzen", command=lambda: self._set_goal(goal_entry.get()))
        set_btn.pack(pady=(0, 5))

    def _build_reflection_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Selbstreflexion")
        self.reflection_box = ScrolledText(frame, state=tk.DISABLED)
        self.reflection_box.pack(fill=tk.BOTH, expand=True)

    def _build_status_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Status")

        self.mode_var = tk.StringVar(value=current_mode().upper())
        self.emotion_var = tk.StringVar(value="-")
        self.delta_var = tk.StringVar(value="0")

        tk.Label(frame, text="Modus:").pack(anchor=tk.W)
        tk.Label(frame, textvariable=self.mode_var).pack(anchor=tk.W)
        tk.Label(frame, text="Emotion:").pack(anchor=tk.W, pady=(10, 0))
        tk.Label(frame, textvariable=self.emotion_var).pack(anchor=tk.W)
        tk.Label(frame, text="Δ-Entropie:").pack(anchor=tk.W, pady=(10, 0))
        tk.Label(frame, textvariable=self.delta_var).pack(anchor=tk.W)

    def _build_graph_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Wissensgraph")

        from interface.graph_viewer import GraphViewer

        self.graph_viewer = GraphViewer(frame, self.memory.graph.graph)
        self.graph_viewer.pack(fill=tk.BOTH, expand=True)
        self._update_graph_view()

        btn = tk.Button(frame, text="Aktualisieren", command=self._update_graph_view)
        btn.pack(pady=5)

        self.new_triplets_box = ScrolledText(frame, height=6, state=tk.DISABLED)
        self.new_triplets_box.pack(fill=tk.BOTH, expand=False)

    def _build_log_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Systemlog")
        self.log_box = ScrolledText(frame, state=tk.DISABLED)
        self.log_box.pack(fill=tk.BOTH, expand=True)
        self._load_log()

    def _build_takt_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Metabotakt")

        run_btn = tk.Button(frame, text="Takt ausführen", command=self._run_takt)
        run_btn.pack(pady=5)

        self.takt_goal_var = tk.StringVar(value="-")
        self.takt_emotion_var = tk.StringVar(value="-")
        self.takt_delta_var = tk.StringVar(value="0")

        tk.Label(frame, textvariable=self.takt_goal_var, wraplength=200).pack(anchor=tk.W)
        tk.Label(frame, text="Emotion:").pack(anchor=tk.W)
        tk.Label(frame, textvariable=self.takt_emotion_var).pack(anchor=tk.W)
        tk.Label(frame, text="Δ-Entropie:").pack(anchor=tk.W)
        tk.Label(frame, textvariable=self.takt_delta_var).pack(anchor=tk.W)

        tk.Label(frame, text="Reflexion:").pack(anchor=tk.W, pady=(10, 0))
        self.takt_reflection = ScrolledText(frame, height=5, state=tk.DISABLED)
        self.takt_reflection.pack(fill=tk.BOTH, expand=True)

    # Button actions -----------------------------------------------------
    def _set_goal(self, goal: str) -> None:
        goal = goal.strip()
        if not goal:
            return
        set_goal(goal)
        self.goal_var.set(goal)
        self._append_chat(f"[Neues Ziel gesetzt: {goal}]\n", "system")

    def _on_send(self, event=None) -> None:  # type: ignore[override]
        user_input = self.entry.get().strip()
        if not user_input:
            return
        self.entry.delete(0, tk.END)

        self._append_chat(f"Du: {user_input}\n", "user")
        thread = threading.Thread(target=self._cycle_thread, args=(user_input,), daemon=True)
        thread.start()

    def _run_takt(self) -> None:
        thread = threading.Thread(target=self._takt_thread, daemon=True)
        thread.start()

    # Update helpers ----------------------------------------------------
    def _append_chat(self, text: str, tag: str = "") -> None:
        self.chat.configure(state=tk.NORMAL)
        if tag:
            self.chat.insert(tk.END, text, tag)
        else:
            self.chat.insert(tk.END, text)
        self.chat.configure(state=tk.DISABLED)

    def _update_subgoals(self, subgoals: list[str]) -> None:
        self.subgoal_box.configure(state=tk.NORMAL)
        self.subgoal_box.delete("1.0", tk.END)
        for sg in subgoals:
            self.subgoal_box.insert(tk.END, f"- {sg}\n")
        self.subgoal_box.configure(state=tk.DISABLED)

    def _update_reflection(self, text: str) -> None:
        self.reflection_box.configure(state=tk.NORMAL)
        self.reflection_box.delete("1.0", tk.END)
        self.reflection_box.insert(tk.END, text)
        self.reflection_box.configure(state=tk.DISABLED)

    def _update_triplets(self, triplets) -> None:
        self.new_triplets_box.configure(state=tk.NORMAL)
        self.new_triplets_box.delete("1.0", tk.END)
        for t in triplets:
            self.new_triplets_box.insert(tk.END, f"{t}\n")
        self.new_triplets_box.configure(state=tk.DISABLED)
        self._update_graph_view()

    # Thread helpers ----------------------------------------------------
    def _cycle_thread(self, user_input: str) -> None:
        result = run_metabo_cycle(user_input)
        self.root.after(0, lambda: self._handle_cycle_result(user_input, result))

    def _handle_cycle_result(self, user_input: str, result: dict) -> None:
        self._append_chat(f"System: {result['reflection']}\n", "system")
        self.chat.see(tk.END)
        self.mode_var.set(current_mode().upper())
        self.goal_var.set(result['goal'])
        self._update_subgoals(result.get('subgoals', []))
        self._update_reflection(result['reflection'])
        self.emotion_var.set(result['emotion'])
        self.delta_var.set(f"{result['delta']:+.2f}")
        self._update_triplets(result.get('triplets', []))
        self._load_log()

    def _takt_thread(self) -> None:
        result = run_metabotakt()
        self.root.after(0, lambda: self._handle_takt_result(result))

    def _handle_takt_result(self, result: dict) -> None:
        self.goal_var.set(result["goal"])
        msg = result.get("goal_update", "")
        if msg:
            self._append_chat(f"[{msg}]\n", "system")
            self.takt_goal_var.set(msg)
        else:
            self.takt_goal_var.set(result["goal"])

        self.takt_emotion_var.set(f"{result['emotion']} ({result['intensity']})")
        self.takt_delta_var.set(f"{result['delta']:+.2f}")
        self.takt_reflection.configure(state=tk.NORMAL)
        self.takt_reflection.delete("1.0", tk.END)
        self.takt_reflection.insert(tk.END, result["reflection"])
        self.takt_reflection.configure(state=tk.DISABLED)
        self._load_log()
        self._update_graph_view()

    def _load_log(self) -> None:
        path = Path("data/metabo_log.jsonl")
        if not path.exists():
            return
        self.log_box.configure(state=tk.NORMAL)
        self.log_box.delete("1.0", tk.END)
        lines = path.read_text(encoding="utf-8").splitlines()[-100:]
        for line in lines:
            try:
                data = json.loads(line)
                self.log_box.insert(tk.END, json.dumps(data, ensure_ascii=False) + "\n")
            except json.JSONDecodeError:
                self.log_box.insert(tk.END, line + "\n")
        self.log_box.configure(state=tk.DISABLED)

    def _update_graph_view(self) -> None:
        try:
            self.graph_viewer.graph = self.memory.graph.graph
            self.graph_viewer.draw()
        except Exception as exc:  # pragma: no cover - visualisation is optional
            self._append_chat(
                f"[Graph konnte nicht geladen werden: {exc}]\n",
                "system",
            )

    def _save_graph(self) -> None:
        """Persist the knowledge graph and notify the user."""
        try:
            self.memory.graph.save_graph()
            self._append_chat("[Graph gespeichert]\n", "system")
        except Exception as exc:  # pragma: no cover - error handling
            self._append_chat(f"[Fehler beim Speichern: {exc}]\n", "system")

    def _on_close(self) -> None:
        """Save graph on window close."""
        self._save_graph()
        self.root.destroy()

    # Public API --------------------------------------------------------
    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    gui = MetaboGUI()
    gui.run()
