# File: streamlit_app.py
import streamlit as st
import requests
import os

# -----------------------------
# Backend base
# -----------------------------
API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="📘 Personal Notes Search",
    layout="wide",
    page_icon="📚"
)

st.title("📘 Personal Notes Search App")
st.markdown("A friendly, intelligent system to search, upload, and query your notes.")

# -----------------------------
# LangSmith status indicator
# -----------------------------
#ls_enabled = os.environ.get("LANGCHAIN_TRACING_V2", "false")
#st.info(f"LangSmith Tracing Enabled: **{ls_enabled}**")

# -----------------------------
# Backend check
# -----------------------------
def check_backend():
    try:
        r = requests.get(f"{API_BASE}/")
        return r.status_code < 500
    except requests.exceptions.RequestException:
        return False

if not check_backend():
    st.error("⚠️ Cannot reach backend. Start FastAPI: `uvicorn app.main:app --reload`")
    st.stop()

# -----------------------------
# Tabs: Upload, Query, History
# -----------------------------
tab1, tab2, tab3 = st.tabs(["📤 Upload Notes", "❓ Ask Question", "💬 Chat History"])

# -----------------------------
# Tab 1: Upload Notes
# -----------------------------
with tab1:
    st.header("Upload Notes")
    st.markdown("Supported formats: `.txt`, `.md`, `.pdf`")
    uploaded_files = st.file_uploader(
        "Select files to upload",
        accept_multiple_files=True,
        type=["txt", "md", "pdf"]
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Upload Files", type="primary"):
            if not uploaded_files:
                st.warning("⚠️ Select files first!")
            else:
                files = [("files", (f.name, f.getvalue(), f.type or "application/octet-stream")) for f in uploaded_files]
                try:
                    resp = requests.post(f"{API_BASE}/upload", files=files, timeout=30)
                    if resp.status_code == 200:
                        st.success("✅ Files uploaded successfully!")
                        st.json(resp.json())
                    else:
                        st.error(f"❌ Upload failed: {resp.status_code}\n{resp.text}")
                except requests.exceptions.RequestException:
                    st.error("❌ Failed to connect during upload.")

    with col2:
        if st.button("Reset All Notes & History", type="secondary"):
            try:
                resp = requests.post(f"{API_BASE}/reset", timeout=10)
                if resp.status_code == 200:
                    st.success("✅ System reset completed")
                else:
                    st.error("❌ Reset failed")
            except requests.exceptions.RequestException:
                st.error("❌ Failed to reset backend.")

# -----------------------------
# Tab 2: Ask Question
# -----------------------------
with tab2:
    st.header("Ask a Question")
    question = st.text_area("Type your question here", height=120)
    use_ollama = st.checkbox("Use Ollama LLM (requires Ollama)", value=False)
    
    if st.button("Ask", type="primary") and question.strip():
        data = {"question": question, "use_ollama": "true" if use_ollama else "false"}
        try:
            resp = requests.post(f"{API_BASE}/query", data=data, timeout=40)
            if resp.status_code == 200:
                j = resp.json()
                
                # Answer
                st.subheader("💡 Answer")
                st.markdown(f"<div style='background-color:#f0f2f6;padding:10px;border-radius:5px'>{j.get('answer')}</div>", unsafe_allow_html=True)
                
                # Sources
                st.subheader("📂 Top Sources")
                for src in j.get("sources", []):
                    st.markdown(
                        f"""
                        <div style='background-color:#ffffff;padding:8px;border-left:4px solid #4B8BBE;margin-bottom:5px;border-radius:5px'>
                        <b>Source {src.get('source_index')} — {src.get('source')}</b> (score: {src.get('score'):.4f})<br>
                        {src.get("text")}
                        </div>
                        """, unsafe_allow_html=True
                    )
            else:
                st.error(f"❌ Query failed: {resp.status_code}\n{resp.text}")
        except requests.exceptions.RequestException:
            st.error("❌ Failed to contact backend for query.")

# -----------------------------
# Tab 3: Chat History
# -----------------------------
with tab3:
    st.header("Chat History")
    col1, col2 = st.columns([1,1])
    
    with col1:
        if st.button("Refresh History"):
            try:
                resp = requests.get(f"{API_BASE}/history", timeout=15)
                if resp.status_code == 200:
                    hist = resp.json().get("history", [])
                    st.write(f"Total entries: **{len(hist)}**")
                    for i, entry in enumerate(reversed(hist), 1):
                        st.markdown(f"### {i}. Q: {entry.get('question','')}")
                        st.markdown(f"A: {entry.get('answer','')[:1500]}")
                        st.markdown("---")
                else:
                    st.error("❌ Could not fetch history")
            except requests.exceptions.RequestException:
                st.error("❌ Failed fetching history.")
    
    with col2:
        if st.button("Clear History"):
            try:
                resp = requests.post(f"{API_BASE}/history/clear", timeout=10)
                if resp.status_code == 200:
                    st.success("✅ History cleared")
                else:
                    st.error("❌ Clear history failed")
            except requests.exceptions.RequestException:
                st.error("❌ Failed to clear history.")
