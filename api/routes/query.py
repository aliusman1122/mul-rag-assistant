# =============================================================================
# FILE: api/routes/query.py
# PURPOSE: User ke questions handle karne ke endpoints.
#          /query endpoint user ka sawal leta hai aur answer deta hai.
# =============================================================================

import logging
from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from typing import Optional

from services import get_rag_service, get_chat_service

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================
class QueryRequest(BaseModel):
    """JSON body request model."""
    question: str
    use_llm: bool = True
    k: int = 4


class QueryResponse(BaseModel):
    """Query response model."""
    question: str
    answer: str
    sources: list
    status: str
    docs_retrieved: int = 0


# =============================================================================
# Query Endpoints
# =============================================================================
@router.post("/query")
async def query(
    question: str = Form(...),
    use_ollama: str = Form("false"),   # Legacy parameter name
    use_llm: str = Form("true"),
    k: int = Form(4)
):
    """
    Main query endpoint.
    User ka question receive karo, answer generate karo.
    
    Args:
        question: User ka sawal
        use_llm: AI use kare ya sirf retrieve kare
        k: Kitne documents retrieve karne hain
    
    Returns:
        dict: Answer + sources
    """
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty!")
    
    # use_llm determine karo (both old and new parameter names support karo)
    should_use_llm = (
        use_llm.lower() == "true" or
        use_ollama.lower() == "true"
    )
    
    logger.info(f"❓ Query received: {question[:80]}")
    
    try:
        rag_service = get_rag_service()
        chat_service = get_chat_service()
        
        # Answer generate karo
        result = rag_service.query(
            question=question,
            k=k,
            use_llm=should_use_llm
        )
        
        # Chat history mein save karo
        chat_service.add_entry(
            question=question,
            answer=result["answer"],
            sources=result.get("sources", []),
            metadata={
                "use_llm": should_use_llm,
                "docs_retrieved": result.get("docs_retrieved", 0)
            }
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/query/json")
async def query_json(request: QueryRequest):
    """
    JSON body query endpoint.
    Alternative endpoint jo JSON format accept karta hai.
    """
    return await query(
        question=request.question,
        use_llm=str(request.use_llm),
        use_ollama="false",
        k=request.k
    )


@router.get("/status")
async def get_status():
    """API aur database status check karo."""
    try:
        rag_service = get_rag_service()
        return rag_service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))