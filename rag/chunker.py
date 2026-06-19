# =============================================================================
# FILE: rag/chunker.py
# PURPOSE: Documents ko chhote chhote "chunks" (pieces) mein todta hai.
#          Kyun? Kyunki AI model ek baar mein poora document process nahi kar sakta.
#          Chhote pieces se better search results milte hain.
#
# Nayi university ke liye: Usually change ki zaroorat NAHIN.
#          Agar content bahut lamba ya chhota hai, CHUNK_SIZE adjust karo.
# =============================================================================

import logging
from typing import List
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)


class DocumentChunker:
    """
    Document chunks banane ki class.
    
    Example:
    - Original: "Minhaj University was founded in 1997... [500 words]"
    - Chunks:   ["Minhaj University was founded in 1997..." (chunk 1),
                 "...1997. The university offers BS programs..." (chunk 2),
                 ...]
    
    Chunk ke beech overlap kyun? Taake koi information miss na ho.
    """
    
    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP
    ):
        """
        Args:
            chunk_size: Har chunk mein kitne characters honge (default: 500)
            chunk_overlap: Consecutive chunks mein kitna overlap ho (default: 100)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # RecursiveCharacterTextSplitter best hai kyunki:
        # 1. Pehle paragraphs par split karta hai
        # 2. Phir sentences par
        # 3. Phir words par
        # Yeh natural breaks prefer karta hai
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",    # Paragraphs
                "\n",      # Lines
                ". ",      # Sentences
                ", ",      # Clauses
                " ",       # Words
                ""         # Characters (last resort)
            ]
        )
        
        logger.info(
            f"📝 Chunker initialized: size={chunk_size}, overlap={chunk_overlap}"
        )
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Documents list ko chunks mein todo.
        
        Args:
            documents: Original documents ki list
        
        Returns:
            List[Document]: Chhote chunks ki list
        """
        if not documents:
            logger.warning("⚠️  No documents to chunk!")
            return []
        
        logger.info(f"✂️  Chunking {len(documents)} documents...")
        
        # Splitter se chunks banao
        chunks = self.splitter.split_documents(documents)
        
        # Empty chunks filter karo
        chunks = [c for c in chunks if c.page_content.strip()]
        
        # Har chunk ko unique ID do
        for i, chunk in enumerate(chunks):
            chunk.metadata['chunk_id'] = i
            chunk.metadata['chunk_size'] = len(chunk.page_content)
        
        logger.info(f"✅ Created {len(chunks)} chunks from {len(documents)} documents")
        logger.info(f"   Average chunk size: {sum(len(c.page_content) for c in chunks) // len(chunks) if chunks else 0} chars")
        
        return chunks
    
    def chunk_text(self, text: str, metadata: dict = None) -> List[Document]:
        """
        Raw text string ko chunks mein todo.
        Web-scraped content ke liye use hota hai.
        
        Args:
            text: Raw text string
            metadata: Optional metadata dict
        
        Returns:
            List[Document]: Chunks
        """
        if not text or not text.strip():
            return []
        
        doc = Document(
            page_content=text,
            metadata=metadata or {}
        )
        
        return self.chunk_documents([doc])
    
    def get_stats(self, chunks: List[Document]) -> dict:
        """
        Chunks ke baare mein statistics return karo.
        Debugging ke liye useful hai.
        """
        if not chunks:
            return {"total": 0}
        
        sizes = [len(c.page_content) for c in chunks]
        return {
            "total_chunks": len(chunks),
            "min_size": min(sizes),
            "max_size": max(sizes),
            "avg_size": sum(sizes) // len(sizes),
            "total_chars": sum(sizes)
        }


# Test ke liye
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Sample text
    sample_text = """
    Minhaj University Lahore (MUL) is a well-known university.
    It offers various programs in Computer Science, AI, and Business.
    
    Admission Requirements:
    Students need intermediate education with minimum 50% marks.
    An interview is also required for all programs.
    
    Fee Structure:
    BS Computer Science: PKR 1,485,000 total
    BS Artificial Intelligence: PKR 1,350,000 total
    """
    
    chunker = DocumentChunker(chunk_size=200, chunk_overlap=50)
    chunks = chunker.chunk_text(sample_text, {"source": "test"})
    
    print(f"\n📊 Stats: {chunker.get_stats(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(chunk.page_content)
        print("---")