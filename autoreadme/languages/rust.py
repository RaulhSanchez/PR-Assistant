import re
from .base import LanguageParser, FileInfo


class RustParser(LanguageParser):
    EXTENSIONS = (".rs",)
    LANGUAGE_NAME = "Rust"

    def _extract(self, info: FileInfo, content: str) -> None:
        # Functions (pub fn and fn)
        info.functions = re.findall(r"(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*[<(]", content)

        # Structs / Enums / Traits (as "classes")
        structs = re.findall(r"(?:pub\s+)?struct\s+(\w+)", content)
        enums = re.findall(r"(?:pub\s+)?enum\s+(\w+)", content)
        traits = re.findall(r"(?:pub\s+)?trait\s+(\w+)", content)
        info.classes = structs + enums + traits

        # Imports
        info.imports = re.findall(r"^use\s+([\w:{}, ]+);", content, re.MULTILINE)

        # Axum / Actix-web / Rocket routes
        route_patterns = [
            (r'get\s*\(\s*"([^"]+)"', "Axum/Actix GET"),
            (r'post\s*\(\s*"([^"]+)"', "Axum/Actix POST"),
            (r'#\[get\s*\(\s*"([^"]+)"\s*\)\]', "Rocket GET"),
            (r'#\[post\s*\(\s*"([^"]+)"\s*\)\]', "Rocket POST"),
        ]
        for pattern, framework in route_patterns:
            for match in re.finditer(pattern, content):
                info.routes.append({"method": framework, "path": match.group(1)})

        # DB connections
        db_patterns = [
            (r"sqlx::|PgPool|MySqlPool|SqlitePool", "SQLx"),
            (r"diesel::", "Diesel ORM"),
            (r"mongodb::", "MongoDB"),
            (r"redis::", "Redis"),
            (r"sea_orm::|SeaOrm", "SeaORM"),
            (r"reqwest::", "HTTP Client (reqwest)"),
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
