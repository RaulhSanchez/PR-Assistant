import re
from .base import LanguageParser, FileInfo


class JavaScriptParser(LanguageParser):
    EXTENSIONS = (".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs")
    LANGUAGE_NAME = "JavaScript/TypeScript"

    def _extract(self, info: FileInfo, content: str) -> None:
        lines = content.splitlines()

        # Exports
        info.exports = re.findall(
            r"export\s+(?:default\s+)?(?:const|function|class|async\s+function)?\s*(\w+)",
            content,
        )

        # Functions (named + arrow)
        info.functions = list(set(
            re.findall(r"(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\()", content)
        ))
        # Flatten tuples from alternation groups
        info.functions = [f for group in info.functions for f in group if f]

        # Classes
        info.classes = re.findall(r"class\s+(\w+)", content)

        # Imports
        info.imports = re.findall(
            r"(?:import|require)\s*[({\"']([^'\")\s]+)[\"')}]", content
        )

        # Express/Fastify/Hono routes
        route_pattern = re.compile(
            r"(?:app|router|server)\.(get|post|put|delete|patch|head|options)\s*"
            r"\(\s*['\"`]([^'\"` ]+)['\"`]",
            re.IGNORECASE,
        )
        for match in route_pattern.finditer(content):
            info.routes.append({"method": match.group(1).upper(), "path": match.group(2)})

        # DB / service connections
        db_patterns = [
            (r"mongoose\.connect\(([^)]+)\)", "MongoDB"),
            (r"new\s+(?:Pool|Client)\s*\(", "PostgreSQL/MySQL"),
            (r"redis\.createClient\(", "Redis"),
            (r"new\s+Sequelize\(", "Sequelize ORM"),
            (r"createConnection\(", "DB Connection"),
            (r"prisma\.\w+\.", "Prisma ORM"),
            (r"knex\(", "Knex.js"),
            (r"axios\.", "HTTP Client (axios)"),
            (r"fetch\(", "HTTP Client (fetch)"),
        ]
        for pattern, label in db_patterns:
            if re.search(pattern, content):
                info.connections.append({"type": label, "file": info.file})

        # Inline comments (first 20)
        info.comments = [
            line.strip().lstrip("//").strip()
            for line in lines
            if line.strip().startswith("//")
        ][:20]
