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
    
    def process_query_stream(self, query: str, session_id: str, db: Session = None, **kwargs):
        """Process query with streaming response"""
        try:
            from services.llm_service import LLMService
            from services.rag_service import RAGService
            
            llm_service = LLMService()
            rag_service = RAGService()
            
            # Build context
            context = self.memory_service.build_context(session_id)
            
            # Get relevant documents
            rag_context = rag_service.retrieve_context(query, k=3)
            full_context = f"{context}\n\n{rag_context}"
            
            # Stream response
            for chunk in llm_service.generate_response_stream(query, full_context):
                yield chunk
                
        except Exception as e:
            yield f"Error: {str(e)}"
