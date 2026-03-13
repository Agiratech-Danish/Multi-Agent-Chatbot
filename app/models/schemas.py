from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[Dict[str, Any]]] = []
    agent_used: str
    session_id: str
    source_type: Optional[str] = "unknown"
    note: Optional[str] = ""
    tokens_used: Optional[int] = 0

class DocumentUpload(BaseModel):
    filename: str
    content: str
    user_id: str

class QueryRewrite(BaseModel):
    original_query: str
    rewritten_query: str
    expanded_queries: List[str]

class RetrievalResult(BaseModel):
    content: str
    score: float
    source: str
    metadata: Dict[str, Any]
