# services/__init__.py
from .rag_service import RAGService, get_rag_service
from .chat_service import ChatService, get_chat_service
from .ingest_service import IngestService, get_ingest_service
from .scraper_service import UniversityScraper