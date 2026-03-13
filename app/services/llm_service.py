from openai import OpenAI
from core.config import get_settings
import os
from dotenv import load_dotenv
import hashlib

# Load .env file explicitly
load_dotenv()

class LLMService:
    def __init__(self):
        settings = get_settings()
        self.use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
        self.response_cache = {}  # Cache for identical queries
        
        if self.use_ollama:
            self.client = OpenAI(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                api_key="ollama"
            )
            self.model = os.getenv("LLM_MODEL", "llama2")
        elif os.getenv("GROQ_API_KEY"):
            self.client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=os.getenv("GROQ_API_KEY")
            )
            self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        else:
            openai_key = os.getenv("OPENAI_API_KEY") or getattr(settings, 'openai_api_key', None)
            if not openai_key:
                raise ValueError("No LLM API key found. Set GROQ_API_KEY, OPENAI_API_KEY, or USE_OLLAMA=true")
            self.client = OpenAI(api_key=openai_key)
            self.model = os.getenv("LLM_MODEL", settings.llm_model)
        
        self.temperature = float(os.getenv("TEMPERATURE", settings.temperature))
    
    def generate_response(self, prompt: str, context: str = "", use_cache: bool = True) -> tuple:
        """Generate response and return (response, token_count)"""
        # Create cache key from prompt + context
        cache_key = hashlib.md5(f"{prompt}{context}".encode()).hexdigest()
        
        # Return cached response if exists and cache is enabled
        if use_cache and cache_key in self.response_cache:
            cached_response, cached_tokens = self.response_cache[cache_key]
            return cached_response, cached_tokens
        
        system_message = "You are a helpful AI assistant. Answer based on the provided context."
        
        # Limit context to prevent token overflow
        if context:
            context = context[:2000]  # ~500 tokens max
            system_message += f"\n\nContext:\n{context}"
        
        # Limit prompt size
        prompt = prompt[:1000]  # ~250 tokens max
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=500  # Limit response size
            )
            result = response.choices[0].message.content
            
            # Calculate tokens (approximate: 1 token ≈ 4 chars)
            input_tokens = len(str(messages)) // 4
            output_tokens = len(result) // 4
            total_tokens = input_tokens + output_tokens
            
            if use_cache:
                self.response_cache[cache_key] = (result, total_tokens)
            
            return result, total_tokens
        except Exception as e:
            if "rate_limit" in str(e).lower() or "413" in str(e):
                return "Rate limit exceeded. Please try again in a moment.", 0
            raise
    
    def generate_with_history(self, messages: list) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature
        )
        
        return response.choices[0].message.content
