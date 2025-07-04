"""Dateioperationen innerhalb des Arbeitsverzeichnisses."""

import os
import subprocess
from typing import List
import ast

class RepoManager:
    """Manage file operations within a git repository."""

    def __init__(self, repo_path: str = '.'):
        # absolute path to the repository root
        self.repo_path = os.path.abspath(repo_path)

    def _resolve(self, path: str) -> str:
        """Return absolute path while preventing directory traversal."""
        full = os.path.abspath(os.path.join(self.repo_path, path))
        if not full.startswith(self.repo_path):
            raise ValueError('Pfad ausserhalb des Repositories nicht erlaubt')
        return full

    def list_dir(self, path: str = '.') -> List[str]:
        """Return directory contents relative to the repo root."""
        full = self._resolve(path)
        return os.listdir(full)

    def read_file(self, path: str) -> str:
        """Read and return the contents of ``path``."""
        full = self._resolve(path)
        with open(full, 'r', encoding='utf-8') as fh:
            return fh.read()

    def write_file(self, path: str, content: str) -> None:
        """Write ``content`` to ``path`` within the repo."""
        full = self._resolve(path)
        with open(full, 'w', encoding='utf-8') as fh:
            fh.write(content)

    def run_python(self, path: str) -> str:
        """Execute a Python file and return its output."""
        full = self._resolve(path)
        result = subprocess.run(['python3', full], capture_output=True, text=True)
        if result.returncode != 0:
            return f'Fehler beim Ausfuehren: {result.stderr.strip()}'
        return result.stdout.strip()

    def compile_repo(self) -> str:
        """Compile all Python files in the repository."""
        files = [f for f in os.listdir(self.repo_path) if f.endswith('.py')]
        cmd = ['python3', '-m', 'py_compile'] + files
        result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
        if result.returncode != 0:
            return f'Fehler beim Kompilieren: {result.stderr.strip()}'
        return 'Kompilierung erfolgreich'

    def run_tests(self) -> str:
        """Run pytest in the repository."""
        result = subprocess.run(
            ['python3', '-m', 'pytest', '-q'],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return (
                'Tests fehlgeschlagen:\n'
                + result.stdout
                + '\n'
                + result.stderr
            )
        return 'Tests erfolgreich:\n' + result.stdout

    def analyze_repo(self) -> str:
        """Return simple statistics about Python files in the repo."""
        lines = 0
        py_files = []
        func_count = 0
        class_count = 0
        loop_count = 0
        # discover all python files
        for root, _dirs, files in os.walk(self.repo_path):
            for f in files:
                if f.endswith('.py'):
                    py_files.append(os.path.join(root, f))
        # count basic metrics for each file
        for f in py_files:
            with open(f, 'r', encoding='utf-8') as fh:
                content = fh.read()
            lines += len(content.splitlines())
            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_count += 1
                elif isinstance(node, ast.ClassDef):
                    class_count += 1
                elif isinstance(node, (ast.For, ast.While)):
                    loop_count += 1
        return (
            f'Python-Dateien: {len(py_files)}, Gesamtzeilen: {lines}, '
            f'Funktionen: {func_count}, Klassen: {class_count}, '
            f'Schleifen: {loop_count}'
        )

    def apply_patch(self, patch: str) -> str:
        """Apply a unified diff patch within the repository."""
        # check patch for absolute paths to avoid escaping the repo
        for line in patch.splitlines():
            if line.startswith(('--- ', '+++ ')):
                path = line[4:].split('\t')[0].strip()
                if path == '/dev/null':
                    continue
                if path.startswith('/') or '..' in os.path.normpath(path).split(os.sep):
                    return 'Fehler: Patch enthaelt ungueltigen Pfad'
        result = subprocess.run(
            ['patch', '-p1', '--batch'],
            cwd=self.repo_path,
            input=patch,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            return f'Patch fehlgeschlagen: {result.stderr.strip()}'
        return result.stdout.strip() or 'Patch angewendet'

    def grep(self, pattern: str) -> str:
        """Search all Python files for ``pattern`` and return matching lines."""
        # collect matches from every *.py file
        matches = []
        for root, _dirs, files in os.walk(self.repo_path):
            for f in files:
                if not f.endswith('.py'):
                    continue
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as fh:
                    for i, line in enumerate(fh, 1):
                        if pattern in line:
                            rel = os.path.relpath(path, self.repo_path)
                            matches.append(f"{rel}:{i}:{line.strip()}")
        return '\n'.join(matches) if matches else 'Keine Treffer'
