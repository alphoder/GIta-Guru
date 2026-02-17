"""
LLM setup — supports both Ollama (free/local) and Anthropic Claude (API).
Switch between them by changing LLM_PROVIDER in config or .env.
"""

from langchain_community.llms import Ollama
from langchain_anthropic import ChatAnthropic
from src.config import (
    LLM_PROVIDER,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
)


def get_llm():
    """
    Return the configured LLM instance.
    - 'ollama'    → local Ollama server (free, no internet needed)
    - 'anthropic' → Anthropic Claude API (requires API key)
    """
    provider = LLM_PROVIDER.lower().strip()

    if provider == "ollama":
        print(f"[LLM] Using Ollama — model: {OLLAMA_MODEL}")
        return Ollama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=TEMPERATURE,
        )

    elif provider == "anthropic":
        if not ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set. "
                "Add it to your .env file or export it as an environment variable."
            )
        print(f"[LLM] Using Anthropic Claude — model: {ANTHROPIC_MODEL}")
        return ChatAnthropic(
            model=ANTHROPIC_MODEL,
            anthropic_api_key=ANTHROPIC_API_KEY,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{LLM_PROVIDER}'. Use 'ollama' or 'anthropic'."
        )
