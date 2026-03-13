from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.database import Document
from services.rag_service import RAGService
from agents.ocr_agent import OCRAgent
import uuid
import PyPDF2
import io
import os
from pathlib import Path

router = APIRouter(prefix="/api/documents", tags=["documents"])
rag_service = RAGService()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """Upload and process document"""
    try:
        content = await file.read()
        
        # Extract text based on file type
        if file.filename.endswith('.pdf'):
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
        elif file.filename.endswith(('.txt', '.md')):
            # Decode text files
            text_content = content.decode('utf-8')
        elif file.filename.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            # Extract text from image using OCR
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
                tmp.write(content)
                temp_path = tmp.name
            try:
                ocr_agent = OCRAgent()
                text_content = ocr_agent.extract_text(temp_path)
            finally:
                os.remove(temp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Supported: PDF, TXT, MD, JPG, JPEG, PNG, BMP, GIF")
        
        # Save to database
        doc = Document(
            filename=file.filename,
            content=text_content,
            user_id=user_id,
            embedding_id=str(uuid.uuid4())
        )
        db.add(doc)
        db.commit()
        
        # Add to vector store
        rag_service.add_documents([text_content])
        
        return {
            "message": "Document uploaded successfully",
            "document_id": doc.id,
            "filename": file.filename
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_documents(user_id: int = 1, db: Session = Depends(get_db)):
    """List all documents for a user"""
    documents = db.query(Document).filter(Document.user_id == user_id).all()
    return {"documents": documents}

@router.delete("/faiss/clear-all")
async def clear_faiss():
    """Clear all FAISS embeddings and documents"""
    try:
        from services.embedding_service import EmbeddingService
        from pathlib import Path
        import shutil
        import os
        
        embedding_service = EmbeddingService()
        vector_path = embedding_service.vector_path
        
        # Delete FAISS files
        if vector_path.exists():
            for file in vector_path.glob("*"):
                if file.is_file():
                    os.remove(file)
        
        # Reset RAG service singleton
        from services.rag_service import RAGService
        rag_service = RAGService()
        rag_service.documents = []
        rag_service.bm25 = None
        rag_service.embedding_service.documents = []
        
        return {"message": "FAISS data cleared successfully", "status": "cleared"}
    except Exception as e:
        print(f"Error clearing FAISS: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear FAISS: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully"}
