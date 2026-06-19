# =============================================================================
# FILE: api/routes/health.py
# PURPOSE: Health check endpoints - server ka status check karne ke liye
# =============================================================================

from fastapi import APIRouter
from services import get_rag_service

router = APIRouter()


@router.get("/health")
async def health_check():
    """Server aur services ka health check."""
    try:
        rag = get_rag_service()
        stats = rag.get_stats()
        
        return {
            "status": "healthy",
            "database_ready": stats.get("ready", False),
            "total_documents": stats.get("database", {}).get("total_documents", 0),
            "llm_provider": stats.get("llm_provider", "unknown")
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}