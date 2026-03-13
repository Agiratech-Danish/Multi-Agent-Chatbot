from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes import (
    router_node,
    retrieval_node,
    ocr_node,
    data_node,
    search_node,
    memory_node
)

def build_workflow():
    """Build LangGraph workflow"""
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("retrieval_agent", retrieval_node)
    workflow.add_node("ocr_agent", ocr_node)
    workflow.add_node("data_agent", data_node)
    workflow.add_node("search_agent", search_node)
    workflow.add_node("memory", memory_node)
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Conditional routing based on agent_name
    workflow.add_conditional_edges(
        "router",
        lambda state: state["agent_name"],
        {
            "data_agent": "data_agent",
            "ocr_agent": "ocr_agent",
            "retrieval_agent": "retrieval_agent"
        }
    )
    
    # Check for knowledge cutoff after retrieval
    def should_use_search(state: AgentState) -> str:
        if state["knowledge_cutoff_detected"]:
            return "search_agent"
        return "memory"
    
    workflow.add_conditional_edges(
        "retrieval_agent",
        should_use_search,
        {
            "search_agent": "search_agent",
            "memory": "memory"
        }
    )
    
    # Direct edges to memory for other agents
    workflow.add_edge("ocr_agent", "memory")
    workflow.add_edge("data_agent", "memory")
    workflow.add_edge("search_agent", "memory")
    
    # Set finish point
    workflow.set_finish_point("memory")
    
    # Compile
    return workflow.compile()

# Create singleton instance
_workflow = None

def get_workflow():
    """Get or create workflow"""
    global _workflow
    if _workflow is None:
        _workflow = build_workflow()
    return _workflow
