"""
ChromaDB vector store — stores and queries Bhagavad Gita verse embeddings.
"""

import chromadb
from langchain_community.vectorstores import Chroma
from src.config import CHROMA_PERSIST_DIR, COLLECTION_NAME, TOP_K_RESULTS
from src.embeddings import get_embedding_model


def get_vector_store() -> Chroma:
    """Return the persisted ChromaDB vector store for the Gita collection."""
    embedding_model = get_embedding_model()
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embedding_model,
    )


def similarity_search(query: str, k: int = TOP_K_RESULTS) -> list:
    """Search the vector store for the most relevant Gita verses."""
    store = get_vector_store()
    results = store.similarity_search_with_score(query, k=k)
    return results


def get_retriever(k: int = TOP_K_RESULTS):
    """Return a LangChain retriever backed by ChromaDB."""
    store = get_vector_store()
    return store.as_retriever(search_kwargs={"k": k})


def reset_vector_store():
    """Delete and recreate the ChromaDB collection."""
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}'.")
    except Exception:
        print(f"No existing collection '{COLLECTION_NAME}' to delete.")
