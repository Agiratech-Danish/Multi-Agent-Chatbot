from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import os
from typing import List, Tuple
from core.config import get_settings
from pathlib import Path

settings = get_settings()

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model)
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.vector_path = Path(settings.vector_db_path)
        self.vector_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.vector_path / "faiss_index.bin"
        self.docs_file = self.vector_path / "documents.json"
        self._load_if_exists()
    
    def _load_if_exists(self):
        """Load existing index and documents"""
        if self.index_file.exists() and self.docs_file.exists():
            self.index = faiss.read_index(str(self.index_file))
            with open(self.docs_file, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
    
    def _save(self):
        """Save index and documents to disk"""
        faiss.write_index(self.index, str(self.index_file))
        with open(self.docs_file, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
    
    def create_embedding(self, text: str) -> np.ndarray:
        """Create embedding for text"""
        return self.model.encode([text])[0]
    
    def add_documents(self, texts: List[str]):
        """Add documents to vector store"""
        embeddings = self.model.encode(texts)
        self.index.add(embeddings.astype('float32'))
        self.documents.extend(texts)
        self._save()  # Save after adding
        print(f"✅ Saved {len(texts)} documents to {self.vector_path}")
    
    def search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """Search similar documents"""
        if len(self.documents) == 0:
            return []
        query_embedding = self.create_embedding(query)
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'), k
        )
        results = [(self.documents[idx], float(dist)) 
                   for idx, dist in zip(indices[0], distances[0]) 
                   if idx < len(self.documents)]
        return results
