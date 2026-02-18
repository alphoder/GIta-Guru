"""
LLM setup — Google Gemini via langchain-google-genai.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import GOOGLE_API_KEY, GEMINI_MODEL, TEMPERATURE, MAX_TOKENS


def get_llm() -> ChatGoogleGenerativeAI:
    """Return a ChatGoogleGenerativeAI instance using the configured model and key."""
    if not GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY is not set. "
            "Get your key at https://aistudio.google.com/app/apikey "
            "and add it to your .env file."
        )
    print(f"[LLM] Using Google Gemini — model: {GEMINI_MODEL}")
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=TEMPERATURE,
        max_output_tokens=MAX_TOKENS,
    )
