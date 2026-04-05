import os
from .base import LLMProvider


class GroqProvider(LLMProvider):
    """Groq provider — free tier, OpenAI-compatible (llama-3.1-8b-instant, mixtral, etc.)."""

    DEFAULT_MODEL = "llama-3.1-8b-instant"

    def __init__(self, model: str | None = None, api_key: str | None = None):
        try:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=api_key or os.environ.get("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
            )
        except ImportError:
            raise ImportError(
                "OpenAI SDK not installed. Run: pip install autoreadme[groq]"
            )
        super().__init__(model or self.DEFAULT_MODEL)

    def chat(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
