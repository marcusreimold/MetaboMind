"""Zentrale Steuerungseinheit von MetaboMind."""

from context_selector import ContextSelector
from goal_manager import GoalManager
from git_manager import GitManager
from repo_manager import RepoManager
import time
import threading

class MetaboKernel:
    """Kernel orchestrating memory, prompt building and LLM calls."""
    def __init__(
        self,
        memory,
        llm,
        prompt_manager,
        goal_manager: GoalManager,
        git_manager: GitManager | None = None,
        repo_manager: RepoManager | None = None,
    ):
        # core components
        self.memory = memory
        self.llm = llm
        self.prompt_manager = prompt_manager
        self.goals = goal_manager
        # optional helpers for repository and git operations
        self.git = git_manager
        self.repo = repo_manager
        # timestamp of last reflection tick
        self.last_tick = time.time()
        self.lock = threading.Lock()
        # store messages that should be displayed to the user
        self.pending_outputs: list[str] = []

    def process_user_message(self, message: str) -> str:
        """Handle a user message and return the assistant response."""
        lower = message.lower()
        # direct command handling without LLM involvement
        if lower.startswith("git") and self.git:
            cmd = message.split(None, 1)[1] if " " in message else message.split(":", 1)[1]
            response = self.git.execute(cmd)
            self.memory.add_message(message, role="user")
            self.memory.add_message(response, role="assistant")
            return response
        if lower.startswith("run ") and self.repo:
            path = message.split(None, 1)[1]
            response = self.repo.run_python(path)
            self.memory.add_message(message, role="user")
            self.memory.add_message(response, role="assistant")
            return response
        if lower.startswith("read ") and self.repo:
            path = message.split(None, 1)[1]
            try:
                text = self.repo.read_file(path)
            except Exception as exc:
                text = f"Fehler: {exc}"
            self.memory.add_message(message, role="user")
            self.memory.add_message(text, role="assistant")
            return text
        if lower.startswith("write ") and self.repo:
            parts = message.split("\n", 1)
            path = parts[0].split(None, 1)[1]
            content = parts[1] if len(parts) > 1 else ""
            try:
                self.repo.write_file(path, content)
                text = "Datei gespeichert"
            except Exception as exc:
                text = f"Fehler: {exc}"
            self.memory.add_message(message, role="user")
            self.memory.add_message(text, role="assistant")
            return text
        if lower.startswith("patch") and self.repo:
            parts = message.split("\n", 1)
            patch = parts[1] if len(parts) > 1 else ""
            result = self.repo.apply_patch(patch)
            self.memory.add_message(message, role="user")
            self.memory.add_message(result, role="assistant")
            return result
        if lower.startswith("test") and self.repo:
            result = self.repo.compile_repo()
            self.memory.add_message(message, role="user")
            self.memory.add_message(result, role="assistant")
            return result
        if lower.startswith("tests") and self.repo:
            result = self.repo.run_tests()
            self.memory.add_message(message, role="user")
            self.memory.add_message(result, role="assistant")
            return result
        if lower.startswith("analyse") and self.repo:
            result = self.repo.analyze_repo()
            self.memory.add_message(message, role="user")
            self.memory.add_message(result, role="assistant")
            return result
        if lower.startswith("grep ") and self.repo:
            pattern = message.split(None, 1)[1]
            result = self.repo.grep(pattern)
            self.memory.add_message(message, role="user")
            self.memory.add_message(result, role="assistant")
            return result
        if lower.startswith("path ") or lower.startswith("pfad "):
            parts = message.split()
            if len(parts) < 3:
                text = "Format: path <wort1> <wort2>"
            else:
                word1, word2 = parts[1], parts[2]
                path = self.memory.shortest_path(word1, word2)
                if not path:
                    text = "Kein Pfad gefunden"
                else:
                    text = " -> ".join(f"{n}:{t[:20]}" for n, t in path)
            self.memory.add_message(message, role="user")
            self.memory.add_message(text, role="assistant")
            return text
        if lower.startswith("export"):
            path = message.split(None, 1)[1] if " " in message else "graph.png"
            self.memory.export_png(path)
            text = f"Graph gespeichert unter {path}"
            self.memory.add_message(message, role="user")
            self.memory.add_message(text, role="assistant")
            return text
        if lower.startswith("archive ") or lower.startswith("archiv "):
            query = message.split(None, 1)[1]
            results = self.memory.search_archive(query)
            text = "\n".join(f"{r.get('id')}: {r.get('text')}" for r in results) or "Keine Treffer"
            self.memory.add_message(message, role="user")
            self.memory.add_message(text, role="assistant")
            return text
        if lower.startswith("words") or lower.startswith("woerter") or lower.startswith("wörter"):
            words = self.memory.top_words()
            text = "\n".join(f"{w}: {c}" for w, c in words)
            self.memory.add_message(message, role="user")
            self.memory.add_message(text, role="assistant")
            return text
        if lower.startswith("ls") and self.repo:
            path = message.split(None, 1)[1] if " " in message else "."
            result = "\n".join(self.repo.list_dir(path))
            self.memory.add_message(message, role="user")
            self.memory.add_message(result, role="assistant")
            return result
        if lower.startswith("search:") or lower.startswith("suche:"):
            query = message.split(":", 1)[1].strip()
            results = self.memory.search_messages(query)
            text = "\n".join(f"{idx}: {data['text']}" for idx, data in results)
            self.memory.add_message(message, role="user")
            self.memory.add_message(text, role="assistant")
            return text
        if message.lower().startswith(("ziel:", "goal:")):
            goal_text = message.split(":", 1)[1].strip()
            self.goals.add_goal(goal_text)
            self.memory.add_message(goal_text, role="goal")
            return f"Neues Ziel gesetzt: {goal_text}"
        self.memory.add_message(message, role="user")
        messages = self.prompt_manager.build_prompt(message)
        # let the LLM respond and optionally request function calls
        response = self.llm.generate(messages, self.function_definitions())

        if isinstance(response, dict) and "function_call" in response:
            call = response["function_call"]
            output = self._execute_function(call["name"], call.get("arguments", ""))
            self.memory.add_message(output, role="function")
            messages.append({"role": "assistant", "function_call": call})
            messages.append({"role": "function", "name": call["name"], "content": output})
            final = self.llm.generate(messages)
            self.memory.add_message(final, role="assistant")
        else:
            self.memory.add_message(response, role="assistant")

        self._self_reflect()
        outputs = self.pending_outputs[:]
        self.pending_outputs.clear()
        if outputs:
            return "\n".join(outputs)
        return None

    def _self_reflect(self):
        """Simple self-reflection storing summary node."""
        context = ContextSelector(self.memory).get_context()
        summary_messages = [
            {
                "role": "system",
                "content": (
                    "Du bist MetaboMind und reflektierst dich selbst. "
                    "Wenn du dem Nutzer etwas mitteilen möchtest, rufe die Funktion "
                    "send_user_message auf."
                ),
            },
            {"role": "user", "content": context},
        ]
        resp = self.llm.generate(summary_messages, self.function_definitions())
        if isinstance(resp, dict) and "function_call" in resp:
            call = resp["function_call"]
            output = self._execute_function(call["name"], call.get("arguments", ""))
            self.memory.add_message(output, role="function")
            summary_messages.append({"role": "assistant", "function_call": call})
            summary_messages.append({"role": "function", "name": call["name"], "content": output})
            final = self.llm.generate(summary_messages)
            self.memory.add_message(final, role="reflection")
        else:
            final = resp
            self.memory.add_message(final, role="reflection")

    def tick(self, interval: float = 10.0):
        """Periodic self-reflection."""
        # called from UI every second; performs reflection every ``interval``
        now = time.time()
        if now - self.last_tick >= interval:
            self.last_tick = now
            with self.lock:
                self._self_reflect()
                outputs = self.pending_outputs[:]
                self.pending_outputs.clear()
                if outputs:
                    return "\n".join(outputs)
        return None

    def active_goal(self):
        return self.goals.active_goal()

    # new helper methods for repository operations
    def repo_analyze(self) -> str:
        if self.repo:
            return self.repo.analyze_repo()
        return "RepoManager nicht verfügbar"

    def repo_test(self) -> str:
        if self.repo:
            return self.repo.compile_repo()
        return "RepoManager nicht verfügbar"

    def repo_run_tests(self) -> str:
        if self.repo:
            return self.repo.run_tests()
        return "RepoManager nicht verfügbar"
    def repo_list_dir(self, path: str = ".") -> list:
        if self.repo:
            return self.repo.list_dir(path)
        return ["RepoManager nicht verfügbar"]
    def repo_apply_patch(self, patch: str) -> str:
        if self.repo:
            return self.repo.apply_patch(patch)
        return "RepoManager nicht verfügbar"
    def repo_grep(self, pattern: str) -> str:
        if self.repo:
            return self.repo.grep(pattern)
        return "RepoManager nicht verfügbar"

    def git_status(self) -> str:
        if self.git:
            return self.git.status()
        return "GitManager nicht verfügbar"

    def git_diff(self) -> str:
        if self.git:
            return self.git.diff()
        return "GitManager nicht verfügbar"

    def git_commit(self, message: str) -> str:
        if self.git:
            return self.git.commit(message)
        return "GitManager nicht verfügbar"
    def git_log(self, limit: int = 5) -> str:
        if self.git:
            return self.git.log(limit)
        return "GitManager nicht verfügbar"

    def repo_run_python(self, path: str) -> str:
        if self.repo:
            return self.repo.run_python(path)
        return "RepoManager nicht verfügbar"

    def repo_read_file(self, path: str) -> str:
        if self.repo:
            return self.repo.read_file(path)
        return "RepoManager nicht verfügbar"

    def repo_write_file(self, path: str, content: str) -> str:
        if self.repo:
            self.repo.write_file(path, content)
            return "Datei gespeichert"
        return "RepoManager nicht verfügbar"

    def memory_shortest_path(self, word1: str, word2: str) -> str:
        path = self.memory.shortest_path(word1, word2)
        if not path:
            return "Kein Pfad gefunden"
        return " -> ".join(f"{n}:{t[:20]}" for n, t in path)

    def function_definitions(self) -> list:
        """Return available function descriptions for the LLM."""
        return [
            {
                "name": "git_status",
                "description": "Zeigt den Git-Status an",
                "parameters": {"type": "object", "properties": {}},
            },
            {
                "name": "git_commit",
                "description": "Führt einen Git-Commit mit Nachricht aus",
                "parameters": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                    "required": ["message"],
                },
            },
            {
                "name": "git_diff",
                "description": "Zeigt die aktuellen Änderungen",
                "parameters": {"type": "object", "properties": {}},
            },
            {
                "name": "repo_analyze",
                "description": "Analysiert den Quellcode im Repository",
                "parameters": {"type": "object", "properties": {}},
            },
            {
                "name": "repo_test",
                "description": "Kompiliert alle Python-Dateien",
                "parameters": {"type": "object", "properties": {}},
            },
            {
                "name": "repo_run_tests",
                "description": "Führt Pytest im Repository aus",
                "parameters": {"type": "object", "properties": {}},
            },
            {
                "name": "repo_grep",
                "description": "Durchsucht Python-Dateien nach einem Muster",
                "parameters": {
                    "type": "object",
                    "properties": {"pattern": {"type": "string"}},
                    "required": ["pattern"],
                },
            },
            {
                "name": "repo_read_file",
                "description": "Liest eine Datei aus dem Repository",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            },
            {
                "name": "repo_write_file",
                "description": "Schreibt Inhalt in eine Datei",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["path", "content"],
                },
            },
            {
                "name": "repo_run_python",
                "description": "Führt eine Python-Datei aus",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            },
            {
                "name": "repo_apply_patch",
                "description": "Wendet einen unified diff Patch an",
                "parameters": {
                    "type": "object",
                    "properties": {"patch": {"type": "string"}},
                    "required": ["patch"],
                },
            },
            {
                "name": "repo_list_dir",
                "description": "Listet Dateien in einem Verzeichnis auf",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": [],
                },
            },
            {
                "name": "memory_top_words",
                "description": "Gibt die häufigsten Wörter im Gedächtnis zurück",
                "parameters": {
                    "type": "object",
                    "properties": {"limit": {"type": "integer"}},
                    "required": [],
                },
            },
            {
                "name": "git_log",
                "description": "Zeigt die letzten Commits an",
                "parameters": {
                    "type": "object",
                    "properties": {"limit": {"type": "integer"}},
                    "required": [],
                },
            },
            {
                "name": "memory_search",
                "description": "Durchsucht den Speicher nach einem Begriff",
                "parameters": {
                    "type": "object",
                    "properties": {"keyword": {"type": "string"}},
                    "required": ["keyword"],
                },
            },
            {
                "name": "memory_search_archive",
                "description": "Durchsucht das Archiv nach einem Begriff",
                "parameters": {
                    "type": "object",
                    "properties": {"keyword": {"type": "string"}},
                    "required": ["keyword"],
                },
            },
            {
                "name": "memory_export_graph",
                "description": "Speichert den Gedächtnisgraphen als PNG",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": [],
                },
            },
            {
                "name": "memory_shortest_path",
                "description": "Findet den kürzesten Pfad zwischen zwei Begriffen im Speicher",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "word1": {"type": "string"},
                        "word2": {"type": "string"},
                    },
                    "required": ["word1", "word2"],
                },
            },
            {
                "name": "send_user_message",
                "description": "Sendet eine Nachricht direkt an den Nutzer",
                "parameters": {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                },
            },
        ]

    def _execute_function(self, name: str, args_json: str) -> str:
        """Lookup and execute one of the helper methods."""
        import json

        try:
            args = json.loads(args_json) if args_json else {}
        except json.JSONDecodeError:
            args = {}
        func = getattr(self, name, None)
        if not callable(func):
            return f"Unbekannte Funktion: {name}"
        try:
            return func(**args)
        except TypeError as exc:
            return f"Fehler bei Funktionsaufruf: {exc}"

    def memory_top_words(self, limit: int = 10) -> str:
        words = self.memory.top_words(limit)
        return "\n".join(f"{w}: {c}" for w, c in words)

    def memory_search(self, keyword: str) -> str:
        results = self.memory.search_messages(keyword)
        if not results:
            return "Keine Treffer"
        return "\n".join(f"{idx}: {data['text']}" for idx, data in results)

    def memory_search_archive(self, keyword: str) -> str:
        results = self.memory.search_archive(keyword)
        if not results:
            return "Keine Treffer"
        return "\n".join(f"{r.get('id')}: {r.get('text')}" for r in results)

    def memory_export_graph(self, path: str = "graph.png") -> str:
        self.memory.export_png(path)
        return f"Graph gespeichert unter {path}"

    def send_user_message(self, text: str) -> str:
        """Store a message intended for the user and return confirmation."""
        self.pending_outputs.append(text)
        self.memory.add_message(text, role="assistant")
        return "ok"
