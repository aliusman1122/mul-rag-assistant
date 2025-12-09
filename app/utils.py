# File: app/utils.py
import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple , Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from pypdf import PdfReader
from langsmith import Client
from .config import (
    EMBED_MODEL,
    CHROMA_DIR,
    CHAT_HISTORY_FILE,
    DATA_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K,
    OLLAMA_MODEL,
    HISTORY_LIMIT,
)
# Initialize the LangSmith client
client = Client()

def get_client():
    return client

# --------------------------------------------------------------------
# LOGGING
# --------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------
# EMBEDDINGS LOADER
# --------------------------------------------------------------------
_embeddings = None
def get_embeddings():
    global _embeddings
    if _embeddings is None:
        logger.info(f"Loading embeddings model: {EMBED_MODEL}")
        _embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    return _embeddings

# --------------------------------------------------------------------
# CHROMA VECTORSTORE
# --------------------------------------------------------------------
_chroma_db: Optional[Chroma] = None

def get_chroma() -> Chroma:
    global _chroma_db
    if _chroma_db is None:
        _chroma_db = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=get_embeddings()
        )
    return _chroma_db

# --------------------------------------------------------------------
# CLEAN TEXT
# --------------------------------------------------------------------
def clean_text(text: str) -> str:
    if not text:
        return ""
    lines = [line.strip() for line in text.splitlines()]
    cleaned = []
    empty_line = False
    for line in lines:
        if not line:
            if not empty_line:
                cleaned.append("")
            empty_line = True
        else:
            cleaned.append(line)
            empty_line = False
    return "\n".join(cleaned).strip()

# --------------------------------------------------------------------
# LOAD FILE (TXT/MD/PDF)
# --------------------------------------------------------------------
def load_file_as_document(path: Path) -> Document:
    path = Path(path)
    if not path.exists():
        logger.warning(f"File missing: {path}")
        return Document(page_content="", metadata={"source": str(path)})

    text = ""
    try:
        if path.suffix.lower() in [".txt", ".md"]:
            text = path.read_text(encoding="utf-8", errors="ignore")
        elif path.suffix.lower() == ".pdf":
            reader = PdfReader(str(path))
            pages = [p.extract_text() or "" for p in reader.pages]
            text = "\n".join(pages)
        else:
            logger.warning(f"Unsupported file type: {path.suffix}")
    except Exception as e:
        logger.error(f"Failed to read file {path}: {e}")

    return Document(page_content=clean_text(text), metadata={"source": str(path)})

# --------------------------------------------------------------------
# CHUNK DOCUMENTS
# --------------------------------------------------------------------
def chunk_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " "]
    )
    chunks = []
    for doc in docs:
        for chunk in splitter.split_text(doc.page_content):
            cleaned = clean_text(chunk)
            if cleaned:
                chunks.append(Document(page_content=cleaned, metadata=doc.metadata))
    logger.info(f"Created {len(chunks)} chunks from {len(docs)} documents")
    return chunks

# --------------------------------------------------------------------
# ADD DOCUMENTS TO CHROMA
# --------------------------------------------------------------------
def add_documents_to_chroma(docs: List[Document]):
    if not docs:
        return
    try:
        db = get_chroma()
        db.add_documents(docs)
        logger.info(f"Added {len(docs)} documents to Chroma")
    except Exception as e:
        logger.error(f"Error adding documents to Chroma: {e}")

# --------------------------------------------------------------------
# SIMILARITY SEARCH
# --------------------------------------------------------------------
def similarity_search(query: str, k: int = TOP_K) -> List[Tuple[Document, float]]:
    try:
        db = get_chroma()
        return db.similarity_search_with_score(query, k=k)
    except Exception as e:
        logger.error(f"Similarity search failed: {e}")
        return []

# --------------------------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------------------------
def load_chat_history() -> List[dict]:
    try:
        if CHAT_HISTORY_FILE.exists():
            return json.loads(CHAT_HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to load chat history: {e}")
    return []
def append_to_history(entry: dict):
    try:
        history = load_chat_history()
        history.append(entry)
        history = history[-HISTORY_LIMIT:]  # enforce limit
        CHAT_HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to append chat history: {e}")

# --------------------------------------------------------------------
# OLLAMA CLI
# --------------------------------------------------------------------
from typing import Optional

def call_ollama_cli(prompt: str, model: str = OLLAMA_MODEL, timeout: int = 120) -> Optional[str]:

    try:
        proc = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout
        )
        if proc.returncode != 0:
            logger.error(f"Ollama CLI error: {proc.stderr.decode()}")
            return None
        return proc.stdout.decode("utf-8").strip()
    except Exception as e:
        logger.error(f"Error calling Ollama CLI: {e}")
        return None

# --------------------------------------------------------------------
# RESET ALL
# --------------------------------------------------------------------
def reset_all(delete_files: bool = True):
    try:
        shutil.rmtree(CHROMA_DIR, ignore_errors=True)
        Path(CHROMA_DIR).mkdir(parents=True, exist_ok=True)
        logger.info(f"Reset Chroma directory: {CHROMA_DIR}")
    except Exception as e:
        logger.error(f"Failed to reset Chroma directory: {e}")

    if delete_files:
        try:
            shutil.rmtree(DATA_DIR, ignore_errors=True)
            Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
            logger.info(f"Reset Data directory: {DATA_DIR}")
        except Exception as e:
            logger.error(f"Failed to reset Data directory: {e}")

    try:
        if CHAT_HISTORY_FILE.exists():
            CHAT_HISTORY_FILE.unlink()
            logger.info(f"Removed chat history file: {CHAT_HISTORY_FILE}")
    except Exception as e:
        logger.error(f"Failed to remove chat history file: {e}")
