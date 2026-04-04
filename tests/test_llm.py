import pytest
from autoreadme.llm.factory import get_provider
from autoreadme.llm.base import LLMProvider

def test_get_provider_ollama():
    # We mock the import to avoid needing ollama installed for this unit test
    # but the factory tries to import autoreadme.llm.ollama_provider
    # For unit testing the factory logic:
    provider = get_provider("ollama", model="llama3")
    assert provider.model == "llama3"

def test_get_provider_invalid():
    with pytest.raises(ValueError):
        get_provider("invalid-provider")

def test_llm_provider_rag_chat(mock_llm):
    response = mock_llm.rag_chat("test prompt", ["context 1", "context 2"])
    assert "Mock RAG response" in response
