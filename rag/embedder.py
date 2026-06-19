# =============================================================================
# FILE: rag/embedder.py
# PURPOSE: Text ko numerical vectors (numbers) mein convert karta hai.
#          Yeh vectors "meaning" ko represent karte hain.
#          Similar meaning wale texts ke vectors similar honge.
#
# Analogy: "Apple" aur "Fruit" ke vectors close honge
#          "Apple" aur "Car" ke vectors door honge
#
# Nayi university ke liye: Change ki zaroorat NAHIN.
# =============================================================================

import logging
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from config.settings import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

# =============================================================================
# Global instance - ek hi baar model load hoga (memory save)
# =============================================================================
_embedder_instance = None


def get_embedder() -> HuggingFaceEmbeddings:
    """
    Embedding model ka singleton instance return karo.
    Singleton pattern: Model ek hi baar load hota hai, baar baar nahi.
    Yeh memory aur time bachata hai.
    
    Returns:
        HuggingFaceEmbeddings: Embedding model instance
    """
    global _embedder_instance
    
    if _embedder_instance is None:
        logger.info(f"🤖 Loading embedding model: {EMBEDDING_MODEL}")
        logger.info("   (First time loading may take 1-2 minutes...)")
        
        # Model configuration
        model_kwargs = {
            'device': 'cpu'   # CPU use karo (GPU nahi chahiye)
        }
        encode_kwargs = {
            'normalize_embeddings': True  # Vectors normalize karo (better similarity)
        }
        
        _embedder_instance = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        
        logger.info("✅ Embedding model loaded successfully!")
    
    return _embedder_instance


class TextEmbedder:
    """
    Text embedding class.
    
    Example usage:
        embedder = TextEmbedder()
        vector = embedder.embed_text("What is the fee for BS CS?")
        # Returns: [0.234, -0.567, 0.891, ...] (384 dimensional vector)
    """
    
    def __init__(self):
        self.model = get_embedder()
        logger.info("📐 TextEmbedder ready!")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Single text ko vector mein convert karo.
        
        Args:
            text: Input text string
        
        Returns:
            List[float]: Numerical vector (384 dimensions)
        """
        if not text or not text.strip():
            raise ValueError("Empty text cannot be embedded!")
        
        vectors = self.model.embed_documents([text])
        return vectors[0]
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Multiple texts ko vectors mein convert karo.
        Batch processing - ek baar mein saare texts process karo.
        
        Args:
            texts: List of text strings
        
        Returns:
            List[List[float]]: List of vectors
        """
        if not texts:
            return []
        
        # Empty texts filter karo
        valid_texts = [t for t in texts if t and t.strip()]
        
        if not valid_texts:
            return []
        
        logger.info(f"📐 Embedding {len(valid_texts)} texts...")
        vectors = self.model.embed_documents(valid_texts)
        logger.info(f"✅ Generated {len(vectors)} embeddings")
        
        return vectors
    
    def embed_query(self, query: str) -> List[float]:
        """
        Search query ko embed karo.
        Query embedding thodi different hoti hai document embedding se.
        
        Args:
            query: User ka question
        
        Returns:
            List[float]: Query vector
        """
        return self.model.embed_query(query)


# Test ke liye
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    embedder = TextEmbedder()
    
    # Test
    text1 = "What is the fee for BS Computer Science?"
    text2 = "BS CS fee structure at MUL"
    text3 = "How to apply for admission?"
    
    v1 = embedder.embed_query(text1)
    v2 = embedder.embed_query(text2)
    
    print(f"\n📊 Embedding dimensions: {len(v1)}")
    print(f"First few values of v1: {v1[:5]}")
    
    # Cosine similarity check
    import numpy as np
    similarity = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    print(f"\n🔍 Similarity between similar texts: {similarity:.4f}")