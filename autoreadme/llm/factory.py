from __future__ import annotations
from .base import LLMProvider


PROVIDER_MAP = {
    "ollama": ("autoreadme.llm.ollama_provider", "OllamaProvider"),
    "openai": ("autoreadme.llm.openai_provider", "OpenAIProvider"),
    "anthropic": ("autoreadme.llm.anthropic_provider", "AnthropicProvider"),
    "gemini": ("autoreadme.llm.gemini_provider", "GeminiProvider"),
    "groq": ("autoreadme.llm.groq_provider", "GroqProvider"),
}


def get_provider(
    provider: str = "ollama",
    model: str | None = None,
    api_key: str | None = None,
) -> LLMProvider:
    """
    Factory function to get an LLM provider instance.

    Args:
        provider: One of 'ollama', 'openai', 'anthropic', 'gemini'.
        model: Model name override. Uses provider default if None.
        api_key: API key override. Falls back to environment variable.

    Returns:
        An instance of the requested LLM provider.
    """
    provider = provider.lower()
    if provider not in PROVIDER_MAP:
        raise ValueError(
            f"Unknown provider '{provider}'. "
            f"Valid options: {', '.join(PROVIDER_MAP)}"
        )
    module_path, class_name = PROVIDER_MAP[provider]
    import importlib
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)

    kwargs: dict = {}
    if model:
        kwargs["model"] = model
    if api_key:
        kwargs["api_key"] = api_key

    return cls(**kwargs)
