import pytest
from autoreadme.languages.python import PythonParser
from autoreadme.languages.registry import get_parser_for_file

def test_python_parser_ast():
    parser = PythonParser()
    content = """
class MyClass:
    def method(self):
        pass

def top_level_func():
    pass

import os
from sys import path
"""
    info = parser.parse("test.py", content)
    assert "MyClass" in info.classes
    assert "method" in info.functions
    assert "top_level_func" in info.functions
    assert "os" in info.imports
    assert "sys" in info.imports

def test_python_parser_regex_fallback():
    parser = PythonParser()
    # Invalid syntax to force regex fallback
    content = "class 123: def invalid("
    info = parser.parse("invalid.py", content)
    # Registry should still work for filename-based detection
    assert info.language == "Python"

def test_python_routes_detection():
    parser = PythonParser()
    content = """
@app.route('/hello')
def index(): pass

@router.get('/api/v1/users')
async def get_users(): pass
"""
    info = parser.parse("app.py", content)
    paths = [r['path'] for r in info.routes]
    assert '/hello' in paths
    assert '/api/v1/users' in paths

def test_registry():
    parser = get_parser_for_file("script.py")
    assert isinstance(parser, PythonParser)
    
    assert get_parser_for_file("unknown.xyz") is None
