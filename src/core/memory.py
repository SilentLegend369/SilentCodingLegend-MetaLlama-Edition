"""
Memory management for conversation history
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ConversationMemory:
    """Manages conversation history and context"""
    
    def __init__(self, storage_dir: str = "data/conversations"):
        self.storage_dir = storage_dir
        self.conversations: Dict[str, List[Dict]] = {}
        self.max_messages_per_session = 100
        self.session_timeout_hours = 24
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Load existing conversations
        self._load_conversations()
    
    def add_message(
        self, 
        session_id: Optional[str], 
        role: str, 
        content: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Add a message to the conversation history"""
        if session_id is None:
            session_id = self._generate_session_id()
        
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversations[session_id].append(message)
        
        # Keep only the most recent messages
        if len(self.conversations[session_id]) > self.max_messages_per_session:
            self.conversations[session_id] = self.conversations[session_id][-self.max_messages_per_session:]
        
        # Save to storage
        self._save_conversation(session_id)
    
    def get_conversation(self, session_id: Optional[str]) -> List[Dict]:
        """Get conversation history for a session"""
        if session_id is None or session_id not in self.conversations:
            return []
        
        # Clean up old messages
        cutoff_time = datetime.now() - timedelta(hours=self.session_timeout_hours)
        
        filtered_messages = []
        for message in self.conversations[session_id]:
            try:
                message_time = datetime.fromisoformat(message["timestamp"])
                if message_time > cutoff_time:
                    filtered_messages.append(message)
            except (ValueError, KeyError):
                # Keep messages without valid timestamps
                filtered_messages.append(message)
        
        self.conversations[session_id] = filtered_messages
        return filtered_messages
    
    def clear_session(self, session_id: str) -> bool:
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]
            
            # Remove from storage
            session_file = os.path.join(self.storage_dir, f"{session_id}.json")
            if os.path.exists(session_file):
                os.remove(session_file)
            
            return True
        return False
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        cutoff_time = datetime.now() - timedelta(hours=self.session_timeout_hours)
        active_sessions = []
        
        for session_id, messages in self.conversations.items():
            if messages:
                try:
                    last_message_time = datetime.fromisoformat(messages[-1]["timestamp"])
                    if last_message_time > cutoff_time:
                        active_sessions.append(session_id)
                except (ValueError, KeyError, IndexError):
                    # Keep sessions with invalid timestamps
                    active_sessions.append(session_id)
        
        return active_sessions
    
    def get_session_summary(self, session_id: str) -> Dict:
        """Get summary information about a session"""
        if session_id not in self.conversations:
            return {}
        
        messages = self.conversations[session_id]
        if not messages:
            return {}
        
        return {
            "session_id": session_id,
            "message_count": len(messages),
            "start_time": messages[0].get("timestamp"),
            "last_activity": messages[-1].get("timestamp"),
            "user_messages": len([m for m in messages if m["role"] == "user"]),
            "assistant_messages": len([m for m in messages if m["role"] == "assistant"])
        }
    
    def search_conversations(self, query: str, session_id: Optional[str] = None) -> List[Dict]:
        """Search for messages containing a query"""
        results = []
        
        sessions_to_search = [session_id] if session_id else self.conversations.keys()
        
        for sid in sessions_to_search:
            if sid in self.conversations:
                for i, message in enumerate(self.conversations[sid]):
                    if query.lower() in message["content"].lower():
                        results.append({
                            "session_id": sid,
                            "message_index": i,
                            "message": message
                        })
        
        return results
    
    def _generate_session_id(self) -> str:
        """Generate a new session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
    
    def _load_conversations(self) -> None:
        """Load conversations from storage"""
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    session_id = filename[:-5]  # Remove .json extension
                    self._load_conversation(session_id)
        except FileNotFoundError:
            logger.info("No existing conversations found")
        except Exception as e:
            logger.error(f"Error loading conversations: {e}")
    
    def _load_conversation(self, session_id: str) -> None:
        """Load a specific conversation from storage"""
        try:
            session_file = os.path.join(self.storage_dir, f"{session_id}.json")
            if os.path.exists(session_file):
                with open(session_file, 'r', encoding='utf-8') as f:
                    self.conversations[session_id] = json.load(f)
        except Exception as e:
            logger.error(f"Error loading conversation {session_id}: {e}")
    
    def _save_conversation(self, session_id: str) -> None:
        """Save a conversation to storage"""
        try:
            session_file = os.path.join(self.storage_dir, f"{session_id}.json")
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations[session_id], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving conversation {session_id}: {e}")
    
    def cleanup_old_sessions(self) -> int:
        """Clean up old/expired sessions"""
        cutoff_time = datetime.now() - timedelta(hours=self.session_timeout_hours)
        sessions_to_remove = []
        
        for session_id, messages in self.conversations.items():
            if messages:
                try:
                    last_message_time = datetime.fromisoformat(messages[-1]["timestamp"])
                    if last_message_time <= cutoff_time:
                        sessions_to_remove.append(session_id)
                except (ValueError, KeyError):
                    continue
        
        # Remove old sessions
        for session_id in sessions_to_remove:
            self.clear_session(session_id)
        
        logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
        return len(sessions_to_remove)