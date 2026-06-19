# =============================================================================
# FILE: services/ingest_service.py
# PURPOSE: Data ingestion pipeline - documents load, chunk, aur store karo.
#          Yeh one-time process hai jo database populate karta hai.
#
# Flow:
# Load Documents -> Chunk -> Generate Embeddings -> Store in ChromaDB
#
# Nayi university ke liye:
# 1. data/pdfs/ mein nayi PDFs daal do
# 2. config mein SCRAPE_URLS update karo
# 3. python scripts/ingest.py run karo
# =============================================================================

import logging
from typing import List, Optional
from langchain.schema import Document

from rag.loader import DocumentLoader
from rag.chunker import DocumentChunker
from rag.vectorstore import get_vectorstore

logger = logging.getLogger(__name__)


class IngestService:
    """
    Data ingestion service.
    
    Yeh class sab kuch coordinate karta hai:
    1. Documents load karna
    2. Chunks banana
    3. Vector store mein save karna
    """
    
    def __init__(self):
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker()
        self.vectorstore = get_vectorstore()
        logger.info("⚙️  IngestService initialized!")
    
    def ingest_all(self, reset_first: bool = False) -> dict:
        """
        Saara data ingest karo (PDFs + scraped data).
        
        Args:
            reset_first: Database pehle empty karo ya nahi
        
        Returns:
            dict: Ingestion results/stats
        """
        logger.info("🚀 Starting full ingestion pipeline...")
        
        # Database reset karo agar requested
        if reset_first:
            logger.info("🗑️  Resetting vector store first...")
            self.vectorstore.reset()
        
        # Step 1: Documents load karo
        logger.info("\n📄 Step 1: Loading documents...")
        documents = self.loader.load_all()
        
        if not documents:
            logger.error("❌ No documents found! Check data/pdfs/ and data/scraped/")
            return {"status": "error", "message": "No documents found"}
        
        logger.info(f"✅ Loaded: {len(documents)} documents")
        
        # Step 2: Chunks banao
        logger.info("\n✂️  Step 2: Chunking documents...")
        chunks = self.chunker.chunk_documents(documents)
        
        if not chunks:
            logger.error("❌ No chunks created!")
            return {"status": "error", "message": "Chunking failed"}
        
        stats = self.chunker.get_stats(chunks)
        logger.info(f"✅ Created: {stats['total_chunks']} chunks")
        logger.info(f"   Avg chunk size: {stats['avg_size']} chars")
        
        # Step 3: Vector store mein save karo
        logger.info("\n💾 Step 3: Storing in vector database...")
        success = self.vectorstore.add_documents(chunks)
        
        if not success:
            return {"status": "error", "message": "Vector store failed"}
        
        # Final stats
        db_stats = self.vectorstore.get_stats()
        
        result = {
            "status": "success",
            "documents_loaded": len(documents),
            "chunks_created": len(chunks),
            "chunks_stored": db_stats.get("total_documents", 0),
            "avg_chunk_size": stats["avg_size"],
            "database_path": db_stats.get("db_path", ""),
        }
        
        logger.info(f"\n🎉 Ingestion complete!")
        logger.info(f"   Documents: {result['documents_loaded']}")
        logger.info(f"   Chunks: {result['chunks_created']}")
        logger.info(f"   Stored in DB: {result['chunks_stored']}")
        
        return result
    
    def ingest_uploaded_files(self, files_data: List[dict]) -> dict:
        """
        User-uploaded files ingest karo (API ke through).
        
        Args:
            files_data: List of {filename, content, content_type}
        
        Returns:
            dict: Ingestion results
        """
        logger.info(f"📤 Ingesting {len(files_data)} uploaded files...")
        
        # Files load karo
        documents = self.loader.load_uploaded_files(files_data)
        
        if not documents:
            return {"status": "error", "message": "Could not load uploaded files"}
        
        # Chunk karo
        chunks = self.chunker.chunk_documents(documents)
        
        # Store karo
        success = self.vectorstore.add_documents(chunks)
        
        return {
            "status": "success" if success else "error",
            "files_processed": len(files_data),
            "documents_created": len(documents),
            "chunks_created": len(chunks)
        }


# Singleton
_ingest_service_instance = None


def get_ingest_service() -> IngestService:
    """IngestService singleton instance."""
    global _ingest_service_instance
    if _ingest_service_instance is None:
        _ingest_service_instance = IngestService()
    return _ingest_service_instance