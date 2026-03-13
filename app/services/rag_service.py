from typing import List, Dict
from rank_bm25 import BM25Okapi
from services.embedding_service import EmbeddingService
from models.schemas import RetrievalResult

# Singleton instance
_rag_service_instance = None

class RAGService:
    def __new__(cls):
        global _rag_service_instance
        if _rag_service_instance is None:
            _rag_service_instance = super().__new__(cls)
            _rag_service_instance._initialized = False
        return _rag_service_instance
    
    def __init__(self):
        if self._initialized:
            return
        self.embedding_service = EmbeddingService()
        self.bm25 = None
        self.documents = self.embedding_service.documents
        self._initialized = True
    
    def query_rewrite(self, query: str) -> List[str]:
        """Expand query for better retrieval"""
        expanded = [query, query.lower(), query.replace("?", "")]
        return expanded
    
    def dense_search(self, query: str, k: int = 5) -> List[RetrievalResult]:
        """Vector search using FAISS"""
        results = self.embedding_service.search(query, k)
        return [
            RetrievalResult(
                content=doc,
                score=1.0 / (1.0 + score),
                source="vector_db",
                metadata={"type": "dense"}
            )
            for doc, score in results
        ]
    
    def sparse_search(self, query: str, k: int = 5) -> List[RetrievalResult]:
        """Keyword search using BM25"""
        if not self.bm25:
            return []
        
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = scores.argsort()[-k:][::-1]
        
        return [
            RetrievalResult(
                content=self.documents[idx],
                score=float(scores[idx]),
                source="bm25",
                metadata={"type": "sparse"}
            )
            for idx in top_indices
        ]
    
    def hybrid_search(self, query: str, k: int = 5) -> List[RetrievalResult]:
        """Combine dense and sparse search"""
        dense_results = self.dense_search(query, k)
        sparse_results = self.sparse_search(query, k)
        
        combined = dense_results + sparse_results
        combined.sort(key=lambda x: x.score, reverse=True)
        return combined[:k]
    
    def add_documents(self, documents: List[str]):
        """Add documents to both vector and BM25 index"""
        self.documents.extend(documents)
        self.embedding_service.add_documents(documents)
        tokenized_docs = [doc.lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        print(f"RAG Service now has {len(self.documents)} documents")
    
    def retrieve_context(self, query: str, k: int = 3) -> str:
        """Retrieve and format context for LLM with token limit"""
        results = self.hybrid_search(query, k)
        context_parts = []
        total_chars = 0
        max_chars = 2000  # Limit context to ~500 tokens
        
        for i, r in enumerate(results):
            part = f"[Source {i+1}]: {r.content[:500]}"  # Truncate each source
            if total_chars + len(part) > max_chars:
                break
            context_parts.append(part)
            total_chars += len(part)
        
        return "\n\n".join(context_parts) if context_parts else "No relevant documents found."
