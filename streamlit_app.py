# File: streamlit_app.py
import streamlit as st
import requests
import os

# -----------------------------
# Backend URL
# -----------------------------
API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")

# -----------------------------
# Page Settings
# -----------------------------
st.set_page_config(
    page_title="📘 RAG Notes Search",
    layout="wide",
    page_icon="🤖",
)

# -----------------------------
# Custom CSS (ChatGPT UI Style)
# -----------------------------
st.markdown("""
<style>

html, body, [class*="css"]  {
    font-family: 'Segoe UI', sans-serif;
}

.chat-bubble-user {
    background-color: #DCF8C6;
    padding: 12px;
    border-radius: 10px;
    max-width: 90%;
    margin-bottom: 8px;
}

.chat-bubble-bot {
    background-color: #F1F0F0;
    padding: 12px;
    border-radius: 10px;
    max-width: 90%;
    margin-bottom: 8px;
    border-left: 4px solid #4B8BBE;
}

.box-card {
    background-color: #ffffff;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e6e6e6;
    margin-bottom: 12px;
}

.source-card {
    background-color: #fafafa;
    border-left: 4px solid #4B8BBE;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 10px;
}

h1, h2, h3, h4 {
    font-weight: 600;
}

.upload-box {
    border: 2px dashed #4B8BBE;
    padding: 20px;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# App Title
# -----------------------------
st.markdown("<h1 style='text-align:center;'>📘 RAG Personal Notes Search</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>Upload → Embed → Query your notes using AI + LangSmith tracing</p>", unsafe_allow_html=True)

# -----------------------------
# LangSmith Status
# -----------------------------
ls_enabled = os.environ.get("LANGCHAIN_TRACING_V2", "false")
st.info(f"LangSmith Tracing: **{ls_enabled}**")

# -----------------------------
# Backend Check
# -----------------------------
def backend_live():
    try:
        r = requests.get(f"{API_BASE}/")
        return r.status_code < 500
    except:
        return False

if not backend_live():
    st.error("❌ Backend not running. Start FastAPI: `uvicorn app.main:app --reload`")
    st.stop()

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3 = st.tabs([
    "📤 Upload Notes",
    "💬 Ask Question",
    "📜 Chat History"
])

# ======================================
# TAB 1 — UPLOAD NOTES
# ======================================
with tab1:
    st.markdown("<h2>📤 Upload Notes</h2>", unsafe_allow_html=True)
    st.markdown("Upload `.txt`, `.md`, `.pdf`")

    uploaded_files = st.file_uploader(
        "Upload Your Documents",
        accept_multiple_files=True,
        type=["txt", "md", "pdf"]
    )

    col1, col2 = st.columns([1,1])

    with col1:
        if st.button("📥 Upload Files", type="primary", use_container_width=True):
            if not uploaded_files:
                st.warning("⚠ Please select files first.")
            else:
                files = [
                    ("files", (f.name, f.getvalue(), f.type or "application/octet-stream"))
                    for f in uploaded_files
                ]
                try:
                    resp = requests.post(f"{API_BASE}/upload", files=files, timeout=30)
                    if resp.status_code == 200:
                        st.success("✅ Files uploaded & embedded!")
                        st.json(resp.json())
                    else:
                        st.error(f"❌ Upload failed: {resp.status_code}")
                except:
                    st.error("❌ Connection error during upload.")

    with col2:
        if st.button("🧹 Reset Notes & History", type="secondary", use_container_width=True):
            try:
                resp = requests.post(f"{API_BASE}/reset")
                if resp.status_code == 200:
                    st.success("🔄 Reset Completed")
                else:
                    st.error("❌ Reset failed")
            except:
                st.error("❌ Unable to reset backend.")

# ======================================
# TAB 2 — ASK QUESTION
# ======================================
with tab2:
    st.markdown("<h2>💬 Ask a Question</h2>", unsafe_allow_html=True)

    question = st.text_area("Your Question", height=120)
    use_ollama = st.checkbox("Use Ollama LLM (Local)")

    if st.button("🚀 Ask", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("⚠ Please type a question.")
        else:
            try:
                resp = requests.post(
                    f"{API_BASE}/query",
                    data={"question": question, "use_ollama": str(use_ollama).lower()},
                    timeout=40
                )
                if resp.status_code == 200:
                    result = resp.json()

                    # User message bubble
                    st.markdown(f"<div class='chat-bubble-user'>{question}</div>", unsafe_allow_html=True)

                    # Answer bubble
                    st.markdown(f"<div class='chat-bubble-bot'>{result.get('answer')}</div>", unsafe_allow_html=True)

                    # Sources
                    st.markdown("<h3>📚 Top Sources</h3>", unsafe_allow_html=True)
                    for src in result.get("sources", []):
                        st.markdown(
                            f"""
                            <div class="source-card">
                                <b>Source {src.get('source_index')} – {src.get('source')}</b>
                                <br><small>Relevance: {src.get('score'):.4f}</small>
                                <br><br>{src.get("text")}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                else:
                    st.error(f"❌ Query failed: {resp.status_code}")
            except:
                st.error("❌ Backend unreachable.")

# ======================================
# TAB 3 — CHAT HISTORY
# ======================================
with tab3:
    st.markdown("<h2>📜 Chat History</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])

    # Refresh history
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            try:
                resp = requests.get(f"{API_BASE}/history")
                if resp.status_code == 200:
                    history = resp.json().get("history", [])
                    st.markdown(f"Total Messages: **{len(history)}**")
                    for entry in reversed(history):
                        st.markdown(f"<div class='chat-bubble-user'><b>Q:</b> {entry['question']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='chat-bubble-bot'><b>A:</b> {entry['answer'][:1500]}</div>", unsafe_allow_html=True)
                else:
                    st.error("❌ Failed fetching history.")
            except:
                st.error("❌ History connection error.")

    # Clear history
    with col2:
        if st.button("🧹 Clear History", use_container_width=True):
            try:
                resp = requests.post(f"{API_BASE}/history/clear")
                if resp.status_code == 200:
                    st.success("🧹 History Cleared")
                else:
                    st.error("❌ Clear failed")
            except:
                st.error("❌ Couldn't clear history.")

