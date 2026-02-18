"""
Configuration for GitaGuru — Bhagavad Gita AI Agent.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Project paths ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
GITA_JSON_PATH = DATA_DIR / "bhagavad_gita.json"
PSYCHOLOGY_JSON_PATH = DATA_DIR / "psychology_books.json"

# ── Gemini settings ────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# ── Embedding settings ─────────────────────────────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ── ChromaDB settings ──────────────────────────────────────────
CHROMA_PERSIST_DIR = str(BASE_DIR / "chroma_db")
COLLECTION_NAME = "bhagavad_gita"

# ── Retrieval settings ─────────────────────────────────────────
TOP_K_RESULTS = 5

# ── LLM generation parameters ─────────────────────────────────
TEMPERATURE = 0.3
MAX_TOKENS = 2048
