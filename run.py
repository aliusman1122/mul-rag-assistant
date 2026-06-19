# =============================================================================
# FILE: run.py
# PURPOSE: Application start karne ka main script.
#          FastAPI backend aur Streamlit UI dono start karta hai.
#
# Run karne ka tareeqa:
#   python run.py
#
# Ya alag alag:
#   uvicorn api.main:app --reload --port 8000
#   streamlit run ui/streamlit_app.py --server.port 8501
# =============================================================================

import subprocess
import sys
import time
import os
import threading
import signal

def run_fastapi():
    """FastAPI backend server start karo."""
    print("🚀 Starting FastAPI backend on port 8000...")
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "api.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
        "--log-level", "info"
    ])


def run_streamlit():
    """Streamlit UI start karo."""
    time.sleep(3)  # FastAPI ke start hone ka wait karo
    print("🎨 Starting Streamlit UI on port 8501...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "ui/streamlit_app.py",
        "--server.port", "8501",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ])


def main():
    """Both servers ek saath start karo."""
    print("=" * 60)
    print("🎓 MUL AI Assistant - Starting...")
    print("=" * 60)
    print()
    print("📊 Services:")
    print("  🔧 FastAPI Backend: http://localhost:8000")
    print("  🌐 Streamlit UI:    http://localhost:8501")
    print("  📚 API Docs:        http://localhost:8000/docs")
    print()
    print("⏹️  Press Ctrl+C to stop all services")
    print("=" * 60)
    
    # Threads mein run karo
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    ui_thread = threading.Thread(target=run_streamlit, daemon=True)
    
    api_thread.start()
    ui_thread.start()
    
    try:
        # Main thread alive raho
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down servers...")
        sys.exit(0)


if __name__ == "__main__":
    main()