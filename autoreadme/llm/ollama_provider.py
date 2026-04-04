from .base import LLMProvider


class OllamaProvider(LLMProvider):
    """Local Ollama provider — no API key required."""

    DEFAULT_MODEL = "qwen2.5-coder:1.5b"

    def __init__(self, model: str | None = None):
        try:
            from ollama import chat as _chat
            self._chat = _chat
        except ImportError:
            raise ImportError(
                "Ollama SDK not installed. Run: pip install autoreadme[ollama]"
            )
        super().__init__(model or self.DEFAULT_MODEL)

    def chat(self, prompt: str) -> str:
        response = self._chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]
