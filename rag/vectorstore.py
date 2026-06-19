# =============================================================================
# FILE: rag/vectorstore.py
# PURPOSE: ChromaDB vector database ke saath kaam karta hai.
#          Documents store karna, search karna - yeh sab yahan hota hai.
#
# Analogy: Yeh ek intelligent library hai jahan books "meaning" ke basis par
#          shelf par rakhi hoti hain, na title ke basis par.
#
# Nayi university ke liye: CHROMA_COLLECTION_NAME change karo config mein
# =============================================================================

import logging
import os
from typing import List, Optional, Tuple
from pathlib import Path

from langchain.schema import Document
from langchain_community.vectorstores import Chroma

from rag.embedder import get_embedder
from config.settings import (
    CHROMA_DB_PATH,
    CHROMA_COLLECTION_NAME,
    TOP_K_RESULTS,
    SIMILARITY_THRESHOLD
)

logger = logging.getLogger(__name__)


class VectorStore:
    """
    ChromaDB vector database wrapper class.
    
    Features:
    - Documents save karna (persist)
    - Semantic search karna
    - Documents delete karna
    - Stats check karna
    """
    
    def __init__(self):
        self.db_path = CHROMA_DB_PATH
        self.collection_name = CHROMA_COLLECTION_NAME
        self.embedder = get_embedder()
        self._db = None  # Database connection (lazy loading)
        
        # DB folder create karo
        Path(self.db_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"📦 VectorStore initialized at: {self.db_path}")
    
    def _get_db(self) -> Chroma:
        """
        Database connection return karo (create karo agar exist nahi karti).
        Lazy loading pattern use kiya hai.
        """
        if self._db is None:
            self._db = Chroma(
                persist_directory=self.db_path,
                embedding_function=self.embedder,
                collection_name=self.collection_name
            )
        return self._db
    
    def add_documents(self, documents: List[Document]) -> bool:
        """
        Documents ko vector database mein store karo.
        
        Process:
        1. Text extract karo document se
        2. Embedding generate karo (text -> vector)
        3. Vector + text database mein save karo
        
        Args:
            documents: List of Document objects
        
        Returns:
            bool: True if successful
        """
        if not documents:
            logger.warning("⚠️  No documents to add!")
            return False
        
        logger.info(f"💾 Adding {len(documents)} documents to vector store...")
        
        try:
            db = self._get_db()
            
            # Batch mein add karo (memory efficient)
            batch_size = 50  # Ek baar mein 50 documents
            total_added = 0
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                # Texts aur metadata extract karo
                texts = [doc.page_content for doc in batch]
                metadatas = [doc.metadata for doc in batch]
                
                # Chroma mein add karo
                db.add_texts(texts=texts, metadatas=metadatas)
                total_added += len(batch)
                
                logger.info(f"   Progress: {total_added}/{len(documents)}")
            
            logger.info(f"✅ Successfully added {total_added} documents!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding documents: {e}")
            return False
    
    def search(
        self,
        query: str,
        k: int = TOP_K_RESULTS,
        filter_metadata: Optional[dict] = None
    ) -> List[Tuple[Document, float]]:
        """
        Query ke similar documents search karo.
        
        Process:
        1. Query text ko vector mein convert karo
        2. Database mein similar vectors dhundo
        3. Results sort karke return karo
        
        Args:
            query: User ka question/search text
            k: Kitne results chahiye
            filter_metadata: Optional metadata filter
        
        Returns:
            List of (Document, similarity_score) tuples
        """
        if not query or not query.strip():
            logger.warning("⚠️  Empty query!")
            return []
        
        logger.info(f"🔍 Searching for: '{query[:50]}...'")
        
        try:
            db = self._get_db()
            
            # Similarity search with scores
            results = db.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_metadata
            )
            
            # Score filter karo (low similarity results remove)
            # Note: ChromaDB mein lower score = more similar (distance)
            filtered_results = [
                (doc, score) for doc, score in results
                if score <= (1 - SIMILARITY_THRESHOLD)  # Convert threshold
            ]
            
            logger.info(f"✅ Found {len(filtered_results)} relevant results")
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            return []
    
    def search_simple(self, query: str, k: int = TOP_K_RESULTS) -> List[Document]:
        """
        Simple search - sirf documents return karo, scores nahi.
        
        Args:
            query: Search query
            k: Number of results
        
        Returns:
            List[Document]: Matching documents
        """
        results = self.search(query, k)
        return [doc for doc, _ in results]
    
    def reset(self) -> bool:
        """
        Vector database mein se saara data delete karo.
        Warning: Yeh operation reversible nahi hai!
        
        Returns:
            bool: True if successful
        """
        try:
            import shutil
            
            if Path(self.db_path).exists():
                shutil.rmtree(self.db_path)
                logger.info(f"🗑️  Deleted vector store at: {self.db_path}")
            
            # Reconnect ke liye None karo
            self._db = None
            
            # Folder dobara create karo
            Path(self.db_path).mkdir(parents=True, exist_ok=True)
            
            logger.info("✅ Vector store reset successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Reset error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """
        Vector database ki statistics return karo.
        
        Returns:
            dict: Stats including document count
        """
        try:
            db = self._get_db()
            collection = db._collection
            count = collection.count()
            
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "db_path": self.db_path,
                "status": "active"
            }
        except Exception as e:
            return {
                "total_documents": 0,
                "status": "error",
                "error": str(e)
            }
    
    def is_empty(self) -> bool:
        """Check karo agar database empty hai."""
        stats = self.get_stats()
        return stats.get("total_documents", 0) == 0


# Singleton instance
_vectorstore_instance = None


def get_vectorstore() -> VectorStore:
    """
    VectorStore ka singleton instance return karo.
    Ek hi instance application mein use hoga.
    """
    global _vectorstore_instance
    if _vectorstore_instance is None:
        _vectorstore_instance = VectorStore()
    return _vectorstore_instance


# Test ke liye
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    vs = VectorStore()
    
    # Test documents add karo
    test_docs = [
        Document(
            page_content="BS Computer Science fee is PKR 1,485,000 for 4 years at MUL",
            metadata={"source": "admissions_page", "type": "fee"}
        ),
        Document(
            page_content="Admission requires minimum 50% marks in intermediate",
            metadata={"source": "admissions_page", "type": "eligibility"}
        ),
        Document(
            page_content="MUL offers BS AI program with PKR 1,350,000 fee",
            metadata={"source": "admissions_page", "type": "fee"}
        )
    ]
    
    vs.add_documents(test_docs)
    
    # Test search
    results = vs.search("What is the fee for BS CS?")
    
    print(f"\n📊 Stats: {vs.get_stats()}")
    print(f"\n🔍 Search results for 'fee for BS CS':")
    for doc, score in results:
        print(f"  Score: {score:.4f} | {doc.page_content[:100]}")