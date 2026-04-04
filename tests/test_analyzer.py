import os
import json
from autoreadme.analyzer import _collect_files, _read_content, ProjectData, analyze_project

def test_collect_files(temp_project):
    files = _collect_files(temp_project)
    # package.json is NOT in SUPPORTED_EXTENSIONS (it's loaded separately)
    # src/main.py is in SUPPORTED_EXTENSIONS (.py)
    assert any(f.endswith("main.py") for f in files)
    assert not any(f.endswith("package.json") for f in files)

def test_read_content(temp_project):
    path = os.path.join(temp_project, "src", "main.py")
    content = _read_content(path)
    assert "def hello():" in content

def test_project_data_initialization():
    data = ProjectData(name="test")
    assert data.name == "test"
    assert isinstance(data.language_summary, dict)
    assert isinstance(data.dependencies, list)

def test_analyze_project_basic(temp_project, mock_llm):
    data = analyze_project(temp_project, mock_llm, cache_dir=os.path.join(temp_project, ".cache"))
    assert data.name == os.path.basename(temp_project)
    assert "dep1" in data.dependencies
    assert data.language_summary["Python"] == 1
    # Check if folders are mapped correctly
    assert "src" in data.folders_summary
