"""
LLM setup — Groq (free, fast inference) via langchain-groq.
"""

from langchain_groq import ChatGroq
from src.config import GROQ_API_KEY, GROQ_MODEL, TEMPERATURE, MAX_TOKENS


def get_llm() -> ChatGroq:
    """Return a ChatGroq instance using the configured model and key."""
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set. "
            "Get your free key at https://console.groq.com/keys "
            "and add it to your .env file."
        )
    print(f"[LLM] Using Groq — model: {GROQ_MODEL}")
    return ChatGroq(
        model=GROQ_MODEL,
        groq_api_key=GROQ_API_KEY,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
