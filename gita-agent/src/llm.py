"""
LLM setup — OpenAI via langchain-openai.
"""

from langchain_openai import ChatOpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL, TEMPERATURE, MAX_TOKENS


def get_llm() -> ChatOpenAI:
    """Return a ChatOpenAI instance using the configured model and key."""
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is not set. "
            "Add it to your .env file or set it as an environment variable."
        )
    print(f"[LLM] Using OpenAI — model: {OPENAI_MODEL}")
    return ChatOpenAI(
        model=OPENAI_MODEL,
        openai_api_key=OPENAI_API_KEY,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
