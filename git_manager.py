"""Wrapper für grundlegende Git-Befehle."""

import subprocess

class GitManager:
    """Simple wrapper around git commands."""

    def __init__(self, repo_path: str = '.'):
        # root directory of the git repository
        self.repo_path = repo_path

    def _run(self, *args: str) -> str:
        """Execute a git command and return its output or error."""
        result = subprocess.run(
            ['git'] + list(args),
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return f"Git-Fehler: {result.stderr.strip()}"
        return result.stdout.strip()

    def status(self) -> str:
        return self._run('status', '--short')

    def diff(self) -> str:
        return self._run('diff', '--stat')

    def pull(self) -> str:
        return self._run('pull')

    def push(self) -> str:
        return self._run('push')

    def commit(self, message: str) -> str:
        self._run('add', '-A')
        return self._run('commit', '-m', message)

    def log(self, limit: int = 5) -> str:
        return self._run('log', '-n', str(limit), '--oneline')

    def execute(self, command: str) -> str:
        """Parse ``command`` and execute the matching git operation."""
        tokens = command.strip().split()
        if not tokens:
            return 'Kein Git-Befehl angegeben.'
        cmd = tokens[0]
        args = tokens[1:]
        if cmd == 'status':
            return self.status()
        if cmd == 'diff':
            return self.diff()
        if cmd == 'pull':
            return self.pull()
        if cmd == 'push':
            return self.push()
        if cmd == 'commit':
            msg = ' '.join(args) or 'Automatischer Commit'
            return self.commit(msg)
        if cmd == 'log':
            limit = int(args[0]) if args else 5
            return self.log(limit)
        # default: pass through
        return self._run(cmd, *args)
