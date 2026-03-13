from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
import os

# Get the project root directory (2 levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    # LLM Configuration
    GROQ_API_KEY: str
    USE_OLLAMA: bool = False
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama-3.1-8b-instant"
    TEMPERATURE: float = 0.3
    
    # Database
    DATABASE_URL: str
    
    # Redis
    USE_REDIS: bool = True
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Vector Store
    VECTOR_DB_PATH: str
    MAX_CONTEXT_LENGTH: int = 5
    
    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = 'ignore'

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
