"""
Configuration for GitaGuru — Bhagavad Gita AI Agent.
Centralizes all settings: LLM provider, model params, paths, and retrieval tuning.
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

# ── LLM Provider: "ollama" or "anthropic" ──────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

# Ollama settings
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Anthropic settings
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

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
