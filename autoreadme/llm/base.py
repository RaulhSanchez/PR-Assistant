from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    def chat(self, prompt: str) -> str:
        """Send a prompt and return the response text."""
        ...

    def rag_chat(self, prompt: str, context: list[str]) -> str:
        """Send a RAG-enriched prompt using a list of context strings."""
        context_block = "\n\n".join(context)
        full_prompt = (
            f"Usa el siguiente contexto técnico para responder en castellano, "
            f"de forma profesional y detallada:\n\n{context_block}\n\n{prompt}"
        )
        return self.chat(full_prompt)
