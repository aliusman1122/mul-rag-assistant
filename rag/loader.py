# =============================================================================
# FILE: rag/loader.py
# PURPOSE: Yeh file documents ko load karti hai.
#          PDF files, text files, aur web-scraped content ko read karta hai.
#
# Nayi university ke liye: Sirf PDF_DATA_PATH change karo config mein
# =============================================================================

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# LangChain document loaders
from langchain.schema import Document
from langchain_community.document_loaders import (
    PyPDFLoader,        # PDF files ke liye
    TextLoader,         # .txt files ke liye
    DirectoryLoader,    # Poora folder load karne ke liye
)

from config.settings import PDF_DATA_PATH, SCRAPED_DATA_PATH

# Logging setup - errors aur info track karne ke liye
logger = logging.getLogger(__name__)


class DocumentLoader:
    """
    Yeh class university ke tamam documents load karti hai.
    
    Supported formats:
    - PDF files (.pdf)
    - Text files (.txt)
    - JSON files (scraped data)
    
    Nayi university ke liye: data/pdfs/ folder mein naye PDFs daal do
    """
    
    def __init__(self):
        self.pdf_path = Path(PDF_DATA_PATH)
        self.scraped_path = Path(SCRAPED_DATA_PATH)
        
        # Folders exist karte hain agar na hon
        self.pdf_path.mkdir(parents=True, exist_ok=True)
        self.scraped_path.mkdir(parents=True, exist_ok=True)
    
    def load_pdfs(self) -> List[Document]:
        """
        data/pdfs/ folder se saari PDF files load karo.
        
        Returns:
            List[Document]: PDF content ke Document objects
        """
        documents = []
        pdf_files = list(self.pdf_path.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"⚠️  No PDF files found in {self.pdf_path}")
            logger.warning("💡 Add university PDFs to data/pdfs/ folder")
            return documents
        
        logger.info(f"📄 Loading {len(pdf_files)} PDF files...")
        
        for pdf_file in pdf_files:
            try:
                # PyPDFLoader har page ko alag document banata hai
                loader = PyPDFLoader(str(pdf_file))
                pages = loader.load()
                
                # Har page mein source information add karo
                for page in pages:
                    page.metadata["source_file"] = pdf_file.name
                    page.metadata["source_type"] = "pdf"
                
                documents.extend(pages)
                logger.info(f"  ✅ Loaded: {pdf_file.name} ({len(pages)} pages)")
                
            except Exception as e:
                logger.error(f"  ❌ Failed to load {pdf_file.name}: {e}")
        
        logger.info(f"📚 Total PDF documents loaded: {len(documents)}")
        return documents
    
    def load_scraped_data(self) -> List[Document]:
        """
        data/scraped/ folder se web-scraped JSON data load karo.
        
        Returns:
            List[Document]: Scraped content ke Document objects
        """
        documents = []
        json_files = list(self.scraped_path.glob("*.json"))
        
        if not json_files:
            logger.warning(f"⚠️  No scraped data found in {self.scraped_path}")
            logger.warning("💡 Run: python scripts/scrape.py first")
            return documents
        
        logger.info(f"🌐 Loading {len(json_files)} scraped data files...")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    scraped_items = json.load(f)
                
                # Har scraped page ek document ban jata hai
                for item in scraped_items:
                    if item.get('content', '').strip():
                        doc = Document(
                            page_content=item['content'],
                            metadata={
                                "source": item.get('url', 'unknown'),
                                "title": item.get('title', 'Unknown Page'),
                                "source_type": "web_scraped",
                                "source_file": json_file.name
                            }
                        )
                        documents.append(doc)
                
                logger.info(f"  ✅ Loaded: {json_file.name}")
                
            except Exception as e:
                logger.error(f"  ❌ Failed to load {json_file.name}: {e}")
        
        logger.info(f"🌐 Total scraped documents loaded: {len(documents)}")
        return documents
    
    def load_text_files(self) -> List[Document]:
        """
        data/pdfs/ folder se text files load karo (.txt extension waali).
        
        Returns:
            List[Document]: Text content ke Document objects
        """
        documents = []
        txt_files = list(self.pdf_path.glob("*.txt"))
        
        for txt_file in txt_files:
            try:
                loader = TextLoader(str(txt_file), encoding='utf-8')
                docs = loader.load()
                
                for doc in docs:
                    doc.metadata["source_file"] = txt_file.name
                    doc.metadata["source_type"] = "text"
                
                documents.extend(docs)
                logger.info(f"  ✅ Loaded text: {txt_file.name}")
                
            except Exception as e:
                logger.error(f"  ❌ Failed to load {txt_file.name}: {e}")
        
        return documents
    
    def load_all(self) -> List[Document]:
        """
        Tamam sources se documents load karo (PDFs + scraped + text).
        Yahi main function hai jo har jagah se data ikatha karta hai.
        
        Returns:
            List[Document]: Combined list of all documents
        """
        logger.info("🔄 Loading all documents...")
        
        all_docs = []
        
        # 1. PDF files load karo
        pdf_docs = self.load_pdfs()
        all_docs.extend(pdf_docs)
        
        # 2. Web scraped data load karo
        scraped_docs = self.load_scraped_data()
        all_docs.extend(scraped_docs)
        
        # 3. Text files load karo
        text_docs = self.load_text_files()
        all_docs.extend(text_docs)
        
        logger.info(f"✅ Total documents loaded: {len(all_docs)}")
        
        if not all_docs:
            logger.warning("⚠️  No documents found! Please add data first.")
            logger.warning("   1. Add PDFs to: data/pdfs/")
            logger.warning("   2. Run scraper: python scripts/scrape.py")
        
        return all_docs
    
    def load_uploaded_files(self, files_data: List[Dict]) -> List[Document]:
        """
        User ne jo files upload ki hain unhe load karo.
        Yeh API ke through uploaded files ke liye hai.
        
        Args:
            files_data: List of dicts with 'filename', 'content', 'content_type'
        
        Returns:
            List[Document]: Uploaded file documents
        """
        documents = []
        temp_dir = Path("./data/temp")
        temp_dir.mkdir(exist_ok=True)
        
        for file_data in files_data:
            filename = file_data['filename']
            content = file_data['content']
            temp_path = temp_dir / filename
            
            try:
                # File temporarily save karo
                with open(temp_path, 'wb') as f:
                    f.write(content)
                
                # Extension check karo
                if filename.endswith('.pdf'):
                    loader = PyPDFLoader(str(temp_path))
                    docs = loader.load()
                elif filename.endswith(('.txt', '.md')):
                    loader = TextLoader(str(temp_path))
                    docs = loader.load()
                else:
                    logger.warning(f"Unsupported file type: {filename}")
                    continue
                
                # Metadata add karo
                for doc in docs:
                    doc.metadata['source_file'] = filename
                    doc.metadata['source_type'] = 'uploaded'
                
                documents.extend(docs)
                logger.info(f"✅ Uploaded file loaded: {filename}")
                
            except Exception as e:
                logger.error(f"❌ Error loading uploaded file {filename}: {e}")
            finally:
                # Temp file delete karo
                if temp_path.exists():
                    temp_path.unlink()
        
        return documents


# Quick test ke liye
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loader = DocumentLoader()
    docs = loader.load_all()
    print(f"\n📊 Total documents loaded: {len(docs)}")
    if docs:
        print(f"First doc preview: {docs[0].page_content[:200]}...")