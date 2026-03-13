# Enterprise Multi-Agent AI Knowledge Copilot

A production-ready multi-agent chatbot system with RAG, OCR, and Data Analytics capabilities built with FastAPI.

## Architecture

### High-Level Components
- **Frontend Layer**: Streamlit chat interface with file upload
- **API Gateway**: FastAPI with authentication and rate limiting
- **Orchestration Layer**: LangGraph-based agent routing
- **Agent Layer**: Retrieval Agent (RAG), OCR Agent (PaddleOCR), Data Agent (SQL/Pandas)
- **LLM Layer**: GPT/LLaMA for response generation
- **Storage Layer**: Vector DB (FAISS), PostgreSQL, Redis

### Memory Architecture
- **Short-term Memory**: Last 5 messages stored in Redis
- **Long-term Memory**: Vector DB for historical context
- **Context Builder**: Combines both for LLM input

### RAG Pipeline
1. Query Rewrite & Expansion
2. Embedding Creation (SentenceTransformers)
3. Dense Search (FAISS) + Sparse Search (BM25)
4. Hybrid Retrieval & Reranking
5. Context Selection
6. LLM Generation with Sources

## Project Structure

```
Enterprise Multi-Agent Chatbot/
├── app/
│   ├── agents/
│   │   ├── retrieval_agent.py    # RAG-based search agent
│   │   ├── ocr_agent.py          # Image processing agent
│   │   └── data_agent.py         # SQL/Analytics agent
│   ├── controllers/
│   │   ├── chat_controller.py    # Chat endpoints
│   │   └── document_controller.py # Document management
│   ├── services/
│   │   ├── orchestration_service.py  # Agent routing
│   │   ├── memory_service.py         # Conversation memory
│   │   ├── rag_service.py            # RAG pipeline
│   │   ├── embedding_service.py      # Vector operations
│   │   └── llm_service.py            # LLM integration
│   ├── models/
│   │   ├── schemas.py            # Pydantic models
│   │   └── database.py           # SQLAlchemy models
│   ├── core/
│   │   ├── config.py             # Configuration
│   │   └── database.py           # DB connection
│   └── main.py                   # FastAPI app
├── requirements.txt
└── .env.example
```

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- PostgreSQL
- Redis

### 2. Installation

```bash
# Clone repository
cd "c:\Project\Enterprise Multi-Agent Chatbot"

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment file
copy .env.example .env

# Edit .env with your credentials
# - OPENAI_API_KEY
# - DATABASE_URL
# - REDIS_URL
# - SECRET_KEY
```

### 4. Database Setup

```bash
# Create PostgreSQL database
createdb chatbot_db

# Tables will be created automatically on first run
```

### 5. Run Application

```bash
# Start FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access API docs
# http://localhost:8000/docs
```

## API Endpoints

### Chat
- `POST /api/chat/message` - Send message and get response
- `POST /api/chat/session/new` - Create new chat session
- `GET /api/chat/session/{session_id}/history` - Get chat history

### Documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents/list` - List documents
- `DELETE /api/documents/{document_id}` - Delete document

## Usage Example

```python
import requests

# Create session
response = requests.post("http://localhost:8000/api/chat/session/new")
session_id = response.json()["session_id"]

# Send message
payload = {
    "message": "What is machine learning?",
    "session_id": session_id
}
response = requests.post("http://localhost:8000/api/chat/message", json=payload)
print(response.json())
```

## Agent Routing Logic

The orchestration service automatically routes queries to the appropriate agent:

- **Data Agent**: Queries containing "data", "sql", "analytics", "statistics"
- **OCR Agent**: Queries containing "image", "ocr", "extract text", "scan"
- **Retrieval Agent**: Default for general knowledge queries

## Features

✅ Multi-agent architecture with intelligent routing  
✅ RAG pipeline with hybrid search (dense + sparse)  
✅ Conversation memory (short-term + long-term)  
✅ OCR capabilities with PaddleOCR  
✅ SQL and data analytics support  
✅ Document upload and processing  
✅ Vector storage with FAISS  
✅ PostgreSQL for persistent storage  
✅ Redis for session management  
✅ FastAPI with automatic API docs  

## Next Steps

1. Add authentication middleware
2. Implement rate limiting
3. Create Streamlit frontend
4. Add monitoring and logging
5. Deploy with Docker
6. Add more specialized agents
7. Implement reranking model
8. Add streaming responses

## License

MIT
