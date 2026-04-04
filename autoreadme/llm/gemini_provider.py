import os
from .base import LLMProvider


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""

    DEFAULT_MODEL = "gemini-1.5-flash"

    def __init__(self, model: str | None = None, api_key: str | None = None):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key or os.environ.get("GOOGLE_API_KEY"))
            self._genai = genai
        except ImportError:
            raise ImportError(
                "Google Generative AI SDK not installed. "
                "Run: pip install autoreadme[gemini]"
            )
        super().__init__(model or self.DEFAULT_MODEL)

    def chat(self, prompt: str) -> str:
        model = self._genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        return response.text
