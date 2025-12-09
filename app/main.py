# File: app/main.py

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import logging
from typing import List, Optional

from langsmith import traceable  # ⬅️ ADDED

from .config import DATA_DIR, TOP_K, OLLAMA_MODEL, CHAT_HISTORY_FILE
from .utils import (
    load_file_as_document,
    chunk_documents,
    add_documents_to_chroma,
    similarity_search,
    call_ollama_cli,
    append_to_history,
    load_chat_history,
    reset_all,
)

# -----------------------------------------------------------
# Initialize FastAPI + Logger
# -----------------------------------------------------------
app = FastAPI(title="Personal Notes Search App")

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

# Allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------
# Background Worker (traceable)
# -----------------------------------------------------------
@traceable(name="process_and_index_files")  # ⬅️ ADDED
def process_and_index_files(file_paths: List[str]):
    try:
        docs = [load_file_as_document(Path(f)) for f in file_paths]
        chunks = chunk_documents(docs)
        add_documents_to_chroma(chunks)

        logger.info("[Background] Indexed %d chunks from %d files.", len(chunks), len(file_paths))
    except Exception:
        logger.exception("[Background] Error processing files")


@app.get("/")
async def root():
    return {"message": "Personal Notes Search API is running."}


# -----------------------------------------------------------
# UPLOAD DOCUMENTS
# -----------------------------------------------------------
@app.post("/upload")
@traceable(name="upload_files")  # ⬅️ ADDED
async def upload(files: List[UploadFile] = File(...), background_tasks: BackgroundTasks = None) -> JSONResponse:
    saved_files = []
    try:
        Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

        for f in files:
            dest = Path(DATA_DIR) / f.filename

            # Avoid conflicts
            if dest.exists():
                base = dest.stem
                suff = dest.suffix
                i = 1
                while True:
                    candidate = dest.with_name(f"{base}_{i}{suff}")
                    if not candidate.exists():
                        dest = candidate
                        break
                    i += 1

            with open(dest, "wb") as out_file:
                shutil.copyfileobj(f.file, out_file)

            saved_files.append(str(dest))

        # Background Indexing
        if background_tasks:
            background_tasks.add_task(process_and_index_files, saved_files)
        else:
            process_and_index_files(saved_files)

        return JSONResponse({"status": "ok", "files_saved": saved_files})

    except Exception:
        logger.exception("Failed to upload files")
        return JSONResponse({"status": "error", "message": "Failed to upload files"}, status_code=500)


# -----------------------------------------------------------
# Q/A ENDPOINT (LangSmith wrapped)
# -----------------------------------------------------------
@app.post("/query")
@traceable(name="query_notes")  # ⬅️ ADDED
async def query(
    question: str = Form(...),
    use_ollama: Optional[bool] = Form(False)
) -> JSONResponse:
    try:
        # Search top-K
        results = similarity_search(question, k=TOP_K)

        if not results:
            return JSONResponse(
                {"status": "no_results", "message": "No relevant notes found."},
                status_code=400
            )

        combined_text = "\n\n".join([doc.page_content for doc, _ in results[:TOP_K]])

        final_prompt = f"""
You are a helpful, friendly assistant.

Below is context from the user's personal notes. Use it when relevant.
If the context doesn't help, answer naturally using your own knowledge.

Retrieved Notes:
{combined_text}

Question: {question}

Answer:
"""

        answer = None
        used_ollama = False

        # Call Ollama (traced)
        if use_ollama:
            answer = call_ollama_cli(final_prompt, model=OLLAMA_MODEL)
            if answer:
                used_ollama = True

        # Fallback
        if not answer:
            fallback_chunks = results[:3]
            fallback_text = "\n\n".join([doc.page_content for doc, _ in fallback_chunks])
            answer = (fallback_text[:2000] + "...") if len(fallback_text) > 2000 else fallback_text

            if not answer:
                answer = "No answer could be generated."

        sources = [
            {
                "source_index": idx,
                "source": doc.metadata.get("source"),
                "text": doc.page_content,
                "score": score,
            }
            for idx, (doc, score) in enumerate(results[:TOP_K])
        ]

        # Save Q/A
        append_to_history({
            "question": question,
            "answer": answer
        })

        return JSONResponse({
            "answer": answer,
            "sources": sources,
            "used_ollama": used_ollama
        })

    except Exception:
        logger.exception("Error in /query")
        return JSONResponse({"status": "error", "message": "Query processing failed"}, status_code=500)


# -----------------------------------------------------------
# HISTORY
# -----------------------------------------------------------
@app.get("/history")
async def history() -> JSONResponse:
    try:
        return JSONResponse({"history": load_chat_history()})
    except Exception:
        logger.exception("Failed loading history")
        return JSONResponse({"status": "error"}, status_code=500)


@app.post("/history/clear")
async def clear_history() -> JSONResponse:
    try:
        if Path(CHAT_HISTORY_FILE).exists():
            Path(CHAT_HISTORY_FILE).unlink()
        return JSONResponse({"status": "ok"})
    except Exception:
        logger.exception("Failed to clear history")
        return JSONResponse({"status": "error"}, status_code=500)


# -----------------------------------------------------------
# SYSTEM RESET
# -----------------------------------------------------------
@app.post("/reset")
async def reset(delete_files: bool = Form(True)) -> JSONResponse:
    try:
        reset_all(delete_files=delete_files)
        return JSONResponse({"status": "ok"})
    except Exception:
        logger.exception("Failed system reset")
        return JSONResponse({"status": "error"}, status_code=500)
