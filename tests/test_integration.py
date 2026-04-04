import os
from autoreadme.generator import generate_readme
from autoreadme.analyzer import analyze_project

def test_full_flow_integration(temp_project, mock_llm):
    # 1. Analyze
    data = analyze_project(temp_project, mock_llm, cache_dir=os.path.join(temp_project, ".cache"))
    
    # 2. Generate
    output_path = os.path.join(temp_project, "GENERATED_README.md")
    readme = generate_readme(data, output_path, mock_llm)
    
    assert os.path.exists(output_path)
    assert data.name in readme
    assert "Mock RAG response" in readme
    assert "main.py" in readme
