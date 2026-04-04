import re
from .base import LanguageParser, FileInfo


class RubyParser(LanguageParser):
    EXTENSIONS = (".rb",)
    LANGUAGE_NAME = "Ruby"

    def _extract(self, info: FileInfo, content: str) -> None:
        # Methods
        info.functions = re.findall(r"^\s*def\s+(\w+)", content, re.MULTILINE)

        # Classes and Modules
        info.classes = re.findall(r"^\s*(?:class|module)\s+(\w+)", content, re.MULTILINE)

        # Requires / includes
        info.imports = re.findall(r"require(?:_relative)?\s+['\"]([^'\"]+)['\"]", content)

        # Rails routes
        route_patterns = [
            (r"(?:get|post|put|patch|delete)\s+['\"]([^'\"]+)['\"]", "Rails"),
            (r"resources\s+:(\w+)", "Rails resources"),
            (r"namespace\s+:(\w+)", "Rails namespace"),
        ]
        for pattern, framework in route_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                info.routes.append({"method": framework, "path": match.group(1)})

        # DB / service patterns
        db_patterns = [
            (r"ActiveRecord::|ApplicationRecord|has_many|belongs_to", "ActiveRecord (Rails)"),
            (r"Mongoid::|include Mongoid", "Mongoid (MongoDB)"),
            (r"Redis\.new|$redis", "Redis"),
            (r"Sequel\.", "Sequel ORM"),
            (r"HTTParty\.|Faraday\.|RestClient\.", "HTTP Client"),
            (r"Sidekiq::|perform_async", "Sidekiq"),
        ]
        for pattern, label in db_patterns:
            if re.search(pattern, content):
                info.connections.append({"type": label, "file": info.file})

        # Comments
        info.comments = [
            line.strip().lstrip("#").strip()
            for line in content.splitlines()
            if line.strip().startswith("#")
        ][:15]
