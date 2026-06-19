# =============================================================================
# FILE: config/settings.py
# PURPOSE: Yeh file poore project ki settings control karti hai.
#          Nayi university ke liye sirf yeh file aur branding.py change karni hai.
# =============================================================================

import os
from dotenv import load_dotenv

# .env file se variables load karo
load_dotenv()

# =============================================================================
# ⚙️  LLM (AI Model) SETTINGS
# Agar nayi university ke liye kaam kar rahe ho, sirf API key change karo
# =============================================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")          # Groq API key (free hai!)
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192") # Default AI model

# OpenAI support bhi rakhi hai (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# LLM Provider: "groq" ya "openai" ya "ollama"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

# Ollama settings (local LLM ke liye)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# =============================================================================
# 🔍 EMBEDDING SETTINGS
# Yeh model text ko numbers (vectors) mein convert karta hai
# Nayi university ke liye change karne ki zaroorat NAHIN
# =============================================================================
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"  # Best free embedding model
)

# =============================================================================
# 🗄️  VECTOR DATABASE SETTINGS
# ChromaDB hamara local vector database hai
# =============================================================================
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "university_docs")

# =============================================================================
# 📄 DOCUMENT PROCESSING SETTINGS
# PDF aur text ko chunks mein todne ki settings
# =============================================================================
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))      # Har chunk ka size (characters)
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100")) # Chunks ke beech overlap

# =============================================================================
# 🔎 RETRIEVAL SETTINGS
# Query karte waqt kitne documents dhundne hain
# =============================================================================
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "4"))  # Top 4 results return karo
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))

# =============================================================================
# 🌐 WEB SCRAPING SETTINGS
# ⚠️  NAYI UNIVERSITY KE LIYE YEH ZAROOR CHANGE KARO
# =============================================================================
SCRAPE_URLS = os.getenv("SCRAPE_URLS", "").split(",") if os.getenv("SCRAPE_URLS") else [
    # Default: Minhaj University pages
    # Nayi university ke liye yeh list change karo
    "https://www.mul.edu.pk/en/admissions-open",
    "https://www.mul.edu.pk/en/about-us",
    "https://www.mul.edu.pk/en/academics",
    "https://www.mul.edu.pk/en/contact-us",
]

# =============================================================================
# 📁 DATA PATHS
# =============================================================================
PDF_DATA_PATH = os.getenv("PDF_DATA_PATH", "./data/pdfs")
SCRAPED_DATA_PATH = os.getenv("SCRAPED_DATA_PATH", "./data/scraped")
PROCESSED_DATA_PATH = os.getenv("PROCESSED_DATA_PATH", "./data/processed")

# =============================================================================
# 🔗 API SETTINGS
# =============================================================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"

# =============================================================================
# 📊 LANGSMITH SETTINGS (Tracing ke liye)
# =============================================================================
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "MUL-RAG-Assistant")

# =============================================================================
# 💬 CHAT SETTINGS
# =============================================================================
CHAT_HISTORY_FILE = os.getenv("CHAT_HISTORY_FILE", "./data/chat_history.json")
MAX_HISTORY_LENGTH = int(os.getenv("MAX_HISTORY_LENGTH", "50"))