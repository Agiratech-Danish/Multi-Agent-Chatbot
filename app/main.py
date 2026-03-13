from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers import chat_controller, document_controller
from core.database import engine, Base
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Create database tables (with error handling)
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database connected")
except Exception as e:
    print(f"⚠️ Database connection failed: {str(e)}")
    print("⚠️ Make sure PostgreSQL is running and credentials are correct")
    print(f"⚠️ Continuing without database...")

app = FastAPI(
    title="Enterprise Multi-Agent AI Knowledge Copilot",
    description="Multi-agent chatbot with RAG, OCR, and Data Analytics capabilities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_controller.router)
app.include_router(document_controller.router)

@app.get("/")
async def root():
    return {
        "message": "Enterprise Multi-Agent AI Knowledge Copilot API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat/message",
            "documents": "/api/documents/upload",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Get host and port from command line args or use defaults
    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    
    print(f"🚀 Starting server at http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    uvicorn.run(app, host=host, port=port)
