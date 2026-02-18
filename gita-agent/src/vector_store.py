"""
ChromaDB vector store — stores and queries Bhagavad Gita verse embeddings.
Auto-builds the collection from JSON data if it doesn't exist (e.g. on first deploy).
"""

import sys
import json
import chromadb
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from src.config import (
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    TOP_K_RESULTS,
    GITA_JSON_PATH,
    PSYCHOLOGY_JSON_PATH,
)
from src.embeddings import get_embedding_model


def _build_collection():
    """Build the ChromaDB collection from the JSON source files."""
    print("[VectorStore] Collection is empty — building from JSON data...")
    embedding_model = get_embedding_model()
    documents = []

    # Load Gita data
    with open(GITA_JSON_PATH, "r", encoding="utf-8") as f:
        gita_data = json.load(f)
    for chapter in gita_data["chapters"]:
        ch_num = chapter["chapter_number"]
        ch_name = chapter["chapter_name"]
        ch_name_hindi = chapter.get("chapter_name_hindi", "")
        ch_summary = chapter.get("chapter_summary", "")
        for verse in chapter["verses"]:
            v_num = verse["verse_number"]
            text = "\n".join([
                f"Chapter {ch_num}: {ch_name} ({ch_name_hindi})",
                f"Verse {v_num}",
                "",
                f"Sanskrit: {verse.get('sanskrit', '')}",
                f"Transliteration: {verse.get('transliteration', '')}",
                f"Hindi Translation: {verse.get('hindi_translation', '')}",
                f"English Translation: {verse.get('english_translation', '')}",
                f"Commentary: {verse.get('commentary', '')}",
                "",
                f"Chapter Summary: {ch_summary}",
            ])
            documents.append(Document(
                page_content=text,
                metadata={
                    "chapter_number": ch_num,
                    "verse_number": v_num,
                    "chapter_name": ch_name,
                    "chapter_name_hindi": ch_name_hindi,
                    "source": f"Bhagavad Gita {ch_num}.{v_num}",
                },
            ))

    # Load psychology data
    if Path(PSYCHOLOGY_JSON_PATH).exists():
        with open(PSYCHOLOGY_JSON_PATH, "r", encoding="utf-8") as f:
            psych_data = json.load(f)
        for book in psych_data["books"]:
            for concept in book["concepts"]:
                text = "\n".join([
                    f"Psychology — {book['title']} by {book['author']}",
                    f"Concept: {concept['concept']}",
                    f"Explanation: {concept['explanation']}",
                    f"Connection to Bhagavad Gita: {concept['gita_connection']}",
                    f"Practical Advice: {concept['practical_advice']}",
                ])
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "source": "Psychology",
                        "book_title": book["title"],
                        "author": book["author"],
                        "concept": concept["concept"],
                    },
                ))

    Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    print(f"[VectorStore] Built collection with {len(documents)} documents.")


def get_vector_store() -> Chroma:
    """Return the persisted ChromaDB vector store, auto-building it if empty."""
    embedding_model = get_embedding_model()
    store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embedding_model,
    )
    if store._collection.count() == 0:
        _build_collection()
        store = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=embedding_model,
        )
    return store


def similarity_search(query: str, k: int = TOP_K_RESULTS) -> list:
    """Search the vector store for the most relevant Gita verses."""
    store = get_vector_store()
    results = store.similarity_search_with_score(query, k=k)
    return results


def get_retriever(k: int = TOP_K_RESULTS):
    """Return a LangChain retriever using MMR for diverse results."""
    store = get_vector_store()
    return store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": k * 4, "lambda_mult": 0.5},
    )


def reset_vector_store():
    """Delete and recreate the ChromaDB collection."""
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}'.")
    except Exception:
        print(f"No existing collection '{COLLECTION_NAME}' to delete.")
