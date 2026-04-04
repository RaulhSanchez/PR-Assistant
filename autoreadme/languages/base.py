from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class FileInfo:
    """Structured data extracted from a source file."""
    file: str
    language: str
    exports: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    routes: list[dict] = field(default_factory=list)
    connections: list[dict] = field(default_factory=list)
    comments: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    narrative: str = ""
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "language": self.language,
            "exports": self.exports,
            "functions": self.functions,
            "classes": self.classes,
            "routes": self.routes,
            "connections": self.connections,
            "comments": self.comments,
            "imports": self.imports,
            "narrative": self.narrative,
            "error": self.error,
        }


class LanguageParser(ABC):
    """Base class for language-specific static parsers."""

    EXTENSIONS: tuple[str, ...] = ()
    LANGUAGE_NAME: str = ""

    def parse(self, file_path: str, content: str) -> FileInfo:
        """
        Run static analysis on file content and return structured FileInfo.
        This should be fast — no LLM calls here.
        """
        info = FileInfo(file=file_path, language=self.LANGUAGE_NAME)
        try:
            self._extract(info, content)
        except Exception as e:
            info.error = str(e)
        return info

    @abstractmethod
    def _extract(self, info: FileInfo, content: str) -> None:
        """Populate `info` fields by parsing `content`."""
        ...

    def build_llm_prompt(self, file_path: str, content_short: str) -> str:
        """Build the prompt to send to the LLM for narrative generation."""
        return (
            f"Analiza este archivo {self.LANGUAGE_NAME} y genera un resumen técnico "
            f"en castellano:\n\n{content_short}\n\n"
            f"Incluye: propósito del archivo, funciones y clases principales, "
            f"rutas o endpoints de API (si hay), acceso a bases de datos o "
            f"servicios externos."
        )
