# File: run_all.py
import subprocess
import time
import sys
import os

# -------------------------------------------------------
# LangSmith Environment Setup (ADDED)
# -------------------------------------------------------
# You can hardcode OR rely on system environment variables.
# These lines ensure LangSmith tracing is active.
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
os.environ.setdefault("LANGCHAIN_PROJECT", "personal-notes-app")  # change if needed

# Optional: warn if no API key found
if "LANGCHAIN_API_KEY" not in os.environ:
    print("[WARN] LANGCHAIN_API_KEY is not set. LangSmith tracing will NOT work.")

print("LangSmith tracing:", os.environ.get("LANGCHAIN_TRACING_V2"))
print("LangSmith project:", os.environ.get("LANGCHAIN_PROJECT"))
print("Starting FastAPI and Streamlit with LangSmith enabled...\n")

# -------------------------------------------------------
# Start FastAPI (uvicorn)
# -------------------------------------------------------
fastapi = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

time.sleep(1)  # give uvicorn a moment

# -------------------------------------------------------
# Start Streamlit
# -------------------------------------------------------
streamlit = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "streamlit_app.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

print("Started FastAPI and Streamlit. Press Ctrl+C to stop.")

try:
    fastapi.wait()
    streamlit.wait()
except KeyboardInterrupt:
    print("\nStopping servers...")
    fastapi.terminate()
    streamlit.terminate()
