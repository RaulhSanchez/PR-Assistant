import subprocess
import os

def get_git_diff(base="main"):
    """Get the current diff against a base branch."""
    try:
        # Check if we are in a git repo
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, check=True)
        
        # Get the diff
        result = subprocess.run(
            ["git", "diff", f"{base}...HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except Exception as e:
        return f"Error: No git repository found or git command failed: {e}"

def get_changed_files(base="main"):
    """Get a list of changed filenames relative to the base branch."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base}...HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except Exception:
        return []

def get_file_content_at_rev(file_path, rev="main"):
    """Get the content of a file at a specific revision."""
    try:
        result = subprocess.run(
            ["git", "show", f"{rev}:{file_path}"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except Exception:
        return None
