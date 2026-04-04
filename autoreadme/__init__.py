"""
autoreadme — Generate professional README files from your codebase using AI.
"""

__version__ = "0.1.0"
__author__ = "autoreadme"

from .analyzer import analyze_project, ProjectData
from .generator import generate_readme
from .llm import get_provider

__all__ = [
    "analyze_project",
    "generate_readme",
    "get_provider",
    "ProjectData",
    "__version__",
]
