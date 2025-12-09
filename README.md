# Personal Notes Search (Local RAG) — FastAPI + ChromaDB + Ollama + Streamlit

## Overview
A complete Retrieval-Augmented Generation (RAG) system using `FastAPI backend, Streamlit UI, ChromaDB vector storage, Sentence Transformers for embeddings, and optional Ollama LLM response generation gemma2:2b`. Fully instrumented with LangSmith for tracing, debugging, and analytics.
`
---

## 🚀 Features
📄 Upload notes (`TXT, PDF, MD`)
✂️ Recursive chunking (RecursiveCharacterTextSplitter)
🔍 High-quality embeddings (all-MiniLM-L6-v2)
🧠 Vector DB storage using ChromaDB
❓ Ask questions → retrieves top 3 relevant chunks
🤖 Optional LLM answering with Ollama (`llama3.2:3b`)
🟦 Professional tracing/debugging via LangSmith
🖥 Clean, modern Streamlit UI

## Project Structure

project/
│── app/
│   ├── main.py
│   ├── _init_.py
│   ├── embedded.py
│   ├── utils.py
│   ├── config.py
│── streamlit_app.py
│── run_all.py
│── requirements.txt
│── .env

## Create venv
python -m venv venv
venv\Scripts\activate  (Windows)
source venv/bin/activate (Mac/Linux)

## Install requirements
- Python 3.9+
- Install Python packages:
```bash
pip install -r requirements.txt
pip install langsmith

## Environment Variables (.env)
LANGSMITH_API_KEY=your_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=Personal_Notes_Search
CHROMA_DB_PATH=./chroma_db
## Start everything:
python run_all.py

##FastAPI Backend
uvicorn app.main:app 

##Streamlit UI
streamlit run streamlit_app.py