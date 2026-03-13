import pandas as pd
from sqlalchemy import create_engine, text
from typing import Dict, Any
from services.llm_service import LLMService
from core.config import get_settings

settings = get_settings()

class DataAgent:
    def __init__(self):
        self.llm_service = LLMService()
        self.engine = create_engine(settings.database_url)
        self.name = "data_agent"
    
    def can_handle(self, query: str) -> bool:
        """Check if this agent can handle the query"""
        keywords = ["data", "sql", "query", "database", "analytics", "statistics", "analyze"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def execute_sql(self, sql_query: str) -> pd.DataFrame:
        """Execute SQL query and return results"""
        with self.engine.connect() as conn:
            result = pd.read_sql(text(sql_query), conn)
        return result
    
    def analyze_dataframe(self, df: pd.DataFrame, query: str) -> tuple:
        """Analyze dataframe using pandas"""
        summary = df.describe().to_string()
        prompt = f"Analyze this data and answer the query.\n\nData Summary:\n{summary}\n\nQuery: {query}"
        return self.llm_service.generate_response(prompt)
    
    def process(self, query: str, sql_query: str = None, context: str = "") -> Dict[str, Any]:
        """Process data query"""
        if sql_query:
            try:
                df = self.execute_sql(sql_query)
                analysis, tokens = self.analyze_dataframe(df, query)
                
                return {
                    "response": analysis,
                    "agent": self.name,
                    "data": df.to_dict(),
                    "sources": [{"type": "sql", "query": sql_query}],
                    "tokens_used": tokens
                }
            except Exception as e:
                return {
                    "response": f"Error executing query: {str(e)}",
                    "agent": self.name,
                    "sources": [],
                    "tokens_used": 0
                }
        else:
            response, tokens = self.llm_service.generate_response(query, context)
            return {
                "response": response,
                "agent": self.name,
                "sources": [],
                "tokens_used": tokens
            }
