import os
from .base import LLMProvider


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    DEFAULT_MODEL = "claude-3-5-haiku-20241022"

    def __init__(self, model: str | None = None, api_key: str | None = None):
        try:
            import anthropic
            self._client = anthropic.Anthropic(
                api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
            )
        except ImportError:
            raise ImportError(
                "Anthropic SDK not installed. Run: pip install autoreadme[anthropic]"
            )
        super().__init__(model or self.DEFAULT_MODEL)

    def chat(self, prompt: str) -> str:
        message = self._client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
