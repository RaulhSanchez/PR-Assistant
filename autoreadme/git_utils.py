import subprocess
import os

def _run_git(args: list[str], cwd: str) -> subprocess.CompletedProcess:
    """Run a git command in a specific directory."""
    return subprocess.run(args, capture_output=True, text=True, cwd=cwd)

def get_git_diff(base: str = "main", cwd: str = ".") -> str:
    """Get the current diff against a base branch."""
    try:
        check = _run_git(["git", "rev-parse", "--is-inside-work-tree"], cwd=cwd)
        if check.returncode != 0:
            return f"Error: '{cwd}' is not inside a git repository."
        result = _run_git(["git", "diff", f"{base}...HEAD"], cwd=cwd)
        return result.stdout or "(no changes)"
    except Exception as e:
        return f"Error: git command failed: {e}"

def get_changed_files(base: str = "main", cwd: str = ".") -> list[str]:
    """Get a list of changed filenames relative to the base branch."""
    try:
        result = _run_git(["git", "diff", "--name-only", f"{base}...HEAD"], cwd=cwd)
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except Exception:
        return []

def get_file_content_at_rev(file_path: str, rev: str = "main", cwd: str = ".") -> str | None:
    """Get the content of a file at a specific revision."""
    try:
        result = _run_git(["git", "show", f"{rev}:{file_path}"], cwd=cwd)
        return result.stdout if result.returncode == 0 else None
    except Exception:
        return None
