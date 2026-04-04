import pytest
import os
import shutil
import tempfile
from unittest.mock import MagicMock
from autoreadme.llm.base import LLMProvider
from autoreadme.analyzer import ProjectData

class MockLLM(LLMProvider):
    def __init__(self, model="mock-model"):
        super().__init__(model)
        self.responses = []
    
    def chat(self, prompt: str) -> str:
        if self.responses:
            return self.responses.pop(0)
        return "Mock response for prompt"

    def rag_chat(self, prompt: str, context: list[str]) -> str:
        return f"Mock RAG response for: {prompt[:20]}..."

@pytest.fixture
def mock_llm():
    return MockLLM()

@pytest.fixture
def temp_project():
    """Creates a temporary project structure for testing."""
    tmpdir = tempfile.mkdtemp()
    
    # Create some files
    os.makedirs(os.path.join(tmpdir, "src"))
    with open(os.path.join(tmpdir, "src", "main.py"), "w") as f:
        f.write("def hello():\n    print('world')\n")
    
    with open(os.path.join(tmpdir, "package.json"), "w") as f:
        f.write('{"name": "test-pkg", "description": "Test description", "dependencies": {"dep1": "1.0"}}')
        
    yield tmpdir
    
    shutil.rmtree(tmpdir)

@pytest.fixture
def sample_project_data():
    data = ProjectData(name="test-project", description="A sample project")
    data.language_summary = {"Python": 2, "JavaScript": 1}
    data.folders_summary = {
        "src": [
            {"file": "src/main.py", "language": "Python", "functions": ["hello"], "narrative": "Main entry point"}
        ]
    }
    return data
