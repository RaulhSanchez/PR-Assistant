import re
from .base import LanguageParser, FileInfo


class GoParser(LanguageParser):
    EXTENSIONS = (".go",)
    LANGUAGE_NAME = "Go"

    def _extract(self, info: FileInfo, content: str) -> None:
        # Functions
        info.functions = re.findall(r"^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(", content, re.MULTILINE)

        # Structs (as "classes")
        info.classes = re.findall(r"type\s+(\w+)\s+struct", content)

        # Interfaces
        interfaces = re.findall(r"type\s+(\w+)\s+interface", content)
        info.classes += interfaces

        # Imports
        import_block = re.search(r"import\s*\(([^)]+)\)", content, re.DOTALL)
        if import_block:
            info.imports = re.findall(r'"([^"]+)"', import_block.group(1))
        single_imports = re.findall(r'^import\s+"([^"]+)"', content, re.MULTILINE)
        info.imports += single_imports

        # Routes: net/http, gin, echo, fiber, chi
        patterns = [
            (r'http\.Handle(?:Func)?\s*\(\s*"([^"]+)"', "HTTP"),
            (r'r\.(?:GET|POST|PUT|DELETE|PATCH|HEAD)\s*\(\s*"([^"]+)"', "Gin/Chi/Echo"),
            (r'app\.(?:Get|Post|Put|Delete|Patch)\s*\(\s*"([^"]+)"', "Fiber"),
            (r'e\.(?:GET|POST|PUT|DELETE|PATCH)\s*\(\s*"([^"]+)"', "Echo"),
        ]
        for pattern, framework in patterns:
            for match in re.finditer(pattern, content):
                info.routes.append({"method": framework, "path": match.group(1)})

        # DB connections
        db_patterns = [
            (r"sql\.Open\(", "database/sql"),
            (r"gorm\.Open\(", "GORM"),
            (r"mongo\.Connect\(", "MongoDB"),
            (r"redis\.NewClient\(", "Redis"),
            (r"pgx\.Connect\(|pgxpool\.New\(", "PostgreSQL (pgx)"),
        ]
        for pattern, label in db_patterns:
            if re.search(pattern, content):
                info.connections.append({"type": label, "file": info.file})

        # Comments
        info.comments = [
            line.strip().lstrip("/").strip()
            for line in content.splitlines()
            if line.strip().startswith("//")
        ][:15]
