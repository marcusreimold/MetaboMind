"""Tk-basierte Benutzerschnittstelle für MetaboMind."""

import tkinter as tk
from tkinter import ttk
from tkinter import font
from metabo_kernel import MetaboKernel
from graph_memory import GraphMemory
from emotion_engine import EmotionEngine
from llm_interface import LLMInterface
from prompt_manager import PromptManager
from goal_manager import GoalManager
from git_manager import GitManager
from repo_manager import RepoManager
import networkx as nx
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

class UIManager(tk.Tk):
    def __init__(self, kernel: MetaboKernel, emotion_engine: EmotionEngine, memory: GraphMemory, goal_manager: GoalManager):
        super().__init__()
        # build dark themed window with chat on the left and diagnostic tabs on the right
        self.title("MetaboMind")
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        dark_bg = "#2b2b2b"
        dark_fg = "#dddddd"
        style.configure("TFrame", background=dark_bg)
        style.configure("TLabel", background=dark_bg, foreground=dark_fg)
        style.configure("TButton", background="#444444", foreground=dark_fg)
        style.configure("TNotebook", background=dark_bg)
        style.configure("TNotebook.Tab", background="#444444", foreground=dark_fg)

        self.configure(bg=dark_bg)
        self.kernel = kernel
        self.emotion_engine = emotion_engine
        self.memory = memory
        self.goals = goal_manager

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        chat_frame = ttk.Frame(self)
        chat_frame.grid(row=0, column=0, sticky="nsew")
        chat_frame.rowconfigure(0, weight=1)
        chat_frame.columnconfigure(0, weight=1)

        self.chat_display = tk.Text(chat_frame, state="disabled", wrap="word", bg="#1e1e1e", fg="#dddddd", insertbackground="white")
        chat_scroll = ttk.Scrollbar(chat_frame, orient="vertical", command=self.chat_display.yview)
        self.chat_display.configure(yscrollcommand=chat_scroll.set)
        default_font = font.nametofont("TkDefaultFont")
        code_font = font.Font(family="Courier", size=10)
        self.chat_display.tag_configure("code", background="#333333", foreground="#d7ba7d", font=code_font)
        self.chat_display.tag_configure("bold", font=(default_font.cget("family"), default_font.cget("size"), "bold"))
        self.chat_display.grid(row=0, column=0, columnspan=2, sticky="nsew")
        chat_scroll.grid(row=0, column=2, sticky="ns")

        self.msg_entry = ttk.Entry(chat_frame)
        self.msg_entry.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.msg_entry.bind("<Return>", lambda _e: self.send_message())
        send_btn = ttk.Button(chat_frame, text="Senden", command=self.send_message)
        send_btn.grid(row=1, column=1, sticky="e", padx=5, pady=5)

        self.status_var = tk.StringVar(value="Emotion: neutral, Entropie: 0.0")
        status_label = ttk.Label(chat_frame, textvariable=self.status_var)
        status_label.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.emotion_bar = ttk.Progressbar(chat_frame, maximum=1.0)
        self.emotion_bar.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5)
        save_btn = ttk.Button(chat_frame, text="Speichern", command=self._save)
        save_btn.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=2)

        # periodic update of diagnostics
        self.after(1000, self._tick)

        notebook = ttk.Notebook(self)
        notebook.grid(row=0, column=1, sticky="nsew")

        tab_takt = ttk.Frame(notebook)
        tab_semantic = ttk.Frame(notebook)
        tab_episode = ttk.Frame(notebook)
        tab_search = ttk.Frame(notebook)
        tab_graph = ttk.Frame(notebook)
        tab_analysis = ttk.Frame(notebook)
        tab_stats = ttk.Frame(notebook)
        tab_entropy = ttk.Frame(notebook)
        tab_goals = ttk.Frame(notebook)
        tab_repo = ttk.Frame(notebook)

        notebook.add(tab_takt, text="Metabo-Takt")
        notebook.add(tab_semantic, text="Semantischer Speicher")
        notebook.add(tab_episode, text="Episodenspeicher")
        notebook.add(tab_search, text="Suche")
        notebook.add(tab_graph, text="Graph")
        notebook.add(tab_analysis, text="Analyse")
        notebook.add(tab_stats, text="Statistik")
        notebook.add(tab_entropy, text="Entropieverlauf")
        notebook.add(tab_goals, text="Ziele")
        notebook.add(tab_repo, text="Repository")

        self.takt_text = tk.Text(tab_takt, state="disabled", wrap="word", bg="#1e1e1e", fg="#dddddd")
        ttk.Scrollbar(tab_takt, orient="vertical", command=self.takt_text.yview).pack(side="right", fill="y")
        self.takt_text.pack(side="left", expand=True, fill="both")

        self.semantic_text = tk.Text(tab_semantic, state="disabled", wrap="word", bg="#1e1e1e", fg="#dddddd")
        ttk.Scrollbar(tab_semantic, orient="vertical", command=self.semantic_text.yview).pack(side="right", fill="y")
        self.semantic_text.pack(side="left", expand=True, fill="both")

        self.episode_text = tk.Text(tab_episode, state="disabled", wrap="word", bg="#1e1e1e", fg="#dddddd")
        ttk.Scrollbar(tab_episode, orient="vertical", command=self.episode_text.yview).pack(side="right", fill="y")
        self.episode_text.pack(side="left", expand=True, fill="both")

        search_frame = ttk.Frame(tab_search)
        search_frame.pack(expand=True, fill="both")
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="top", fill="x", padx=5, pady=5)
        btn_row = ttk.Frame(search_frame)
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="Memory", command=self._search_memory).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Archive", command=self._search_archive).pack(side="left", padx=5)
        ttk.Label(btn_row, text="Pfad:").pack(side="left", padx=5)
        self.path_entry1 = ttk.Entry(btn_row, width=10)
        self.path_entry1.pack(side="left")
        self.path_entry2 = ttk.Entry(btn_row, width=10)
        self.path_entry2.pack(side="left")
        ttk.Button(btn_row, text="Suchen", command=self._search_path).pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda _e: self._search_memory())
        self.search_text = tk.Text(search_frame, state="disabled", wrap="word", bg="#1e1e1e", fg="#dddddd")
        ttk.Scrollbar(search_frame, orient="vertical", command=self.search_text.yview).pack(side="right", fill="y")
        self.search_text.pack(side="left", expand=True, fill="both")

        self.graph_fig = Figure(figsize=(4, 3))
        self.graph_ax = self.graph_fig.add_subplot(111)
        self.graph_canvas = FigureCanvasTkAgg(self.graph_fig, master=tab_graph)
        self.graph_canvas.get_tk_widget().pack(expand=True, fill="both")
        ttk.Button(tab_graph, text="Export", command=self._export_graph).pack(pady=5)

        self.ent_fig = Figure(figsize=(4, 3))
        self.ent_ax = self.ent_fig.add_subplot(111)
        self.ent_canvas = FigureCanvasTkAgg(self.ent_fig, master=tab_entropy)
        self.ent_canvas.get_tk_widget().pack(expand=True, fill="both")

        self.central_text = tk.Text(tab_analysis, state="disabled", height=6, wrap="word", bg="#1e1e1e", fg="#dddddd")
        ttk.Scrollbar(tab_analysis, orient="vertical", command=self.central_text.yview).pack(side="right", fill="y")
        self.central_text.pack(side="top", expand=True, fill="both")

        ttk.Label(tab_analysis, text="Top-Wörter").pack(anchor="w")
        self.words_text = tk.Text(tab_analysis, state="disabled", height=6, wrap="word", bg="#1e1e1e", fg="#dddddd")
        ttk.Scrollbar(tab_analysis, orient="vertical", command=self.words_text.yview).pack(side="right", fill="y")
        self.words_text.pack(side="top", expand=True, fill="both")

        self.stats_text = tk.Text(tab_stats, state="disabled", wrap="word", bg="#1e1e1e", fg="#dddddd")
        ttk.Scrollbar(tab_stats, orient="vertical", command=self.stats_text.yview).pack(side="right", fill="y")
        self.stats_text.pack(side="left", expand=True, fill="both")

        goals_frame = ttk.Frame(tab_goals)
        goals_frame.pack(expand=True, fill="both")
        entry_frame = ttk.Frame(goals_frame)
        entry_frame.pack(fill="x")
        self.goal_entry = ttk.Entry(entry_frame)
        self.goal_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.goal_entry.bind("<Return>", lambda _e: self._add_goal())
        ttk.Button(entry_frame, text="Hinzufügen", command=self._add_goal).pack(side="left", padx=5)

        lists_frame = ttk.Frame(goals_frame)
        lists_frame.pack(expand=True, fill="both")

        self.goal_list = tk.Listbox(lists_frame)
        self.goal_list.pack(side="left", expand=True, fill="both", padx=5, pady=5)
        self.goal_list.bind("<Double-Button-1>", lambda _e: self._complete_goal())

        self.completed_list = tk.Listbox(lists_frame)
        self.completed_list.pack(side="left", expand=True, fill="both", padx=5, pady=5)

        btn_frame = ttk.Frame(goals_frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Als erledigt", command=self._complete_goal).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Entfernen", command=self._remove_goal).pack(side="left", padx=5)

        # show existing goals
        self._update_goals_text()

        # repository tab elements
        repo_output = ttk.Frame(tab_repo)
        repo_output.pack(fill="x")
        self.repo_text = tk.Text(repo_output, state="disabled", height=6, wrap="word", bg="#1e1e1e", fg="#dddddd")
        ttk.Scrollbar(repo_output, orient="vertical", command=self.repo_text.yview).pack(side="right", fill="y")
        self.repo_text.pack(side="left", expand=True, fill="both")

        repo_btns = ttk.Frame(tab_repo)
        repo_btns.pack(fill="x")
        ttk.Button(repo_btns, text="Analyse", command=self._analyse_repo).pack(side="left", padx=5, pady=5)
        ttk.Button(repo_btns, text="Test", command=self._test_repo).pack(side="left", padx=5, pady=5)
        ttk.Button(repo_btns, text="Tests", command=self._run_tests).pack(side="left", padx=5, pady=5)
        ttk.Button(repo_btns, text="Status", command=self._git_status).pack(side="left", padx=5, pady=5)
        ttk.Button(repo_btns, text="Diff", command=self._git_diff).pack(side="left", padx=5, pady=5)
        self.commit_entry = ttk.Entry(repo_btns)
        self.commit_entry.pack(side="left", expand=True, fill="x", padx=5)
        ttk.Button(repo_btns, text="Commit", command=self._git_commit).pack(side="left", padx=5)
        ttk.Button(repo_btns, text="Patch", command=self._open_patch_window).pack(side="left", padx=5)
        self.grep_entry = ttk.Entry(repo_btns)
        self.grep_entry.pack(side="left", expand=True, fill="x", padx=5)
        ttk.Button(repo_btns, text="Grep", command=self._grep_repo).pack(side="left", padx=5)

        file_ops = ttk.Frame(tab_repo)
        file_ops.pack(fill="x", pady=5)
        self.file_path = ttk.Entry(file_ops)
        self.file_path.pack(side="left", expand=True, fill="x", padx=5)
        ttk.Button(file_ops, text="Read", command=self._read_file).pack(side="left", padx=5)
        ttk.Button(file_ops, text="Save", command=self._write_file).pack(side="left", padx=5)
        ttk.Button(file_ops, text="Run", command=self._run_file).pack(side="left", padx=5)
        ttk.Button(file_ops, text="List", command=self._list_dir).pack(side="left", padx=5)

        file_frame = ttk.Frame(tab_repo)
        file_frame.pack(fill="both", expand=True)
        self.repo_file_text = tk.Text(file_frame, wrap="word", bg="#1e1e1e", fg="#dddddd")
        ttk.Scrollbar(file_frame, orient="vertical", command=self.repo_file_text.yview).pack(side="right", fill="y")
        self.repo_file_text.pack(side="left", expand=True, fill="both")

    def send_message(self):
        msg = self.msg_entry.get().strip()
        if not msg:
            return
        self.msg_entry.delete(0, tk.END)
        self.append_chat(f"Du: {msg}")
        placeholder_index = self.append_chat("Bot: ...")
        threading.Thread(
            target=self._process_message, args=(msg, placeholder_index), daemon=True
        ).start()

    def _process_message(self, msg: str, index: str):
        response = self.kernel.process_user_message(msg)
        self.after(
            0,
            lambda: self._finalize_message(msg, response, index),
        )

    def _finalize_message(self, msg: str, response: str, index: str):
        self.chat_display.configure(state="normal")
        self.chat_display.delete(index, f"{index} lineend")
        if response:
            self._insert_markdown(self.chat_display, f"Bot: {response}")
        self.chat_display.configure(state="disabled")
        if response:
            self.chat_display.see(tk.END)
        self.update_diagnostics(msg, response or "")

    def append_chat(self, text: str) -> str:
        """Append markdown-formatted text and return index."""
        self.chat_display.configure(state="normal")
        index = self.chat_display.index(tk.END)
        self._insert_markdown(self.chat_display, text)
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see(tk.END)
        return index

    def update_diagnostics(self, msg: str, response: str):
        self.takt_text.configure(state="normal")
        self.takt_text.insert(tk.END, f"Letzte Nachricht: {msg}\n")
        self.takt_text.configure(state="disabled")

        self.semantic_text.configure(state="normal")
        self.semantic_text.insert(tk.END, f"Antwort: {response}\n")
        self.semantic_text.configure(state="disabled")

        self.episode_text.configure(state="normal")
        self.episode_text.insert(tk.END, f"Entropie: {self.memory.entropy():.2f}\n")
        self.episode_text.configure(state="disabled")

        self.central_text.configure(state="normal")
        self.central_text.delete("1.0", tk.END)
        for idx, data, score in self.memory.centrality():
            txt = data.get("text", "")[:30].replace("\n", " ")
            self.central_text.insert(tk.END, f"{idx}: {score:.2f} {txt}\n")
        self.central_text.configure(state="disabled")

        self.words_text.configure(state="normal")
        self.words_text.delete("1.0", tk.END)
        for word, count in self.memory.top_words():
            self.words_text.insert(tk.END, f"{word}: {count}\n")
        self.words_text.configure(state="disabled")

        stats = self.memory.stats()
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", tk.END)
        for key, val in stats.items():
            self.stats_text.insert(tk.END, f"{key}: {val}\n")
        self.stats_text.configure(state="disabled")

        self._update_goals_text()

        emotion = self.emotion_engine.evaluate()
        intensity = self.emotion_engine.intensity()
        goal = self.goals.active_goal() or "-"
        self.status_var.set(
            f"Emotion: {emotion} ({intensity:.2f}), Entropie: {self.memory.entropy():.2f}, Ziel: {goal}"
        )
        self.emotion_bar['value'] = intensity
        self.emotion_bar['value'] = intensity

    def update_status(self):
        emotion = self.emotion_engine.evaluate()
        intensity = self.emotion_engine.intensity()
        goal = self.goals.active_goal() or "-"
        self.status_var.set(
            f"Emotion: {emotion} ({intensity:.2f}), Entropie: {self.memory.entropy():.2f}, Ziel: {goal}"
        )

    def draw_graph(self):
        self.graph_ax.clear()
        G = self.memory.graph
        if G.number_of_nodes() == 0:
            self.graph_canvas.draw()
            return
        pos = nx.spring_layout(G)
        labels = {n: G.nodes[n].get("role", str(n)) for n in G.nodes()}
        self.graph_fig.patch.set_facecolor("#2b2b2b")
        self.graph_ax.set_facecolor("#2b2b2b")
        nx.draw_networkx(
            G,
            pos,
            labels=labels,
            ax=self.graph_ax,
            node_size=300,
            font_size=8,
            node_color="#1f78b4",
            edge_color="#888888",
            font_color="#ffffff",
        )
        self.graph_ax.set_axis_off()
        self.graph_canvas.draw()

    def draw_entropy(self):
        self.ent_ax.clear()
        history = self.memory.entropy_history()
        if history:
            start = history[0][0]
            xs = [t - start for t, _ in history]
            ys = [e for _, e in history]
            self.ent_ax.plot(xs, ys, color="cyan")
        self.ent_ax.set_xlabel("Zeit (s)")
        self.ent_ax.set_ylabel("Entropie")
        self.ent_canvas.draw()

    def _tick(self):
        """Periodic updates to diagnostic tabs."""
        # called every second via ``after``; also triggers kernel tick
        output = self.kernel.tick()
        if output:
            self.append_chat(f"Bot: {output}")
        self.update_status()
        self._update_goals_text()
        self.draw_graph()
        self.draw_entropy()
        # autosave memory and goals periodically
        self.memory.autosave("memory.json")
        self.goals.autosave("goals.json")
        self.central_text.configure(state="normal")
        self.central_text.delete("1.0", tk.END)
        for idx, data, score in self.memory.centrality():
            txt = data.get("text", "")[:30].replace("\n", " ")
            self.central_text.insert(tk.END, f"{idx}: {score:.2f} {txt}\n")
        self.central_text.configure(state="disabled")
        self.words_text.configure(state="normal")
        self.words_text.delete("1.0", tk.END)
        for word, count in self.memory.top_words():
            self.words_text.insert(tk.END, f"{word}: {count}\n")
        self.words_text.configure(state="disabled")

        stats = self.memory.stats()
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", tk.END)
        for key, val in stats.items():
            self.stats_text.insert(tk.END, f"{key}: {val}\n")
        self.stats_text.configure(state="disabled")
        self.after(1000, self._tick)

    def _add_goal(self):
        text = self.goal_entry.get().strip()
        if not text:
            return
        self.goal_entry.delete(0, tk.END)
        self.goals.add_goal(text)
        self._update_goals_text()

    def _complete_goal(self):
        sel = self.goal_list.curselection()
        if not sel:
            return
        self.goals.complete_goal(sel[0])
        self._update_goals_text()

    def _remove_goal(self):
        sel = self.goal_list.curselection()
        if not sel:
            return
        self.goals.remove_goal(sel[0])
        self._update_goals_text()

    def _save(self):
        self.memory.save("memory.json")
        self.goals.save("goals.json")

    def _update_goals_text(self):
        self.goal_list.delete(0, tk.END)
        for g in self.goals.goals:
            self.goal_list.insert(tk.END, g["text"])
        self.completed_list.delete(0, tk.END)
        for g in self.goals.completed:
            self.completed_list.insert(tk.END, g["text"])

    def _search_memory(self):
        query = self.search_entry.get().strip()
        if not query:
            return
        results = self.memory.search_messages(query)
        self.search_text.configure(state="normal")
        self.search_text.delete("1.0", tk.END)
        for idx, data in results:
            self.search_text.insert(tk.END, f"{idx}: {data['text']}\n")
        self.search_text.configure(state="disabled")

    def _search_archive(self):
        query = self.search_entry.get().strip()
        if not query:
            return
        results = self.memory.search_archive(query)
        self.search_text.configure(state="normal")
        self.search_text.delete("1.0", tk.END)
        for entry in results:
            self.search_text.insert(tk.END, f"{entry.get('id')}: {entry.get('text')}\n")
        if not results:
            self.search_text.insert(tk.END, "Keine Treffer\n")
        self.search_text.configure(state="disabled")

    def _search_path(self):
        w1 = self.path_entry1.get().strip()
        w2 = self.path_entry2.get().strip()
        if not w1 or not w2:
            return
        result = self.kernel.memory_shortest_path(w1, w2)
        self.search_text.configure(state="normal")
        self.search_text.delete("1.0", tk.END)
        self.search_text.insert("1.0", result + "\n")
        self.search_text.configure(state="disabled")

    def _analyse_repo(self):
        result = self.kernel.repo_analyze()
        self._append_repo(result)

    def _test_repo(self):
        result = self.kernel.repo_test()
        self._append_repo(result)

    def _run_tests(self):
        result = self.kernel.repo_run_tests()
        self._append_repo(result)

    def _git_status(self):
        result = self.kernel.git_status()
        self._append_repo(result)

    def _git_diff(self):
        result = self.kernel.git_diff()
        self._append_repo(result)

    def _grep_repo(self):
        pattern = self.grep_entry.get().strip()
        if not pattern:
            return
        result = self.kernel.repo_grep(pattern)
        self._append_repo(result)

    def _open_patch_window(self):
        win = tk.Toplevel(self)
        win.title("Patch anwenden")
        text = tk.Text(win, wrap="word", bg="#1e1e1e", fg="#dddddd", insertbackground="white")
        text.pack(expand=True, fill="both")
        ttk.Button(win, text="Anwenden", command=lambda: self._apply_patch(text.get("1.0", "end-1c"), win)).pack(pady=5)

    def _apply_patch(self, patch: str, win=None):
        if not patch.strip():
            return
        result = self.kernel.repo_apply_patch(patch)
        self._append_repo(result)
        if win is not None:
            win.destroy()

    def _git_commit(self):
        msg = self.commit_entry.get().strip() or "Auto-Commit"
        result = self.kernel.git_commit(msg)
        self._append_repo(result)

    def _append_repo(self, text: str):
        self.repo_text.configure(state="normal")
        self._insert_markdown(self.repo_text, text)
        self.repo_text.insert(tk.END, "\n")
        self.repo_text.configure(state="disabled")
        self.repo_text.see(tk.END)

    def _read_file(self):
        path = self.file_path.get().strip()
        if not path:
            return
        content = self.kernel.repo_read_file(path)
        self.repo_file_text.delete("1.0", tk.END)
        self.repo_file_text.insert("1.0", content)

    def _write_file(self):
        path = self.file_path.get().strip()
        if not path:
            return
        content = self.repo_file_text.get("1.0", "end-1c")
        result = self.kernel.repo_write_file(path, content)
        self._append_repo(result)

    def _run_file(self):
        path = self.file_path.get().strip()
        if not path:
            return
        result = self.kernel.repo_run_python(path)
        self._append_repo(result)

    def _export_graph(self):
        path = "graph.png"
        self.kernel.memory_export_graph(path)
        self._append_repo(f"Graph exportiert nach {path}")

    def _list_dir(self):
        path = self.file_path.get().strip() or '.'
        result = self.kernel.repo_list_dir(path)
        if isinstance(result, list):
            result = '\n'.join(result)
        self._append_repo(result)

    def _insert_markdown(self, widget: tk.Text, text: str):
        """Very small subset of Markdown rendering."""
        # supports ``**bold**`` and `````code````` sections
        parts = text.split('```')
        code = False
        for part in parts:
            if code:
                widget.insert(tk.END, part, ("code",))
            else:
                while '**' in part:
                    before, star, rest = part.partition('**')
                    widget.insert(tk.END, before)
                    if '**' in rest:
                        bold, star2, part = rest.partition('**')
                        widget.insert(tk.END, bold, ("bold",))
                    else:
                        widget.insert(tk.END, star + rest)
                        part = ''
                widget.insert(tk.END, part)
            code = not code


def main():
    # load persisted state and start the UI
    memory = GraphMemory(archive_path="memory_archive.jsonl")
    try:
        memory.load("memory.json")
    except FileNotFoundError:
        pass
    emotion = EmotionEngine(memory)
    # Use dummy key placeholder; replace with real API key for actual usage
    llm = LLMInterface(api_key="YOUR_OPENAI_API_KEY")  # API-Schlüssel anpassen
    goals = GoalManager()
    try:
        goals.load("goals.json")
    except FileNotFoundError:
        pass
    prompt_manager = PromptManager(memory, emotion, goals)
    git_mgr = GitManager()
    repo_mgr = RepoManager()
    kernel = MetaboKernel(memory, llm, prompt_manager, goals, git_mgr, repo_mgr)
    app = UIManager(kernel, emotion, memory, goals)

    def on_close():
        memory.save("memory.json")
        goals.save("goals.json")
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_close)
    app.mainloop()

if __name__ == "__main__":
    main()
