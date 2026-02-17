"""
Memory Manager - Handles memory storage and retrieval
Implements session-based memory management with persistence
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
import os


class MemoryManager:
    """Manages conversation memory and context storage"""
    
    def __init__(self, memory_file: str = "memory_store.json"):
        self.memory_file = memory_file
        self.short_term_memory = []  # Current session memory
        self.long_term_memory = []   # Persistent memory across sessions
        self.context_window = 10     # Number of recent messages to keep in context
        self.load_memory()
    
    def add_to_memory(self, content: str, memory_type: str, metadata: Optional[Dict] = None):
        """Add new item to memory"""
        memory_item = {
            'content': content,
            'type': memory_type,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.short_term_memory.append(memory_item)
        
        # Add important items to long-term memory
        if self._is_important(content, memory_type):
            self.long_term_memory.append(memory_item)
            self.save_memory()
        
        # Maintain memory window size
        if len(self.short_term_memory) > self.context_window * 2:
            self.short_term_memory = self.short_term_memory[-self.context_window * 2:]
    
    def get_recent_context(self, n: int = None) -> List[Dict]:
        """Get recent conversation context"""
        n = n or self.context_window
        return self.short_term_memory[-n:]
    
    def get_relevant_memories(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve relevant memories based on query (simple keyword matching)"""
        query_keywords = set(query.lower().split())
        scored_memories = []
        
        for memory in self.long_term_memory:
            memory_keywords = set(memory['content'].lower().split())
            overlap = len(query_keywords & memory_keywords)
            
            if overlap > 0:
                scored_memories.append({
                    'memory': memory,
                    'score': overlap
                })
        
        # Sort by relevance score
        scored_memories.sort(key=lambda x: x['score'], reverse=True)
        return [item['memory'] for item in scored_memories[:top_k]]
    
    def search_memory(self, keyword: str) -> List[Dict]:
        """Search memory for specific keyword"""
        results = []
        keyword_lower = keyword.lower()
        
        all_memories = self.short_term_memory + self.long_term_memory
        for memory in all_memories:
            if keyword_lower in memory['content'].lower():
                results.append(memory)
        
        return results
    
    def get_all_memories(self) -> List[Dict]:
        """Get all stored memories"""
        return self.long_term_memory
    
    def get_memory_count(self) -> int:
        """Get total memory count"""
        return len(self.short_term_memory) + len(self.long_term_memory)
    
    def save_memory(self):
        """Save long-term memory to file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump({
                    'long_term_memory': self.long_term_memory,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def load_memory(self):
        """Load long-term memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.long_term_memory = data.get('long_term_memory', [])
        except Exception as e:
            print(f"Error loading memory: {e}")
            self.long_term_memory = []
    
    def save_session(self, session_id: str, messages: List[Dict]):
        """Save entire conversation session"""
        session_file = f"sessions/session_{session_id}.json"
        os.makedirs("sessions", exist_ok=True)
        
        try:
            with open(session_file, 'w') as f:
                json.dump({
                    'session_id': session_id,
                    'messages': messages,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def load_session(self, session_id: str) -> Optional[List[Dict]]:
        """Load a previous conversation session"""
        session_file = f"sessions/session_{session_id}.json"
        
        try:
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    return data.get('messages', [])
        except Exception as e:
            print(f"Error loading session: {e}")
        
        return None
    
    def get_user_preferences(self) -> Dict:
        """Extract user preferences from memory"""
        preferences = {}
        
        for memory in self.long_term_memory:
            if 'preference' in memory['type']:
                key = memory.get('metadata', {}).get('preference_type', 'general')
                preferences[key] = memory['content']
        
        return preferences
    
    def summarize_session(self, messages: List[Dict]) -> str:
        """Generate a summary of the conversation session"""
        if not messages:
            return "No conversation to summarize."
        
        user_messages = [m for m in messages if m['role'] == 'user']
        assistant_messages = [m for m in messages if m['role'] == 'assistant']
        
        summary = f"""
Conversation Summary:
- Total messages: {len(messages)}
- User messages: {len(user_messages)}
- Assistant responses: {len(assistant_messages)}
- Duration: {self._calculate_duration(messages)}

Key Topics Discussed:
{self._extract_key_topics(messages)}
"""
        return summary.strip()
    
    def _is_important(self, content: str, memory_type: str) -> bool:
        """Determine if memory item should be stored long-term"""
        important_keywords = [
            'remember', 'important', 'prefer', 'always', 'never',
            'my name is', 'i am', 'i work', 'i like', 'i need'
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in important_keywords)
    
    def _calculate_duration(self, messages: List[Dict]) -> str:
        """Calculate conversation duration"""
        if len(messages) < 2:
            return "N/A"
        
        try:
            start_time = datetime.fromisoformat(messages[0].get('timestamp', ''))
            end_time = datetime.fromisoformat(messages[-1].get('timestamp', ''))
            duration = end_time - start_time
            
            minutes = int(duration.total_seconds() / 60)
            if minutes < 1:
                return "Less than a minute"
            elif minutes == 1:
                return "1 minute"
            else:
                return f"{minutes} minutes"
        except:
            return "N/A"
    
    def _extract_key_topics(self, messages: List[Dict]) -> str:
        """Extract key topics from conversation"""
        user_messages = [m['content'] for m in messages if m['role'] == 'user']
        
        if not user_messages:
            return "- No topics identified"
        
        # Simple topic extraction based on first few words
        topics = []
        for msg in user_messages[:5]:  # Get first 5 user messages
            words = msg.split()[:5]  # First 5 words
            topic = ' '.join(words) + '...'
            topics.append(f"- {topic}")
        
        return '\n'.join(topics) if topics else "- No topics identified"
    
    def clear_memory(self):
        """Clear all memory (use with caution)"""
        self.short_term_memory = []
        self.long_term_memory = []
        self.save_memory()