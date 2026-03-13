from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    """State passed through LangGraph workflow"""
    query: str
    session_id: str
    context: str
    agent_name: str
    response: str
    sources: List[dict]
    source_type: str
    knowledge_cutoff_detected: bool
    error: Optional[str]
    tokens_used: int
