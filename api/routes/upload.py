# =============================================================================
# FILE: api/routes/upload.py
# PURPOSE: File upload aur database reset endpoints.
#          Users PDF aur text files upload kar sakte hain.
# =============================================================================

import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException

from services import get_ingest_service
from rag.vectorstore import get_vectorstore

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Files upload karo aur vector database mein store karo.
    
    Supported formats: PDF, TXT, MD
    
    Args:
        files: List of uploaded files
    
    Returns:
        dict: Upload results
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided!")
    
    logger.info(f"📤 Uploading {len(files)} files...")
    
    # Files data prepare karo
    files_data = []
    
    for file in files:
        # File type check karo
        filename = file.filename or "unknown"
        
        if not any(filename.endswith(ext) for ext in ['.pdf', '.txt', '.md']):
            logger.warning(f"⚠️  Skipping unsupported file: {filename}")
            continue
        
        # File content read karo
        content = await file.read()
        
        if not content:
            logger.warning(f"⚠️  Empty file: {filename}")
            continue
        
        files_data.append({
            "filename": filename,
            "content": content,
            "content_type": file.content_type or "application/octet-stream"
        })
    
    if not files_data:
        raise HTTPException(
            status_code=400,
            detail="No valid files found! Supported: PDF, TXT, MD"
        )
    
    # Ingest karo
    try:
        ingest_service = get_ingest_service()
        result = ingest_service.ingest_uploaded_files(files_data)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))
        
        logger.info(f"✅ Upload complete: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/reset")
async def reset_database():
    """
    Vector database reset karo.
    Warning: Saara data delete ho jayega!
    
    Returns:
        dict: Reset status
    """
    try:
        vectorstore = get_vectorstore()
        success = vectorstore.reset()
        
        if success:
            logger.info("🗑️  Database reset successfully!")
            return {"status": "success", "message": "Database reset complete"}
        else:
            raise HTTPException(status_code=500, detail="Reset failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Reset error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest")
async def trigger_ingestion(reset_first: bool = False):
    """
    Data/pdfs/ aur data/scraped/ folders se data ingest karo.
    
    Args:
        reset_first: Database pehle clear karo
    
    Returns:
        dict: Ingestion results
    """
    try:
        ingest_service = get_ingest_service()
        result = ingest_service.ingest_all(reset_first=reset_first)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))