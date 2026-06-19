# =============================================================================
# FILE: api/main.py
# PURPOSE: FastAPI application ka main entry point.
#          Yeh backend server hai jo UI se requests receive karta hai.
#
# Nayi university ke liye: Usually change ki zaroorat NAHIN
#          Sirf branding aur description change karo
# =============================================================================

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import query, upload, history, health
from config.branding import UNIVERSITY_NAME, BOT_NAME, BOT_DESCRIPTION

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Application Startup aur Shutdown Events
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    App startup aur shutdown ke waqt kya karna hai.
    Startup: Services initialize karo
    Shutdown: Cleanup karo
    """
    # Startup
    logger.info(f"🚀 Starting {BOT_NAME}...")
    logger.info(f"🏫 University: {UNIVERSITY_NAME}")
    
    # Services warm up karo (embedding model load hoga)
    try:
        from services import get_rag_service, get_chat_service
        rag_service = get_rag_service()
        chat_service = get_chat_service()
        
        if rag_service.is_ready():
            db_stats = rag_service.get_stats()
            docs = db_stats.get("database", {}).get("total_documents", 0)
            logger.info(f"✅ Vector DB ready with {docs} chunks")
        else:
            logger.warning("⚠️  Vector DB is empty! Run ingestion first:")
            logger.warning("    python scripts/ingest.py")
    
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
    
    logger.info("✅ Server ready!")
    
    yield  # Server chal raha hai
    
    # Shutdown
    logger.info("👋 Server shutting down...")


# =============================================================================
# FastAPI App Create karo
# =============================================================================
app = FastAPI(
    title=f"{UNIVERSITY_NAME} AI Assistant API",
    description=BOT_DESCRIPTION,
    version="2.0.0",
    docs_url="/docs",       # Swagger UI: http://localhost:8000/docs
    redoc_url="/redoc",     # ReDoc UI: http://localhost:8000/redoc
    lifespan=lifespan
)

# =============================================================================
# CORS Middleware - Browser se requests allow karo
# =============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Production mein specific origins dalo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Routes Register karo
# =============================================================================
app.include_router(health.router, tags=["Health"])
app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(history.router, prefix="/api", tags=["History"])

# Legacy routes (backward compatibility - purani code ke saath kaam kare)
app.include_router(query.router, tags=["Legacy"])
app.include_router(upload.router, tags=["Legacy"])
app.include_router(history.router, tags=["Legacy"])


# =============================================================================
# Root endpoint
# =============================================================================
@app.get("/")
async def root():
    """Root endpoint - server health check."""
    return {
        "status": "running",
        "name": BOT_NAME,
        "university": UNIVERSITY_NAME,
        "version": "2.0.0",
        "docs": "/docs"
    }