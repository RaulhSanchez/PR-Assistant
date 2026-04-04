import os
from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI provider (GPT-4o, GPT-4-turbo, etc.)."""

    DEFAULT_MODEL = "gpt-4o"

    def __init__(self, model: str | None = None, api_key: str | None = None):
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError(
                "OpenAI SDK not installed. Run: pip install autoreadme[openai]"
            )
        super().__init__(model or self.DEFAULT_MODEL)

    def chat(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
