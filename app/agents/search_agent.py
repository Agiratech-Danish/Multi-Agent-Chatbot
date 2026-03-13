import requests
from typing import Dict, Any
from services.llm_service import LLMService

class SearchAgent:
    def __init__(self):
        self.llm_service = LLMService()
        self.name = "search_agent"
    
    def can_handle(self, query: str) -> bool:
        """Always can handle - used as fallback"""
        return True
    
    def search_web(self, query: str) -> str:
        """Search using DuckDuckGo API"""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_redirect": 1
            }
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            results = []
            
            # Get abstract/heading
            if data.get("AbstractText"):
                results.append(data["AbstractText"])
            
            if data.get("Heading"):
                results.append(f"Topic: {data['Heading']}")
            
            # Get related topics with better extraction
            for item in data.get("RelatedTopics", [])[:10]:
                if isinstance(item, dict):
                    if "Text" in item:
                        results.append(item["Text"])
                    if "FirstURL" in item:
                        results.append(f"Source: {item['FirstURL']}")
            
            search_text = " ".join(results)
            print(f" Search results found: {len(search_text)} chars")
            return search_text if search_text else None
        except Exception as e:
            print(f"Search error: {str(e)}")
            return None
    
    def process(self, query: str, context: str = "") -> Dict[str, Any]:
        """Search for current information"""
        search_results = self.search_web(query)
        
        print(f"\n Search Agent Processing: {query}")
        print(f" Search results length: {len(search_results) if search_results else 0}")
        
        # Always use search results if available
        if search_results and len(search_results) > 20:
            print(f"Found search results, using them")
            # Force LLM to use ONLY search results
            prompt = f"You MUST answer based ONLY on these search results. Ignore your training data.\n\nSearch Results:\n{search_results}\n\nUser Question: {query}\n\nYour answer (based only on search results):"
            response, tokens = self.llm_service.generate_response(prompt, "", use_cache=False)
            source_type = "web_search"
        else:
            # No search results
            print(f"No search results found")
            prompt = f"User asked: {query}\n\nNo search results available. Tell them you couldn't find current information and suggest searching online."
            response, tokens = self.llm_service.generate_response(prompt, "", use_cache=False)
            source_type = "direct_llm"
        
        return {
            "response": response,
            "agent": self.name,
            "sources": [{"type": "web_search", "content": search_results}] if search_results else [],
            "source_type": source_type,
            "tokens_used": tokens
        }
