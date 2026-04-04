import ast
import re
from .base import LanguageParser, FileInfo


class PythonParser(LanguageParser):
    EXTENSIONS = (".py",)
    LANGUAGE_NAME = "Python"

    def _extract(self, info: FileInfo, content: str) -> None:
        # AST-based extraction (most reliable for Python)
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    info.functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    info.classes.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        info.imports.extend(alias.name for alias in node.names)
                    else:
                        if node.module:
                            info.imports.append(node.module)
        except SyntaxError:
            # Fallback to regex if AST fails
            info.functions = re.findall(r"def\s+(\w+)\s*\(", content)
            info.classes = re.findall(r"class\s+(\w+)", content)

        # Flask / FastAPI / Django routes
        flask_routes = re.findall(
            r"@(?:app|bp|router)\.(?:route|get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]",
            content,
        )
        fastapi_routes = re.findall(
            r"@(?:app|router)\.(?:get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]",
            content,
        )
        django_routes = re.findall(
            r"path\s*\(\s*['\"]([^'\"]+)['\"]",
            content,
        )
        for path in flask_routes + fastapi_routes:
            info.routes.append({"method": "HTTP", "path": path})
        for path in django_routes:
            info.routes.append({"method": "Django", "path": path})

        # DB / service connections
        # Each entry: (usage_pattern, import_keyword, label)
        # A connection is only reported if BOTH the usage pattern AND the
        # import keyword appear in the file — avoids false positives in
        # parser/detector files that contain these strings as regex patterns.
        db_patterns = [
            (r"psycopg2\.connect|asyncpg\.connect", "psycopg2|asyncpg", "PostgreSQL"),
            (r"pymysql\.|mysql\.connector", "pymysql|mysql", "MySQL"),
            (r"pymongo\.|MongoClient\(", "pymongo|MongoClient", "MongoDB"),
            (r"redis\.Redis\(|aioredis\.", "redis|aioredis", "Redis"),
            (r"create_engine\(|sessionmaker\(", "sqlalchemy", "SQLAlchemy ORM"),
            (r"django\.db\.", "django", "Django ORM"),
            (r"tortoise\.Tortoise\.|Tortoise\.init", "tortoise", "Tortoise ORM"),
            (r"httpx\.(?:get|post|put|delete|AsyncClient)|requests\.(?:get|post|put|delete|Session)", "httpx|requests", "HTTP Client"),
            (r"boto3\.(?:client|resource|Session)", "boto3|botocore", "AWS (boto3)"),
            (r"celery\.Celery\(|\.apply_async\(|\.delay\(", "celery", "Celery"),
        ]
        imports_block = " ".join(info.imports).lower()
        for usage_pattern, import_keyword, label in db_patterns:
            import_found = any(kw in imports_block for kw in import_keyword.split("|"))
            usage_found = re.search(usage_pattern, content)
            if import_found and usage_found:
                info.connections.append({"type": label, "file": info.file})

        # Exports (module-level __all__)
        all_match = re.search(r"__all__\s*=\s*\[([^\]]+)\]", content)
        if all_match:
            info.exports = re.findall(r"['\"](\w+)['\"]", all_match.group(1))

        # Comments (first 15 meaningful docstrings / comments)
        info.comments = [
            line.strip().lstrip("#").strip()
            for line in content.splitlines()
            if line.strip().startswith("#")
        ][:15]
