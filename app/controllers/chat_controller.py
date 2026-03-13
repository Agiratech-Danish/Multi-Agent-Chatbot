from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from models.schemas import ChatRequest, ChatResponse
from services.orchestration_service import OrchestrationService
from core.database import get_db
from models.database import ChatSession, ChatHistory, Document
import uuid
import json

router = APIRouter(prefix="/api/chat", tags=["chat"])
orchestration_service = OrchestrationService()

@router.post("/message/stream")
async def send_message_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """Send a message and get streaming response like ChatGPT"""
    def generate():
        try:
            session = db.query(ChatSession).filter(
                ChatSession.session_id == request.session_id
            ).first()
            
            if not session:
                session = ChatSession(session_id=request.session_id)
                db.add(session)
                db.commit()
            
            previous_messages = db.query(ChatHistory).filter(
                ChatHistory.session_id == session.id
            ).order_by(ChatHistory.timestamp).all()
            
            context_parts = []
            for msg in previous_messages[-10:]:
                context_parts.append(f"{msg.role}: {msg.content}")
            full_context = "\n".join(context_parts)
            
            # Stream the response
            full_response = ""
            result = orchestration_service.process_query_stream(
                request.message,
                request.session_id,
                db=db,
                context=full_context
            )
            
            for chunk in result:
                if isinstance(chunk, dict):
                    # Metadata chunk
                    yield f"data: {json.dumps(chunk)}\n\n"
                else:
                    # Text chunk
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Save to database
            user_msg = ChatHistory(
                session_id=session.id,
                role="user",
                content=request.message
            )
            assistant_msg = ChatHistory(
                session_id=session.id,
                role="assistant",
                content=full_response
            )
            db.add(user_msg)
            db.add(assistant_msg)
            db.commit()
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    """Send a message and get response"""
    try:
        # Get full conversation history for context
        session = db.query(ChatSession).filter(
            ChatSession.session_id == request.session_id
        ).first()
        
        if not session:
            session = ChatSession(session_id=request.session_id)
            db.add(session)
            db.commit()
        
        # Get all previous messages for context
        previous_messages = db.query(ChatHistory).filter(
            ChatHistory.session_id == session.id
        ).order_by(ChatHistory.timestamp).all()
        
        # Build context from all messages
        context_parts = []
        for msg in previous_messages[-10:]:  # Last 10 messages
            context_parts.append(f"{msg.role}: {msg.content}")
        full_context = "\n".join(context_parts)
        
        # Process query with full context
        result = orchestration_service.process_query(
            request.message,
            request.session_id,
            db=db,
            context=full_context
        )
        
        # Save OCR extracted text to documents table
        if result["agent"] == "ocr_agent" and "extracted_text" in result:
            doc = Document(
                filename=f"ocr_{uuid.uuid4()}.txt",
                content=result["extracted_text"],
                user_id=1,
                embedding_id=str(uuid.uuid4())
            )
            db.add(doc)
        
        # Save chat history
        user_msg = ChatHistory(
            session_id=session.id,
            role="user",
            content=request.message
        )
        assistant_msg = ChatHistory(
            session_id=session.id,
            role="assistant",
            content=result["response"]
        )
        db.add(user_msg)
        db.add(assistant_msg)
        db.commit()
        
        # Convert sources to dict if they are Pydantic models
        sources = result.get("sources", [])
        if sources and hasattr(sources[0], 'model_dump'):
            sources = [s.model_dump() for s in sources]
        
        return ChatResponse(
            response=result["response"],
            sources=sources,
            agent_used=result["agent"],
            session_id=request.session_id,
            source_type=result.get("source_type", "unknown"),
            note=result.get("note", ""),
            tokens_used=result.get("tokens_used", 0)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/new")
async def create_session():
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}

@router.get("/session/{session_id}/history")
async def get_history(session_id: str, db: Session = Depends(get_db)):
    """Get chat history for a session"""
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(ChatHistory).filter(
        ChatHistory.session_id == session.id
    ).order_by(ChatHistory.timestamp).all()
    
    return {"messages": messages}
