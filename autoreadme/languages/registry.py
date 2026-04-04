from .javascript import JavaScriptParser
from .python import PythonParser
from .go import GoParser
from .java import JavaParser
from .rust import RustParser
from .ruby import RubyParser
from .base import LanguageParser

_PARSERS: list[type[LanguageParser]] = [
    JavaScriptParser,
    PythonParser,
    GoParser,
    JavaParser,
    RustParser,
    RubyParser,
]

# Build extension → parser map
_EXT_MAP: dict[str, LanguageParser] = {}
for _cls in _PARSERS:
    _instance = _cls()
    for _ext in _cls.EXTENSIONS:
        _EXT_MAP[_ext] = _instance

SUPPORTED_EXTENSIONS: tuple[str, ...] = tuple(_EXT_MAP.keys())


def get_parser_for_file(file_path: str) -> LanguageParser | None:
    """Return the appropriate parser for a given file path, or None if unsupported."""
    import os
    ext = os.path.splitext(file_path)[1].lower()
    return _EXT_MAP.get(ext)
