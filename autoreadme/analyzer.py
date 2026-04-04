"""
analyzer.py — Multi-language project analyzer.

Walks the project directory, runs static parsers per file,
then enriches each file with an LLM-generated narrative.
"""
from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from .languages import get_parser_for_file, SUPPORTED_EXTENSIONS, FileInfo
from .llm.base import LLMProvider

MAX_LINES = 500
DEFAULT_WORKERS = 4

# Directories to always skip during traversal
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__",
    ".mypy_cache", ".ruff_cache", "dist", "build", ".next",
    "coverage", ".pytest_cache", "target", "tests",
}

# Directories whose files are never counted as real API routes or DB connections
# (parsers, test files, fixtures — they contain pattern strings, not real usage)
SKIP_ROUTES_AND_CONNECTIONS_DIRS = {"tests", "test", "spec", "specs", "languages", "parsers"}


@dataclass
class ProjectData:
    """All data extracted from a project."""
    name: str
    description: str = ""
    language_summary: dict[str, int] = field(default_factory=dict)
    folders_summary: dict[str, list[dict]] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    dev_dependencies: list[str] = field(default_factory=list)
    routes: list[dict] = field(default_factory=list)
    connections: list[dict] = field(default_factory=list)
    docker: str = ""
    k8s: dict[str, str] = field(default_factory=dict)


def _load_gitignore(project_path: str):
    """Load .gitignore and return a PathSpec object, or None."""
    path = os.path.join(project_path, ".gitignore")
    if not os.path.exists(path):
        return None
    try:
        import pathspec
        with open(path, "r", encoding="utf-8") as f:
            spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
        return spec
    except (ImportError, Exception):
        return None


def _collect_files(project_path: str) -> list[str]:
    """Recursively collect all supported source files, respecting .gitignore."""
    collected = []
    gitignore = _load_gitignore(project_path)

    for root, dirs, files in os.walk(project_path):
        # Prune skip dirs in-place so os.walk doesn't descend
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        # Calculate relative path of the root for gitignore matching
        rel_root = os.path.relpath(root, project_path)
        if rel_root == ".":
            rel_root = ""

        for filename in files:
            rel_path = os.path.join(rel_root, filename)
            
            # Check gitignore
            if gitignore and gitignore.match_file(rel_path):
                continue

            ext = os.path.splitext(filename)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                collected.append(os.path.join(root, filename))
    return collected


def _read_content(file_path: str) -> str:
    """Read file content, truncating to MAX_LINES if necessary."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    if len(lines) > MAX_LINES:
        lines = lines[:MAX_LINES]
    return "".join(lines)


def _analyze_file(
    file_path: str,
    llm: LLMProvider,
    cache_dir: str,
) -> dict:
    """Analyze a single file: static parse + LLM narrative, with caching."""
    cache_key = file_path.replace(os.sep, "_").replace(":", "") + ".json"
    cache_file = os.path.join(cache_dir, cache_key)

    # Check cache
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached = json.load(f)
            # Invalidate if file was modified
            mtime = os.path.getmtime(file_path)
            if cached.get("mtime") == mtime:
                return cached["data"]
        except Exception:
            pass

    try:
        content = _read_content(file_path)
        parser = get_parser_for_file(file_path)
        if not parser:
            return {"file": file_path, "language": "unknown", "error": "No parser"}

        info: FileInfo = parser.parse(file_path, content)

        # LLM narrative
        prompt = parser.build_llm_prompt(file_path, content)
        info.narrative = llm.chat(prompt)

        result = info.to_dict()

        # Save to cache
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"mtime": os.path.getmtime(file_path), "data": result}, f, ensure_ascii=False, indent=2)

        return result

    except Exception as e:
        return {"file": file_path, "language": "unknown", "error": str(e)}


def analyze_project(
    project_path: str,
    llm: LLMProvider,
    workers: int = DEFAULT_WORKERS,
    cache_dir: str = "/tmp/autoreadme_cache",
    progress_callback=None,
) -> ProjectData:
    """
    Analyze an entire project and return structured ProjectData.

    Args:
        project_path: Absolute path to the project root.
        llm: An initialized LLMProvider instance.
        workers: Number of parallel threads for LLM calls.
        cache_dir: Directory to store analysis cache.
        progress_callback: Optional callable(processed, total, file_path).
    """
    project_path = os.path.abspath(project_path)
    data = ProjectData(name=os.path.basename(project_path))

    # ── Package / dependency files ──────────────────────────────────────────
    _load_package_json(project_path, data)
    _load_pyproject_toml(project_path, data)
    _load_go_mod(project_path, data)
    _load_cargo_toml(project_path, data)
    _load_gemfile(project_path, data)

    # ── Docker / K8s ─────────────────────────────────────────────────────────
    _load_docker(project_path, data)
    _load_k8s(project_path, data)

    # ── Source files ─────────────────────────────────────────────────────────
    all_files = _collect_files(project_path)
    total = len(all_files)
    processed = 0
    start_time = time.time()

    results: list[dict] = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(_analyze_file, fp, llm, cache_dir): fp
            for fp in all_files
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            processed += 1
            if progress_callback:
                elapsed = time.time() - start_time
                avg = elapsed / processed
                remaining = avg * (total - processed)
                progress_callback(processed, total, futures[future], elapsed, remaining)

    # ── Organise by folder ────────────────────────────────────────────────────
    for r in results:
        fp = r.get("file", "")
        rel_folder = os.path.relpath(os.path.dirname(fp), project_path)
        data.folders_summary.setdefault(rel_folder, []).append(r)
        lang = r.get("language", "unknown")
        data.language_summary[lang] = data.language_summary.get(lang, 0) + 1

        # Skip routes and connections from test/parser directories
        rel_parts = set(rel_folder.replace("\\", "/").split("/"))
        if rel_parts & SKIP_ROUTES_AND_CONNECTIONS_DIRS:
            continue

        # Aggregate routes — inject file path into each route dict
        for route in r.get("routes", []):
            data.routes.append({**route, "file": fp})

        # Aggregate connections
        data.connections.extend(r.get("connections", []))

    return data


# ── Dependency loaders ────────────────────────────────────────────────────────

def _load_package_json(project_path: str, data: ProjectData) -> None:
    path = os.path.join(project_path, "package.json")
    if not os.path.exists(path):
        return
    import json
    with open(path, "r", encoding="utf-8") as f:
        pkg = json.load(f)
    if not data.description:
        data.description = pkg.get("description", "")
    data.dependencies += list(pkg.get("dependencies", {}).keys())
    data.dev_dependencies += list(pkg.get("devDependencies", {}).keys())


def _load_pyproject_toml(project_path: str, data: ProjectData) -> None:
    path = os.path.join(project_path, "pyproject.toml")
    if not os.path.exists(path):
        return
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore
        except ImportError:
            return
    with open(path, "rb") as f:
        toml = tomllib.load(f)
    project = toml.get("project", {})
    if not data.description:
        data.description = project.get("description", "")
    for dep in project.get("dependencies", []):
        name = dep.split("[")[0].split(">")[0].split("<")[0].split("=")[0].strip()
        data.dependencies.append(name)


def _load_go_mod(project_path: str, data: ProjectData) -> None:
    path = os.path.join(project_path, "go.mod")
    if not os.path.exists(path):
        return
    import re
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    requires = re.findall(r"^\s+([\w./\-]+)\s+v[\w.+\-]+", content, re.MULTILINE)
    data.dependencies += requires


def _load_cargo_toml(project_path: str, data: ProjectData) -> None:
    path = os.path.join(project_path, "Cargo.toml")
    if not os.path.exists(path):
        return
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore
        except ImportError:
            return
    with open(path, "rb") as f:
        toml = tomllib.load(f)
    if not data.description:
        data.description = toml.get("package", {}).get("description", "")
    data.dependencies += list(toml.get("dependencies", {}).keys())
    data.dev_dependencies += list(toml.get("dev-dependencies", {}).keys())


def _load_gemfile(project_path: str, data: ProjectData) -> None:
    path = os.path.join(project_path, "Gemfile")
    if not os.path.exists(path):
        return
    import re
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    gems = re.findall(r"gem\s+['\"](\w[\w\-]*)['\"]", content)
    data.dependencies += gems


def _load_docker(project_path: str, data: ProjectData) -> None:
    for name in ("docker-compose.yml", "docker-compose.yaml"):
        path = os.path.join(project_path, name)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data.docker = f.read()
            return


def _load_k8s(project_path: str, data: ProjectData) -> None:
    k8s_path = os.path.join(project_path, "deploy", "k8s")
    if not os.path.exists(k8s_path):
        return
    for filename in os.listdir(k8s_path):
        if filename.endswith((".yml", ".yaml")):
            with open(os.path.join(k8s_path, filename), "r", encoding="utf-8") as f:
                data.k8s[filename] = f.read()
