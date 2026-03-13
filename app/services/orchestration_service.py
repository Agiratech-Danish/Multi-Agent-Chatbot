from typing import Dict, Any
from agents.graph import get_workflow
from services.memory_service import MemoryService
from sqlalchemy.orm import Session

class OrchestrationService:
    def __init__(self):
        self.workflow = get_workflow()
        self.memory_service = MemoryService()
    
    def process_query(self, query: str, session_id: str, db: Session = None, **kwargs) -> Dict[str, Any]:
        """Process query through LangGraph workflow"""
        try:
            # Build context from memory
            context = self.memory_service.build_context(session_id)
            
            # Initialize state
            state = {
                "query": query,
                "session_id": session_id,
                "context": context,
                "agent_name": "",
                "response": "",
                "sources": [],
                "source_type": "",
                "knowledge_cutoff_detected": False,
                "error": None
            }
            
            # Execute workflow
            result = self.workflow.invoke(state)
            
            return {
                "response": result["response"],
                "agent": result["agent_name"],
                "sources": result["sources"],
                "source_type": result["source_type"]
            }
        except Exception as e:
            return {
                "response": f"I encountered an error: {str(e)}",
                "agent": "error",
                "sources": [],
                "error": str(e)
            }
