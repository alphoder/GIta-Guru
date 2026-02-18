"""
RAG chain — retrieval + generation pipeline for GitaGuru.
Includes conversation memory, user profile, and verse deduplication.
"""

from src.vector_store import get_vector_store
from src.llm import get_llm
from src.config import TOP_K_RESULTS
from src.prompts import (
    RAG_PROMPT,
    format_retrieved_docs,
    format_chat_history,
    format_user_profile,
)


def _extract_cited_verses(chat_history: list) -> set:
    """Extract verse IDs already cited in the conversation to avoid repeats."""
    cited = set()
    if not chat_history:
        return cited
    for msg in chat_history:
        if msg["role"] == "assistant":
            content = msg["content"]
            # Look for patterns like "Chapter 2, Verse 47" or "2.47"
            import re
            for match in re.finditer(r"Chapter\s+(\d+),?\s*Verse\s+(\d+)", content, re.IGNORECASE):
                cited.add(f"{match.group(1)}.{match.group(2)}")
            for match in re.finditer(r"(\d+)\.(\d+)", content):
                cited.add(f"{match.group(1)}.{match.group(2)}")
    return cited


def ask_gita(
    question: str,
    llm_provider: str = None,
    chat_history: list = None,
    user_profile: dict = None,
) -> dict:
    """
    Ask GitaGuru a question with full conversational context.
    Avoids repeating verses already cited in the conversation.
    """
    if llm_provider:
        import src.config as cfg
        cfg.LLM_PROVIDER = llm_provider

    store = get_vector_store()
    llm = get_llm()

    # Find which verses were already cited
    cited_verses = _extract_cited_verses(chat_history)

    # Retrieve more candidates than needed, then filter out repeats
    fetch_count = TOP_K_RESULTS * 3
    raw_docs = store.max_marginal_relevance_search(question, k=fetch_count, fetch_k=fetch_count * 2, lambda_mult=0.5)

    # Filter: prefer verses NOT already cited
    fresh_docs = []
    fallback_docs = []
    for doc in raw_docs:
        meta = doc.metadata
        verse_id = f"{meta.get('chapter_number', '?')}.{meta.get('verse_number', '?')}"
        if verse_id not in cited_verses:
            fresh_docs.append(doc)
        else:
            fallback_docs.append(doc)

    # Use fresh docs first, fall back to cited ones if not enough
    docs = (fresh_docs + fallback_docs)[:TOP_K_RESULTS]

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
