# =============================================================================
# FILE: rag/retriever.py
# PURPOSE: User ke question ke liye relevant documents dhundta hai.
#          Yeh RAG ka "R" (Retrieval) part hai.
#
# Flow: User Question -> Embed Query -> Search VectorStore -> Return Context
#
# Nayi university ke liye: Change ki zaroorat NAHIN
# =============================================================================

import logging
from typing import List, Dict, Optional
from langchain.schema import Document
from rag.vectorstore import get_vectorstore
from config.settings import TOP_K_RESULTS

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """
    Documents retrieve karne ki class.
    
    Example:
    User puchta hai: "BS CS ki fee kya hai?"
    Retriever: Database mein dhundta hai aur fee-related chunks return karta hai
    """
    
    def __init__(self):
        self.vectorstore = get_vectorstore()
        logger.info("🔍 DocumentRetriever ready!")
    
    def retrieve(
        self,
        query: str,
        k: int = TOP_K_RESULTS,
        source_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Query ke liye relevant documents retrieve karo.
        
        Args:
            query: User ka question
            k: Kitne documents chahiye
            source_filter: Sirf ek specific source se documents (optional)
        
        Returns:
            List of dicts with document info and scores
        """
        if not query or not query.strip():
            logger.warning("⚠️  Empty query received!")
            return []
        
        logger.info(f"🔍 Retrieving docs for: '{query[:60]}'")
        
        # Metadata filter (optional)
        filter_dict = None
        if source_filter:
            filter_dict = {"source_type": source_filter}
        
        # Vector store se search karo
        results = self.vectorstore.search(query, k=k, filter_metadata=filter_dict)
        
        if not results:
            logger.warning(f"⚠️  No relevant documents found for: '{query}'")
            return []
        
        # Results ko readable format mein convert karo
        retrieved = []
        for i, (doc, score) in enumerate(results):
            retrieved.append({
                "rank": i + 1,                           # Result ka rank
                "text": doc.page_content,                # Document ka content
                "score": float(score),                   # Similarity score
                "source": doc.metadata.get("source", "Unknown"),
                "source_file": doc.metadata.get("source_file", ""),
                "source_type": doc.metadata.get("source_type", ""),
                "page": doc.metadata.get("page", ""),
                "chunk_id": doc.metadata.get("chunk_id", i),
                "metadata": doc.metadata
            })
        
        logger.info(f"✅ Retrieved {len(retrieved)} documents")
        return retrieved
    
    def retrieve_context(self, query: str, k: int = TOP_K_RESULTS) -> str:
        """
        Query ke liye context string return karo.
        Yeh AI model ke prompt mein directly use hota hai.
        
        Args:
            query: User ka question
            k: Number of documents
        
        Returns:
            str: Formatted context string
        """
        docs = self.retrieve(query, k)
        
        if not docs:
            return "No relevant information found in the university documents."
        
        # Context build karo
        context_parts = []
        for doc in docs:
            source_info = doc.get("source", "University Document")
            context_parts.append(
                f"[Source: {source_info}]\n{doc['text']}"
            )
        
        context = "\n\n---\n\n".join(context_parts)
        return context
    
    def is_database_ready(self) -> bool:
        """Check karo agar database mein documents hain."""
        return not self.vectorstore.is_empty()
    
    def get_database_stats(self) -> dict:
        """Database ki stats return karo."""
        return self.vectorstore.get_stats()


# Singleton instance
_retriever_instance = None


def get_retriever() -> DocumentRetriever:
    """DocumentRetriever ka singleton instance."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = DocumentRetriever()
    return _retriever_instance


# Test ke liye
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    retriever = DocumentRetriever()
    
    stats = retriever.get_database_stats()
    print(f"\n📊 Database Stats: {stats}")
    
    if retriever.is_database_ready():
        results = retriever.retrieve("What is the fee for BS CS?")
        print(f"\n🔍 Retrieved {len(results)} documents:")
        for r in results:
            print(f"  Rank {r['rank']}: {r['text'][:100]}...")
    else:
        print("⚠️  Database is empty! Run ingestion script first.")