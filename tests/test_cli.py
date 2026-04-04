import os
from click.testing import CliRunner
from autoreadme.cli import cli, load_config
from unittest.mock import patch

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert "Generates a professional README.md" in result.output

def test_cli_config_show():
    runner = CliRunner()
    # Path '.' is needed because the CLI group takes an argument first
    result = runner.invoke(cli, ['.', 'config', 'show'])
    assert result.exit_code == 0
    assert "autoreadme config" in result.output

@patch('autoreadme.cli.load_config')
def test_cli_config_set_key(mock_load):
    mock_load.return_value = {"api_keys": {}}
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['.', 'config', 'set-key', 'openai', 'test-key'])
        assert result.exit_code == 0
        # Check for substring to avoid ANSI color issues
        assert "API key for openai saved" in result.output

@patch('autoreadme.llm.factory.get_provider')
@patch('autoreadme.analyzer.analyze_project')
@patch('autoreadme.generator.generate_readme')
def test_cli_analyze_flow(mock_gen, mock_analyze, mock_get_provider, temp_project, mock_llm, sample_project_data):
    mock_get_provider.return_value = mock_llm
    mock_analyze.return_value = sample_project_data
    
    runner = CliRunner()
    # Options should come BEFORE the project_path argument in this Click configuration
    result = runner.invoke(cli, ['--provider', 'ollama', temp_project])
    
    if result.exit_code != 0:
        print(f"CLI Error: {result.output}")
    assert result.exit_code == 0
    assert "Analysis complete" in result.output
    assert "README generated" in result.output
