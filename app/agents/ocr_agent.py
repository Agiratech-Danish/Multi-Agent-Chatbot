from paddleocr import PaddleOCR
import cv2
import numpy as np
from typing import Dict, Any
from services.llm_service import LLMService

class OCRAgent:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
        self.llm_service = LLMService()
        self.name = "ocr_agent"
    
    def can_handle(self, query: str) -> bool:
        """Check if this agent can handle the query"""
        keywords = ["image", "ocr", "extract text", "read", "scan", "picture"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def extract_text(self, image_path: str) -> str:
        """Extract text from image using PaddleOCR"""
        result = self.ocr.ocr(image_path)
        
        extracted_text = []
        if result and result[0]:
            for line in result[0]:
                text = line[1][0]
                extracted_text.append(text)
        
        return "\n".join(extracted_text) if extracted_text else "No text found in image"
    
    def process(self, query: str, image_path: str = None, context: str = "") -> Dict[str, Any]:
        """Process image and answer query"""
        if not image_path:
            return {
                "response": "Please provide an image to process.",
                "agent": self.name,
                "sources": [],
                "tokens_used": 0
            }
        
        # Extract text from image
        extracted_text = self.extract_text(image_path)
        
        # Generate response based on extracted text
        prompt = f"Based on the following extracted text from an image:\n\n{extracted_text}\n\nUser query: {query}"
        response, tokens = self.llm_service.generate_response(prompt, context)
        
        return {
            "response": response,
            "agent": self.name,
            "extracted_text": extracted_text,
            "sources": [{"type": "ocr", "content": extracted_text}],
            "tokens_used": tokens
        }
