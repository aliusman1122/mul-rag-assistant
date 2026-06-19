# =============================================================================
# FILE: api/routes/history.py
# PURPOSE: Chat history ke CRUD endpoints.
# =============================================================================

import logging
from fastapi import APIRouter, HTTPException
from services import get_chat_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/history")
async def get_history(limit: int = 20):
    """
    Chat history return karo.
    
    Args:
        limit: Kitne recent entries chahiye
    
    Returns:
        dict: History list
    """
    try:
        chat_service = get_chat_service()
        history = chat_service.get_history(limit=limit)
        
        return {
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/history/clear")
async def clear_history():
    """Chat history clear karo."""
    try:
        chat_service = get_chat_service()
        success = chat_service.clear_history()
        
        if success:
            return {"status": "success", "message": "History cleared!"}
        else:
            raise HTTPException(status_code=500, detail="Clear failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/stats")
async def history_stats():
    """History statistics return karo."""
    chat_service = get_chat_service()
    return chat_service.get_stats()