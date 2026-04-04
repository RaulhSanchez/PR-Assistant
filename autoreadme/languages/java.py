import re
from .base import LanguageParser, FileInfo


class JavaParser(LanguageParser):
    EXTENSIONS = (".java",)
    LANGUAGE_NAME = "Java"

    def _extract(self, info: FileInfo, content: str) -> None:
        # Classes and interfaces
        info.classes = re.findall(
            r"(?:public|private|protected)?\s*(?:abstract\s+)?(?:class|interface|enum)\s+(\w+)",
            content,
        )

        # Methods
        info.functions = re.findall(
            r"(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+\w+\s*)?\{",
            content,
        )

        # Imports
        info.imports = re.findall(r"^import\s+([\w.]+);", content, re.MULTILINE)

        # Spring/JAX-RS routes
        route_patterns = [
            (r'@(?:Get|Post|Put|Delete|Patch)Mapping\s*\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\']', "Spring"),
            (r'@RequestMapping\s*\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\']', "Spring"),
            (r'@Path\s*\(\s*["\']([^"\']+)["\']', "JAX-RS"),
        ]
        for pattern, framework in route_patterns:
            for match in re.finditer(pattern, content):
                info.routes.append({"method": framework, "path": match.group(1)})

        # DB patterns
        db_patterns = [
            (r"@Repository|JpaRepository|CrudRepository", "Spring Data JPA"),
            (r"EntityManager|@Entity", "JPA/Hibernate"),
            (r"JdbcTemplate|NamedParameterJdbcTemplate", "Spring JDBC"),
            (r"MongoRepository|MongoTemplate", "MongoDB"),
            (r"RedisTemplate|@RedisHash", "Redis"),
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
