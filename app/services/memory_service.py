from typing import List, Dict
from models.schemas import ChatMessage
from core.config import get_settings
import json
import os

settings = get_settings()

class MemoryService:
    def __init__(self):
        self.use_redis = os.getenv("USE_REDIS", "false").lower() == "true"
        self.max_context = settings.max_context_length
        
        if self.use_redis:
            import redis
            self.redis_client = redis.from_url(settings.redis_url)
            self.memory = None
        else:
            # FREE: Use in-memory dictionary (no Redis needed)
            self.redis_client = None
            self.memory = {}
    
    def add_message(self, session_id: str, message: ChatMessage):
        if self.use_redis:
            key = f"session:{session_id}:messages"
            self.redis_client.lpush(key, message.model_dump_json())
            self.redis_client.ltrim(key, 0, self.max_context - 1)
        else:
            if session_id not in self.memory:
                self.memory[session_id] = []
            self.memory[session_id].insert(0, message)
            self.memory[session_id] = self.memory[session_id][:self.max_context]
    
    def get_recent_messages(self, session_id: str) -> List[ChatMessage]:
        if self.use_redis:
            key = f"session:{session_id}:messages"
            messages = self.redis_client.lrange(key, 0, -1)
            return [ChatMessage(**json.loads(msg)) for msg in messages]
        else:
            return self.memory.get(session_id, [])
    
    def build_context(self, session_id: str) -> str:
        messages = self.get_recent_messages(session_id)
        # Include all messages for better context
        context = "\n".join([f"{msg.role}: {msg.content}" for msg in reversed(messages)])
        return context
    
    def clear_session(self, session_id: str):
        if self.use_redis:
            key = f"session:{session_id}:messages"
            self.redis_client.delete(key)
        else:
            if session_id in self.memory:
                del self.memory[session_id]
