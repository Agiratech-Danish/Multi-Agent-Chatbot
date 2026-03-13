from agents.state import AgentState
from services.memory_service import MemoryService

memory_service = MemoryService()

def router_node(state: AgentState) -> AgentState:
    """Route query to appropriate agent"""
    query = state["query"]
    
    # Data Agent
    if any(keyword in query.lower() for keyword in ["data", "sql", "analytics", "statistics"]):
        state["agent_name"] = "data_agent"
    # OCR Agent
    elif any(keyword in query.lower() for keyword in ["image", "ocr", "extract text", "read", "scan", "picture"]):
        state["agent_name"] = "ocr_agent"
    # Retrieval Agent (default)
    else:
        state["agent_name"] = "retrieval_agent"
    
    print(f"🔀 Routed to: {state['agent_name']}")
    return state

def retrieval_node(state: AgentState) -> AgentState:
    """Process with retrieval agent"""
    from agents.retrieval_agent import RetrievalAgent
    
    agent = RetrievalAgent()
    result = agent.process(state["query"], state["context"])
    
    state["response"] = result["response"]
    state["sources"] = result.get("sources", [])
    state["source_type"] = result.get("source_type", "unknown")
    state["agent_name"] = result.get("agent", "retrieval_agent")
    state["tokens_used"] = result.get("tokens_used", 0)
    
    return state

def ocr_node(state: AgentState) -> AgentState:
    """Process with OCR agent"""
    from agents.ocr_agent import OCRAgent
    
    agent = OCRAgent()
    result = agent.process(state["query"], None, state["context"])
    
    state["response"] = result["response"]
    state["sources"] = result.get("sources", [])
    state["source_type"] = result.get("source_type", "unknown")
    
    return state

def data_node(state: AgentState) -> AgentState:
    """Process with data agent"""
    from agents.data_agent import DataAgent
    
    agent = DataAgent()
    result = agent.process(state["query"], None, state["context"])
    
    state["response"] = result["response"]
    state["sources"] = result.get("sources", [])
    state["source_type"] = result.get("source_type", "unknown")
    
    return state

def search_node(state: AgentState) -> AgentState:
    """Process with search agent"""
    from agents.search_agent import SearchAgent
    
    agent = SearchAgent()
    result = agent.process(state["query"], state["context"])
    
    state["response"] = result["response"]
    state["sources"] = result.get("sources", [])
    state["source_type"] = result.get("source_type", "web_search")
    
    return state

def memory_node(state: AgentState) -> AgentState:
    """Store messages in memory"""
    from models.schemas import ChatMessage
    from datetime import datetime
    
    user_msg = ChatMessage(role="user", content=state["query"], timestamp=datetime.utcnow())
    assistant_msg = ChatMessage(role="assistant", content=state["response"], timestamp=datetime.utcnow())
    
    memory_service.add_message(state["session_id"], user_msg)
    memory_service.add_message(state["session_id"], assistant_msg)
    
    return state
