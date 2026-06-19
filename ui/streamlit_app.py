# =============================================================================
# FILE: ui/streamlit_app.py
# PURPOSE: Professional Streamlit web interface.
#          Yeh user-facing chatbot UI hai.
#
# ⚠️  NAYI UNIVERSITY KE LIYE: Sirf config/branding.py change karo!
#     UI code same rahega, colors aur text change ho jayenge.
# =============================================================================

import streamlit as st
import requests
import os
import sys

# Project root ko Python path mein add karo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.branding import (
    APP_TITLE, APP_SUBTITLE, APP_ICON,
    UNIVERSITY_NAME, UNIVERSITY_SHORT_NAME,
    PRIMARY_COLOR, SECONDARY_COLOR,
    BOT_NAME, BOT_EMOJI,
    WELCOME_MESSAGE, EXAMPLE_QUESTIONS,
    FOOTER_TEXT, CONTACT_EMAIL
)

# =============================================================================
# Backend URL Configuration
# =============================================================================
# Production mein environment variable se le
API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

# =============================================================================
# Page Configuration - SABSE PEHLE HONA CHAHIYE
# =============================================================================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# Custom CSS - Professional University Theme
# ⚠️  Colors config/branding.py se aa rahe hain
# =============================================================================
st.markdown(f"""
<style>
    /* ---- Global Styles ---- */
    html, body, [class*="css"] {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* ---- Main App Background ---- */
    .main {{
        background-color: #F4F7FB;
    }}
    
    /* ---- Header / Title ---- */
    .app-header {{
        background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, #2E5C8A 100%);
        padding: 25px 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(30, 58, 95, 0.3);
    }}
    .app-header h1 {{
        color: white !important;
        font-size: 2.2em;
        font-weight: 700;
        margin: 0;
    }}
    .app-header p {{
        color: #C8D8E8;
        font-size: 1.1em;
        margin: 5px 0 0 0;
    }}
    
    /* ---- Chat Bubbles ---- */
    .chat-user {{
        background-color: {PRIMARY_COLOR};
        color: white;
        padding: 14px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 85%;
        margin-left: auto;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        font-size: 0.95em;
        line-height: 1.5;
    }}
    .chat-bot {{
        background: white;
        color: #2C2C2C;
        padding: 14px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 85%;
        border-left: 4px solid {SECONDARY_COLOR};
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        font-size: 0.95em;
        line-height: 1.6;
    }}
    
    /* ---- Source Cards ---- */
    .source-card {{
        background: white;
        border-left: 4px solid {PRIMARY_COLOR};
        padding: 14px 16px;
        border-radius: 8px;
        margin: 8px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }}
    .source-card .source-title {{
        font-weight: 700;
        color: {PRIMARY_COLOR};
        font-size: 0.9em;
        margin-bottom: 6px;
    }}
    .source-card .source-text {{
        color: #555;
        font-size: 0.85em;
        line-height: 1.5;
    }}
    
    /* ---- Stats Badge ---- */
    .stat-badge {{
        background: {PRIMARY_COLOR};
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 600;
        display: inline-block;
    }}
    
    /* ---- Example Questions ---- */
    .example-q {{
        background: #EEF2F7;
        padding: 8px 14px;
        border-radius: 8px;
        margin: 4px 0;
        cursor: pointer;
        font-size: 0.9em;
        border: 1px solid #D0DAE8;
        color: {PRIMARY_COLOR};
    }}
    .example-q:hover {{
        background: {PRIMARY_COLOR};
        color: white;
    }}
    
    /* ---- Sidebar ---- */
    .css-1d391kg {{
        background-color: #F0F4F8;
    }}
    
    /* ---- Footer ---- */
    .footer {{
        text-align: center;
        padding: 15px;
        color: #888;
        font-size: 0.8em;
        border-top: 1px solid #E0E0E0;
        margin-top: 30px;
    }}
    
    /* ---- Buttons ---- */
    .stButton > button {{
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s;
    }}
    
    /* ---- Status indicator ---- */
    .status-dot-green {{
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #28a745;
        border-radius: 50%;
        margin-right: 6px;
        animation: pulse 2s infinite;
    }}
    .status-dot-red {{
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #dc3545;
        border-radius: 50%;
        margin-right: 6px;
    }}
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
        100% {{ opacity: 1; }}
    }}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# Helper Functions
# =============================================================================
def check_backend() -> dict:
    """Backend server ka status check karo."""
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=5)
        if resp.status_code == 200:
            return resp.json()
        return {"status": "error"}
    except:
        return {"status": "offline"}


def send_query(question: str, use_llm: bool = True) -> dict:
    """Backend ko query bhejo."""
    try:
        resp = requests.post(
            f"{API_BASE}/api/query",
            data={
                "question": question,
                "use_llm": str(use_llm).lower()
            },
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json()
        return {
            "answer": f"Error: {resp.status_code}",
            "sources": [],
            "status": "error"
        }
    except requests.exceptions.Timeout:
        return {
            "answer": "⏱️ Request timed out. Please try again.",
            "sources": [],
            "status": "timeout"
        }
    except Exception as e:
        return {
            "answer": f"Connection error: {str(e)}",
            "sources": [],
            "status": "error"
        }


# =============================================================================
# Session State Initialize karo
# =============================================================================
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "db_ready" not in st.session_state:
    st.session_state.db_ready = False


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    # Logo / University Name
    st.markdown(f"""
    <div style="text-align:center; padding: 10px 0 20px 0;">
        <div style="font-size: 2.5em;">{BOT_EMOJI}</div>
        <div style="font-weight: 700; color: {PRIMARY_COLOR}; font-size: 1.1em;">
            {UNIVERSITY_SHORT_NAME} AI Assistant
        </div>
        <div style="color: #888; font-size: 0.8em;">{UNIVERSITY_NAME}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Server Status
    st.markdown("**🔌 Server Status**")
    backend_status = check_backend()
    
    if backend_status.get("status") in ["healthy", "running"]:
        total_docs = backend_status.get("total_documents", 0)
        db_ready = backend_status.get("database_ready", False)
        st.session_state.db_ready = db_ready
        
        if db_ready:
            st.markdown(
                f'<span class="status-dot-green"></span>'
                f'**Online** | {total_docs} chunks loaded',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<span class="status-dot-red"></span>'
                f'**Online** | ⚠️ DB Empty - Run ingestion!',
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            '<span class="status-dot-red"></span>**Offline**',
            unsafe_allow_html=True
        )
        st.error("Start backend: `uvicorn api.main:app --reload`")
    
    st.divider()
    
    # LLM Settings
    st.markdown("**⚙️ Settings**")
    use_llm = st.toggle("Use AI (LLM)", value=True, help="AI ke saath better answers milenge")
    k_docs = st.slider("Source documents", 2, 8, 4, help="Kitne sources use karne hain")
    
    st.divider()
    
    # Example Questions
    st.markdown("**💡 Example Questions**")
    for q in EXAMPLE_QUESTIONS[:4]:
        if st.button(q, key=f"ex_{q[:20]}", use_container_width=True):
            st.session_state.pending_question = q
    
    st.divider()
    
    # Quick Actions
    st.markdown("**🔧 Quick Actions**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Contact Info
    st.divider()
    st.markdown(f"""
    **📞 Contact MUL**
    - 📧 {CONTACT_EMAIL}
    - 🌐 [mul.edu.pk](https://www.mul.edu.pk)
    """)


# =============================================================================
# MAIN CONTENT AREA
# =============================================================================

# Header
st.markdown(f"""
<div class="app-header">
    <h1>{BOT_EMOJI} {UNIVERSITY_SHORT_NAME} AI Information Assistant</h1>
    <p>{APP_SUBTITLE}</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📤 Upload Documents", "📊 About"])


# =============================================================================
# TAB 1: CHAT
# =============================================================================
with tab1:
    
    # Welcome message (sirf pehli baar)
    if not st.session_state.chat_messages:
        st.markdown(f"""
        <div class="chat-bot">
            {WELCOME_MESSAGE}
        </div>
        """, unsafe_allow_html=True)
    
    # Chat history display
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-user">👤 {msg["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="chat-bot">{BOT_EMOJI} {msg["content"]}</div>',
                unsafe_allow_html=True
            )
            
            # Sources show karo
            if msg.get("sources"):
                with st.expander(f"📚 {len(msg['sources'])} Sources Used", expanded=False):
                    for src in msg["sources"]:
                        st.markdown(f"""
                        <div class="source-card">
                            <div class="source-title">
                                Source {src.get('source_index', '?')} — {src.get('source', 'Document')}
                                <span style="float:right; color:#888; font-size:0.85em;">
                                    Score: {src.get('score', 0):.3f}
                                </span>
                            </div>
                            <div class="source-text">{src.get('text', '')[:400]}...</div>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Input area
    st.divider()
    
    # Check if example question was clicked in sidebar
    pending_q = st.session_state.pop("pending_question", None)
    
    # User input
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        
        with col_input:
            user_input = st.text_input(
                "Ask a question...",
                value=pending_q or "",
                placeholder=f"Ask anything about {UNIVERSITY_SHORT_NAME}...",
                label_visibility="collapsed"
            )
        
        with col_btn:
            submit = st.form_submit_button(
                "Send 🚀",
                use_container_width=True,
                type="primary"
            )
    
    # Process the question
    if submit and user_input and user_input.strip():
        
        # Check if backend is ready
        if not st.session_state.db_ready:
            st.warning("⚠️ Database is not ready! Please ingest documents first.")
        else:
            # User message add karo
            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_input.strip()
            })
            
            # Loading spinner
            with st.spinner(f"🤔 {BOT_NAME} is thinking..."):
                result = send_query(user_input.strip(), use_llm=use_llm)
            
            # Bot response add karo
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": result.get("answer", "Sorry, I couldn't generate a response."),
                "sources": result.get("sources", [])
            })
            
            # Page refresh
            st.rerun()


# =============================================================================
# TAB 2: UPLOAD DOCUMENTS
# =============================================================================
with tab2:
    st.markdown(f"### 📤 Upload Documents to {UNIVERSITY_SHORT_NAME} Knowledge Base")
    st.info("Upload university documents (PDF, TXT, MD) to enhance the AI's knowledge.")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Select documents to upload",
        accept_multiple_files=True,
        type=["pdf", "txt", "md"],
        help="Supported formats: PDF, TXT, Markdown"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Upload & Process", type="primary", use_container_width=True):
            if not uploaded_files:
                st.warning("Please select files first!")
            else:
                with st.spinner("Processing files..."):
                    files_to_send = [
                        ("files", (f.name, f.getvalue(), f.type or "application/octet-stream"))
                        for f in uploaded_files
                    ]
                    try:
                        resp = requests.post(
                            f"{API_BASE}/api/upload",
                            files=files_to_send,
                            timeout=120
                        )
                        if resp.status_code == 200:
                            result = resp.json()
                            st.success(f"✅ Upload successful!")
                            st.json(result)
                        else:
                            st.error(f"❌ Upload failed: {resp.status_code}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
    
    with col2:
        if st.button("🔄 Refresh Database", use_container_width=True):
            with st.spinner("Running ingestion..."):
                try:
                    resp = requests.post(f"{API_BASE}/api/ingest", timeout=300)
                    if resp.status_code == 200:
                        st.success("✅ Ingestion complete!")
                        st.json(resp.json())
                    else:
                        st.error(f"❌ Failed: {resp.status_code}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    with col3:
        if st.button("🗑️ Reset Database", type="secondary", use_container_width=True):
            if st.session_state.get("confirm_reset", False):
                with st.spinner("Resetting..."):
                    try:
                        resp = requests.post(f"{API_BASE}/api/reset", timeout=30)
                        if resp.status_code == 200:
                            st.success("✅ Database reset!")
                        else:
                            st.error("❌ Reset failed!")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                st.session_state.confirm_reset = False
            else:
                st.session_state.confirm_reset = True
                st.warning("⚠️ Click again to confirm reset!")


# =============================================================================
# TAB 3: ABOUT
# =============================================================================
with tab3:
    st.markdown(f"### About {UNIVERSITY_SHORT_NAME} AI Assistant")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **🏫 University:** {UNIVERSITY_NAME}
        
        **🤖 Technology Stack:**
        - 🔍 **Retrieval:** ChromaDB + Semantic Search
        - 🧠 **Embeddings:** Sentence Transformers
        - ⚡ **LLM:** Groq (LLaMA 3)
        - 🌐 **Backend:** FastAPI
        - 🎨 **UI:** Streamlit
        
        **📊 Capabilities:**
        - Answer admission queries
        - Fee structure information
        - Program eligibility details
        - Contact information
        """)
    
    with col2:
        # Database stats
        try:
            resp = requests.get(f"{API_BASE}/health", timeout=5)
            if resp.status_code == 200:
                stats = resp.json()
                
                st.markdown("**📊 Database Statistics:**")
                st.metric("Documents in KB", stats.get("total_documents", 0))
                st.metric("Status", "🟢 Active" if stats.get("database_ready") else "🔴 Empty")
                st.metric("LLM Provider", stats.get("llm_provider", "N/A"))
        except:
            st.warning("Backend offline")
    
    # Architecture info
    st.markdown("---")
    st.markdown("### 🏗️ RAG Architecture")
    st.markdown("""
    ```
    User Query → Embedding → Vector Search → Retrieved Context
                                                     ↓
                              LLM Answer ← System Prompt + Context
    ```
    
    This is a **Retrieval-Augmented Generation (RAG)** system that:
    1. Stores university documents as semantic vectors
    2. Finds relevant information for each question
    3. Uses an AI model to generate helpful answers
    """)


# =============================================================================
# FOOTER
# =============================================================================
st.markdown(f"""
<div class="footer">
    {FOOTER_TEXT} | 
    Built with ❤️ using Python, FastAPI & Streamlit
</div>
""", unsafe_allow_html=True)