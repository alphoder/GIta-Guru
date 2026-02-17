"""
RAG chain — retrieval + generation pipeline for GitaGuru.
Now includes conversation memory and user profile for personalized counseling.
"""

from src.vector_store import get_retriever
from src.llm import get_llm
from src.prompts import (
    RAG_PROMPT,
    format_retrieved_docs,
    format_chat_history,
    format_user_profile,
)


def ask_gita(
    question: str,
    llm_provider: str = None,
    chat_history: list = None,
    user_profile: dict = None,
) -> dict:
    """
    Ask GitaGuru a question with full conversational context.

    Args:
        question:     The user's current message
        llm_provider: "ollama" or "anthropic" (overrides config)
        chat_history: List of {"role": ..., "content": ...} message dicts
        user_profile: Dict with "name" and/or "situation" keys
    Returns:
        Dict with 'answer' and 'sources'
    """
    if llm_provider:
        import src.config as cfg
        cfg.LLM_PROVIDER = llm_provider

    retriever = get_retriever()
    llm = get_llm()

    # Retrieve relevant verses based on the question
    docs = retriever.invoke(question)

    # Format all prompt variables
    context = format_retrieved_docs(docs)
    history_str = format_chat_history(chat_history or [])
    profile_str = format_user_profile(user_profile or {})

    # Build prompt with all context and invoke LLM
    prompt_value = RAG_PROMPT.format_messages(
        context=context,
        question=question,
        chat_history=history_str,
        user_profile=profile_str,
    )
    response = llm.invoke(prompt_value)

    # Extract answer text
    answer = response.content if hasattr(response, "content") else str(response)

    # Build source citations
    sources = []
    for doc in docs:
        meta = doc.metadata
        sources.append({
            "chapter": meta.get("chapter_number", "?"),
            "verse": meta.get("verse_number", "?"),
            "chapter_name": meta.get("chapter_name", ""),
            "text_snippet": doc.page_content[:200],
        })

    return {"answer": answer, "sources": sources}
