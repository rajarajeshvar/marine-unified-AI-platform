"""
Marine Guardian AI — LLM Provider Service

Abstracts the underlying Language Model provider (Ollama, OpenAI, Anthropic, etc.)
Allows switching between local inference and cloud APIs seamlessly.
"""

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from config import LLM_PROVIDER, LLM_MODEL, OLLAMA_BASE_URL, OPENAI_API_KEY, ANTHROPIC_API_KEY


def get_llm() -> BaseChatModel:
    """Factory function to instantiate the configured LLM provider."""
    provider = LLM_PROVIDER.lower().strip()

    if provider == "ollama":
        return ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL)

    elif provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY must be set in .env when using 'openai' provider.")
            return ChatOpenAI(model=LLM_MODEL, api_key=OPENAI_API_KEY)
        except ImportError:
            raise ImportError("Please run `pip install langchain-openai` to use OpenAI models.")

    elif provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
            if not ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY must be set in .env when using 'anthropic' provider.")
            return ChatAnthropic(model=LLM_MODEL, api_key=ANTHROPIC_API_KEY)
        except ImportError:
            raise ImportError("Please run `pip install langchain-anthropic` to use Anthropic models.")

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")
