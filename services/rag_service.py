# =============================================================================
# FILE: services/rag_service.py
# PURPOSE: Yeh poori RAG pipeline ko coordinate karta hai.
#          Retrieval + AI Generation ka combination yahan hota hai.
#
# RAG Flow:
# 1. User ka question aaya
# 2. Related documents database se nikalo (Retrieve)
# 3. AI model ko context + question do (Augment)
# 4. AI answer generate kare (Generate)
# 5. Answer + sources user ko do
#
# Nayi university ke liye: system_prompt.txt change karo
# =============================================================================

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from rag.retriever import get_retriever
from config.settings import (
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    LANGSMITH_API_KEY,
    LANGCHAIN_TRACING_V2,
    LANGCHAIN_PROJECT
)

logger = logging.getLogger(__name__)

# =============================================================================
# LangSmith tracing setup (optional - debugging ke liye)
# =============================================================================
if LANGCHAIN_TRACING_V2 == "true" and LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
    logger.info("📊 LangSmith tracing enabled")


class RAGService:
    """
    Main RAG Service - poori pipeline yahan hai.
    
    Yeh class:
    1. Relevant documents retrieve karti hai
    2. AI model se answer generate karti hai
    3. Sources ke saath answer return karti hai
    
    Supported LLM Providers:
    - Groq (recommended - fast, free)
    - OpenAI (paid but very good)
    - Ollama (local, offline)
    """
    
    def __init__(self):
        self.retriever = get_retriever()
        self.llm = None  # Lazy load
        self._load_prompts()
        logger.info(f"🤖 RAGService initialized with provider: {LLM_PROVIDER}")
    
    def _load_prompts(self):
        """Prompt files load karo."""
        prompts_dir = Path("./prompts")
        
        # System prompt load karo
        system_file = prompts_dir / "system_prompt.txt"
        if system_file.exists():
            self.system_prompt = system_file.read_text(encoding='utf-8')
        else:
            # Default system prompt agar file na mile
            self.system_prompt = (
                "You are a helpful university information assistant. "
                "Answer questions based only on the provided context."
            )
        
        # QA prompt template load karo
        qa_file = prompts_dir / "qa_prompt.txt"
        if qa_file.exists():
            self.qa_prompt_template = qa_file.read_text(encoding='utf-8')
        else:
            self.qa_prompt_template = (
                "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
            )
        
        # Fallback prompt load karo
        fallback_file = prompts_dir / "fallback_prompt.txt"
        if fallback_file.exists():
            self.fallback_template = fallback_file.read_text(encoding='utf-8')
        else:
            self.fallback_template = "No information found. Please contact the university directly."
        
        logger.info("📝 Prompts loaded successfully")
    
    def _get_llm(self):
        """
        LLM instance return karo.
        Provider setting ke hisab se sahi LLM load karo.
        """
        if self.llm is not None:
            return self.llm
        
        if LLM_PROVIDER == "groq":
            self.llm = self._setup_groq()
        elif LLM_PROVIDER == "openai":
            self.llm = self._setup_openai()
        elif LLM_PROVIDER == "ollama":
            self.llm = self._setup_ollama()
        else:
            logger.warning(f"Unknown LLM provider: {LLM_PROVIDER}, using Groq")
            self.llm = self._setup_groq()
        
        return self.llm
    
    def _setup_groq(self):
        """Groq LLM setup karo (recommended - free aur fast)."""
        try:
            from groq import Groq
            
            if not GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not set in .env file!")
            
            client = Groq(api_key=GROQ_API_KEY)
            logger.info(f"✅ Groq LLM ready: {GROQ_MODEL}")
            return client
            
        except ImportError:
            raise ImportError("Install groq: pip install groq")
    
    def _setup_openai(self):
        """OpenAI LLM setup karo."""
        try:
            from openai import OpenAI
            
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set!")
            
            client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info(f"✅ OpenAI LLM ready: {OPENAI_MODEL}")
            return client
            
        except ImportError:
            raise ImportError("Install openai: pip install openai")
    
    def _setup_ollama(self):
        """Ollama local LLM setup karo."""
        try:
            from langchain_community.llms import Ollama
            
            llm = Ollama(
                base_url=OLLAMA_BASE_URL,
                model=OLLAMA_MODEL
            )
            logger.info(f"✅ Ollama LLM ready: {OLLAMA_MODEL}")
            return llm
            
        except Exception as e:
            raise RuntimeError(f"Ollama setup failed: {e}. Is Ollama running?")
    
    def _call_llm(self, messages: list) -> str:
        """
        LLM ko call karo aur response return karo.
        Provider ke hisab se different API call.
        """
        llm = self._get_llm()
        
        try:
            if LLM_PROVIDER == "groq":
                response = llm.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=messages,
                    temperature=0.3,        # Low = more factual
                    max_tokens=1000,
                )
                return response.choices[0].message.content
            
            elif LLM_PROVIDER == "openai":
                response = llm.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1000,
                )
                return response.choices[0].message.content
            
            elif LLM_PROVIDER == "ollama":
                # Ollama ke liye messages ko string mein convert karo
                prompt = "\n".join([
                    f"{m['role'].upper()}: {m['content']}"
                    for m in messages
                ])
                return llm.invoke(prompt)
            
        except Exception as e:
            logger.error(f"❌ LLM call failed: {e}")
            raise
    
    def query(
        self,
        question: str,
        k: int = 4,
        use_llm: bool = True
    ) -> Dict:
        """
        Main query function - user ka question le, answer do.
        
        Args:
            question: User ka question
            k: Kitne source documents use karne hain
            use_llm: AI generate kare ya sirf documents return kare
        
        Returns:
            Dict with answer, sources, and metadata
        """
        if not question or not question.strip():
            return {
                "answer": "Please ask a valid question.",
                "sources": [],
                "question": question,
                "status": "error"
            }
        
        logger.info(f"❓ Query: {question[:80]}")
        
        # =============================================================================
        # Step 1: RETRIEVE - Relevant documents dhundo
        # =============================================================================
        retrieved_docs = self.retriever.retrieve(question, k=k)
        
        if not retrieved_docs:
            logger.warning("⚠️  No relevant documents found!")
            
            # Fallback response
            fallback_answer = (
                "I couldn't find specific information about your query in my knowledge base. "
                "Please contact Minhaj University Lahore directly:\n"
                "📧 Email: info@mul.edu.pk\n"
                "📞 Phone: +92-42-35761999\n"
                "🌐 Website: www.mul.edu.pk"
            )
            
            return {
                "answer": fallback_answer,
                "sources": [],
                "question": question,
                "status": "no_context"
            }
        
        # =============================================================================
        # Step 2: AUGMENT - Context build karo
        # =============================================================================
        context = self._build_context(retrieved_docs)
        
        # =============================================================================
        # Step 3: GENERATE - AI se answer generate karo
        # =============================================================================
        if use_llm:
            answer = self._generate_answer(question, context)
        else:
            # Sirf context return karo (no AI generation)
            answer = f"**Relevant Information:**\n\n{context}"
        
        # Sources format karo
        sources = self._format_sources(retrieved_docs)
        
        logger.info(f"✅ Answer generated ({len(answer)} chars)")
        
        return {
            "answer": answer,
            "sources": sources,
            "question": question,
            "context_length": len(context),
            "docs_retrieved": len(retrieved_docs),
            "status": "success"
        }
    
    def _build_context(self, retrieved_docs: List[Dict]) -> str:
        """
        Retrieved documents se context string banao.
        Yeh context AI model ko diya jata hai.
        """
        context_parts = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc.get("source", "University Document")
            text = doc.get("text", "")
            
            context_parts.append(
                f"[Document {i}] (Source: {source})\n{text}"
            )
        
        return "\n\n".join(context_parts)
    
    def _generate_answer(self, question: str, context: str) -> str:
        """
        AI model se answer generate karo.
        
        Args:
            question: User ka question
            context: Retrieved documents ka context
        
        Returns:
            str: AI generated answer
        """
        # QA prompt template fill karo
        user_message = self.qa_prompt_template.format(
            context=context,
            question=question
        )
        
        # Messages format (OpenAI-style)
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        try:
            answer = self._call_llm(messages)
            return answer.strip()
        except Exception as e:
            logger.error(f"❌ LLM error: {e}")
            # Fallback: context dikhao
            return (
                f"I found relevant information but couldn't generate a response.\n\n"
                f"**Relevant Context:**\n{context[:1000]}...\n\n"
                f"Please contact MUL for clarification: info@mul.edu.pk"
            )
    
    def _format_sources(self, retrieved_docs: List[Dict]) -> List[Dict]:
        """Sources ko response format mein convert karo."""
        sources = []
        
        for doc in retrieved_docs:
            sources.append({
                "source_index": doc.get("rank", 1),
                "source": doc.get("source", "University Document"),
                "source_file": doc.get("source_file", ""),
                "source_type": doc.get("source_type", ""),
                "text": doc.get("text", "")[:500],  # Pehle 500 chars
                "score": round(doc.get("score", 0), 4)
            })
        
        return sources
    
    def is_ready(self) -> bool:
        """Check karo agar service ready hai (database populated)."""
        return self.retriever.is_database_ready()
    
    def get_stats(self) -> dict:
        """Service stats return karo."""
        return {
            "llm_provider": LLM_PROVIDER,
            "llm_model": GROQ_MODEL if LLM_PROVIDER == "groq" else OPENAI_MODEL,
            "database": self.retriever.get_database_stats(),
            "prompts_loaded": hasattr(self, 'system_prompt'),
            "ready": self.is_ready()
        }


# Singleton
_rag_service_instance = None


def get_rag_service() -> RAGService:
    """RAGService singleton instance."""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance


# Test ke liye
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    service = RAGService()
    stats = service.get_stats()
    print(f"\n📊 RAG Service Stats: {json.dumps(stats, indent=2)}")
    
    if service.is_ready():
        result = service.query("What is the fee for BS Computer Science?")
        print(f"\n❓ Question: {result['question']}")
        print(f"💬 Answer: {result['answer'][:500]}")
        print(f"\n📚 Sources: {len(result['sources'])}")
    else:
        print("⚠️  Database not ready! Run ingestion first.")