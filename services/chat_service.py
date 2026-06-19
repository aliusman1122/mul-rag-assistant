# =============================================================================
# FILE: services/chat_service.py
# PURPOSE: Chat history store aur retrieve karta hai.
#          User ke purane sawal aur jawab save karta hai.
#
# Nayi university ke liye: Change ki zaroorat NAHIN
# =============================================================================

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from config.settings import CHAT_HISTORY_FILE, MAX_HISTORY_LENGTH

logger = logging.getLogger(__name__)


class ChatService:
    """
    Chat history manage karne ki class.
    
    Features:
    - Conversation history save karna
    - History load karna
    - History clear karna
    - History length limit maintain karna
    """
    
    def __init__(self):
        self.history_file = Path(CHAT_HISTORY_FILE)
        
        # Parent directory create karo
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # History file create karo agar exist nahi karti
        if not self.history_file.exists():
            self._save_history([])
        
        logger.info(f"💬 ChatService initialized: {self.history_file}")
    
    def _load_history(self) -> List[Dict]:
        """File se history load karo."""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning("⚠️  History file corrupted or missing, starting fresh")
            return []
    
    def _save_history(self, history: List[Dict]) -> bool:
        """History ko file mein save karo."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save history: {e}")
            return False
    
    def add_entry(
        self,
        question: str,
        answer: str,
        sources: List[Dict] = None,
        metadata: Dict = None
    ) -> bool:
        """
        Naya chat entry add karo.
        
        Args:
            question: User ka question
            answer: AI ka answer
            sources: Used sources list
            metadata: Extra information
        
        Returns:
            bool: True if saved successfully
        """
        history = self._load_history()
        
        # Naya entry create karo
        entry = {
            "id": len(history) + 1,
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "sources": sources or [],
            "metadata": metadata or {}
        }
        
        history.append(entry)
        
        # Max length maintain karo - purane entries remove karo
        if len(history) > MAX_HISTORY_LENGTH:
            history = history[-MAX_HISTORY_LENGTH:]
            logger.info(f"📊 History trimmed to {MAX_HISTORY_LENGTH} entries")
        
        return self._save_history(history)
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        """
        Recent chat history return karo.
        
        Args:
            limit: Kitne entries return karne hain
        
        Returns:
            List of chat entries (newest first)
        """
        history = self._load_history()
        
        # Recent entries pehle
        recent = list(reversed(history[-limit:]))
        
        return recent
    
    def get_all_history(self) -> List[Dict]:
        """Poori history return karo."""
        return self._load_history()
    
    def clear_history(self) -> bool:
        """
        Saari chat history delete karo.
        
        Returns:
            bool: True if cleared successfully
        """
        success = self._save_history([])
        if success:
            logger.info("🗑️  Chat history cleared!")
        return success
    
    def get_stats(self) -> Dict:
        """Chat history ki statistics."""
        history = self._load_history()
        return {
            "total_conversations": len(history),
            "max_allowed": MAX_HISTORY_LENGTH,
            "file_path": str(self.history_file)
        }
    
    def search_history(self, keyword: str) -> List[Dict]:
        """
        History mein keyword search karo.
        
        Args:
            keyword: Search keyword
        
        Returns:
            Matching entries
        """
        history = self._load_history()
        keyword_lower = keyword.lower()
        
        matches = [
            entry for entry in history
            if (keyword_lower in entry.get("question", "").lower() or
                keyword_lower in entry.get("answer", "").lower())
        ]
        
        return matches


# Singleton
_chat_service_instance = None


def get_chat_service() -> ChatService:
    """ChatService singleton instance."""
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = ChatService()
    return _chat_service_instance