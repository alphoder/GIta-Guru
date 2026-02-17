"""
Embedding model setup using HuggingFace sentence-transformers.
Uses all-MiniLM-L6-v2 — a lightweight, fast model that runs locally.
"""

from langchain_community.embeddings import HuggingFaceEmbeddings
from src.config import EMBEDDING_MODEL


def get_embedding_model() -> HuggingFaceEmbeddings:
    """Initialize and return the HuggingFace embedding model."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
