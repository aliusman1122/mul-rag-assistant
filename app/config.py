# File: app/config.py
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
LANGSMITH_API_KEY = os.getenv("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")
LANGSMITH_PROJECT = os.getenv("LANGCHAIN_PROJECT", "personal_report_search_app")

# Project root (assumes app/ is a subfolder)
ROOT = Path(__file__).resolve().parent.parent

# Directories & files
APP_DIR = ROOT / "app"
DATA_DIR = ROOT / "data"
CHROMA_DIR = ROOT / "chroma"
CHAT_HISTORY_FILE = ROOT / "chat_history.json"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Embedding model (HF sentence-transformers)
EMBED_MODEL = os.environ.get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Chunking / retrieval defaults (tunable via env)
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", 200))
TOP_K = int(os.environ.get("TOP_K", 3))

# Ollama model (if using local Ollama)
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")

# Chat history rotation limit
HISTORY_LIMIT = int(os.environ.get("HISTORY_LIMIT", 500))
