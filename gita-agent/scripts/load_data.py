#!/usr/bin/env python3
"""
load_data.py — Process Bhagavad Gita JSON and load into ChromaDB.

Usage:
    python scripts/load_data.py           # Load data into ChromaDB
    python scripts/load_data.py --reset   # Clear existing data and reload
"""

import sys
import json
import argparse
from pathlib import Path

# Add project root to path so we can import src modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import GITA_JSON_PATH, PSYCHOLOGY_JSON_PATH, COLLECTION_NAME, CHROMA_PERSIST_DIR
from src.embeddings import get_embedding_model
from src.vector_store import reset_vector_store
from langchain_community.vectorstores import Chroma
from langchain.schema import Document


def load_gita_json(filepath: Path) -> dict:
    """Read the Bhagavad Gita JSON file."""
    print(f"[1/4] Reading Gita data from {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    total_chapters = len(data["chapters"])
    total_verses = sum(len(ch["verses"]) for ch in data["chapters"])
    print(f"       Found {total_chapters} chapters, {total_verses} verses.")
    return data


def create_documents(data: dict) -> list[Document]:
    """
    Convert each verse into a LangChain Document.
    Each document contains the full verse text (Sanskrit, translations, commentary)
    and metadata for filtering/citation.
    """
    print("[2/4] Creating document chunks (one per verse)...")
    documents = []

    for chapter in data["chapters"]:
        ch_num = chapter["chapter_number"]
        ch_name = chapter["chapter_name"]
        ch_name_hindi = chapter.get("chapter_name_hindi", "")
        ch_summary = chapter.get("chapter_summary", "")

        for verse in chapter["verses"]:
            v_num = verse["verse_number"]

            # Combine all verse fields into a rich text block
            text_parts = [
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
            ]
            page_content = "\n".join(text_parts)

            metadata = {
                "chapter_number": ch_num,
                "verse_number": v_num,
                "chapter_name": ch_name,
                "chapter_name_hindi": ch_name_hindi,
                "source": f"Bhagavad Gita {ch_num}.{v_num}",
            }

            documents.append(Document(page_content=page_content, metadata=metadata))

    print(f"       Created {len(documents)} document chunks.")
    return documents


def load_psychology_json(filepath: Path) -> dict:
    """Read the psychology books JSON file."""
    print(f"[P1] Reading psychology books from {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    total_books = len(data["books"])
    total_concepts = sum(len(b["concepts"]) for b in data["books"])
    print(f"       Found {total_books} books, {total_concepts} concepts.")
    return data


def create_psychology_documents(data: dict) -> list[Document]:
    """Convert each psychology concept into a LangChain Document."""
    print("[P2] Creating psychology document chunks...")
    documents = []

    for book in data["books"]:
        title = book["title"]
        author = book["author"]

        for concept in book["concepts"]:
            text_parts = [
                f"Psychology — {title} by {author}",
                f"Concept: {concept['concept']}",
                f"Explanation: {concept['explanation']}",
                f"Connection to Bhagavad Gita: {concept['gita_connection']}",
                f"Practical Advice: {concept['practical_advice']}",
            ]
            page_content = "\n".join(text_parts)

            metadata = {
                "source": "Psychology",
                "book_title": title,
                "author": author,
                "concept": concept["concept"],
            }

            documents.append(Document(page_content=page_content, metadata=metadata))

    print(f"       Created {len(documents)} psychology chunks.")
    return documents


def store_in_chromadb(documents: list[Document]):
    """Generate embeddings and store documents in ChromaDB."""
    print("[3/4] Generating embeddings and storing in ChromaDB...")
    print(f"       Persist directory: {CHROMA_PERSIST_DIR}")
    print(f"       Collection name:   {COLLECTION_NAME}")

    embedding_model = get_embedding_model()

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
    )

    print(f"       Stored {len(documents)} documents in ChromaDB.")
    return vectorstore


def main():
    parser = argparse.ArgumentParser(description="Load Bhagavad Gita data into ChromaDB")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear existing ChromaDB collection before loading",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  GitaGuru — Data Loader")
    print("=" * 60)

    # Reset if requested
    if args.reset:
        print("[0/4] Resetting vector store...")
        reset_vector_store()

    # Load Gita data
    data = load_gita_json(GITA_JSON_PATH)
    gita_docs = create_documents(data)

    # Load psychology data
    psych_data = load_psychology_json(PSYCHOLOGY_JSON_PATH)
    psych_docs = create_psychology_documents(psych_data)

    # Combine and store all documents
    all_documents = gita_docs + psych_docs
    store_in_chromadb(all_documents)

    # Final stats
    print("[4/4] Done!")
    print(f"       Gita verses loaded:      {len(gita_docs)}")
    print(f"       Psychology concepts loaded: {len(psych_docs)}")
    print(f"       Total documents:          {len(all_documents)}")
    print(f"       ChromaDB location:   {CHROMA_PERSIST_DIR}")
    print(f"       Collection:          {COLLECTION_NAME}")
    print("=" * 60)
    print("  Ready! Run the app with: streamlit run app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
