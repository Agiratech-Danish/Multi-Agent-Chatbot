from services.rag_service import RAGService
from services.llm_service import LLMService
from typing import Dict, Any

class RetrievalAgent:
    def __init__(self):
        self.rag_service = RAGService()
        self.llm_service = LLMService()
        self.name = "retrieval_agent"
    
    def can_handle(self, query: str) -> bool:
        """Check if this agent can handle the query"""
        keywords = ["search", "find", "what is", "explain", "tell me about", "information"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def _should_use_search(self, response: str) -> bool:
        """Check if LLM couldn't answer from DB - then use search"""
        cutoff_phrases = [
            "i don't have",
            "not in my knowledge",
            "not available",
            "cannot find",
            "no information",
            "not found",
            "unable to",
            "knowledge cutoff",
            "my knowledge",
            "i cannot",
            "i'm not able"
        ]
        return any(phrase in response.lower() for phrase in cutoff_phrases)
    
    def _is_relevant(self, retrieved_context: str, query: str) -> bool:
        """Check if retrieved context is relevant to query"""
        if len(retrieved_context) < 100:
            return False
        query_words = set(query.lower().split())
        context_words = set(retrieved_context.lower().split())
        overlap = len(query_words & context_words) / len(query_words) if query_words else 0
        return overlap > 0.3
    
    def process(self, query: str, context: str = "") -> Dict[str, Any]:
        """Process query using RAG pipeline"""
        try:
            # Check if documents exist
            num_docs = len(self.rag_service.documents)
            print(f"\n RAG Status: {num_docs} documents in vector store")
            
            if num_docs == 0:
                # No documents, use LLM directly
                print(" Using DIRECT LLM (no documents)")
                response, tokens = self.llm_service.generate_response(query, context)
                
                # Check if LLM couldn't answer
                if self._should_use_search(response):
                    print("LLM couldn't answer, routing to search agent")
                    from agents.search_agent import SearchAgent
                    search_agent = SearchAgent()
                    return search_agent.process(query, context)
                
                return {
                    "response": response,
                    "agent": self.name,
                    "sources": [],
                    "source_type": "direct_llm",
                    "tokens_used": tokens,
                    "note": f"Using Direct LLM - No documents uploaded yet. Upload PDFs to enable RAG."
                }
            
            # Retrieve relevant context from documents
            print(f" Using RAG with {num_docs} documents")
            retrieved_context = self.rag_service.retrieve_context(query, k=3)
            sources = self.rag_service.hybrid_search(query, k=3)
            
            # Check if retrieved context is actually relevant
            if not self._is_relevant(retrieved_context, query):
                print(" Retrieved context not relevant, using Direct LLM")
                response, tokens = self.llm_service.generate_response(query, context)
                
                if self._should_use_search(response):
                    print(" LLM couldn't answer, routing to search agent")
                    from agents.search_agent import SearchAgent
                    search_agent = SearchAgent()
                    return search_agent.process(query, context)
                
                return {
                    "response": response,
                    "agent": self.name,
                    "sources": [],
                    "source_type": "direct_llm",
                    "tokens_used": tokens,
                    "note": "Using Direct LLM - Retrieved documents not relevant to query."
                }
            
            # Combine with conversation context
            full_context = f"{context}\n\nRelevant information from uploaded documents:\n{retrieved_context}" if context else f"Based on uploaded documents:\n{retrieved_context}"
            
            # Generate response
            response, tokens = self.llm_service.generate_response(query, full_context)
            
            # Check if LLM couldn't answer
            if self._should_use_search(response):
                print(" LLM couldn't answer, routing to search agent")
                from agents.search_agent import SearchAgent
                search_agent = SearchAgent()
                return search_agent.process(query, context)
            
            return {
                "response": response,
                "agent": self.name,
                "sources": sources,
                "source_type": "rag",
                "tokens_used": tokens,
                "note": f" Using RAG - Answer generated from {num_docs} uploaded documents."
            }
        except Exception as e:
            # Fallback to search agent on error
            print(f" RAG Error: {str(e)}, routing to search agent")
            from agents.search_agent import SearchAgent
            search_agent = SearchAgent()
            return search_agent.process(query, context)
