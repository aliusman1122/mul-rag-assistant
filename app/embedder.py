# File: embedder.py
from sentence_transformers import SentenceTransformer
from langsmith import traceable   # ✅ LangSmith tracing

# Load model once for quick local testing
model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Add LangSmith tracing
@traceable(name="Embed Text")
def embed_text(text: str):
    return model.encode(text)

if __name__ == "__main__":
    text = "Hello, this is a test sentence."

    # ❗ NEW: use traced function
    emb = embed_text(text)          # ✅ Now tracked in LangSmith

    print("Embedding length:", len(emb))
    print(emb[:10])
