"""
Retriever Module

Implements semantic retrieval of complaint chunks using the vector store.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.preprocessing import normalize
from sentence_transformers import SentenceTransformer

from .vector_store_loader import VectorStoreLoader


class Retriever:
    """Retrieves semantically relevant complaint chunks for user queries."""
    
    def __init__(self, vector_store_loader: VectorStoreLoader, top_k: int = 5):
        """
        Initialize the retriever.
        
        Args:
            vector_store_loader: Loaded VectorStoreLoader instance
            top_k: Number of top chunks to retrieve (default: 5)
        """
        if not vector_store_loader.is_loaded():
            raise ValueError("Vector store must be loaded before initializing Retriever")
        
        self.vector_store = vector_store_loader
        self.index = vector_store_loader.index
        self.chunks = vector_store_loader.chunks
        self.metadata = vector_store_loader.metadata
        self.embedding_model = vector_store_loader.embedding_model
        self.top_k = top_k
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve top-k most relevant chunks for a query.
        
        Args:
            query: User question/query string
            top_k: Number of chunks to retrieve (overrides default if provided)
        
        Returns:
            List of dictionaries containing:
                - chunk: The text chunk
                - metadata: Associated metadata (complaint_id, product_category, etc.)
                - similarity_score: Cosine similarity score
                - rank: Rank (1-indexed)
        """
        if top_k is None:
            top_k = self.top_k
        
        # Embed the query
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        
        # Normalize for cosine similarity (FAISS IndexFlatIP with normalized vectors)
        query_embedding_normalized = normalize(query_embedding, norm='l2', axis=1).astype('float32')
        
        # Search the index
        distances, indices = self.index.search(query_embedding_normalized, top_k)
        
        # Build results
        results = []
        for rank, (distance, idx) in enumerate(zip(distances[0], indices[0]), 1):
            if idx < len(self.chunks) and idx < len(self.metadata):
                results.append({
                    'chunk': self.chunks[idx],
                    'metadata': self.metadata[idx],
                    'similarity_score': float(distance),
                    'rank': rank
                })
        
        return results
    
    def retrieve_with_filter(
        self, 
        query: str, 
        product_category: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chunks with optional product category filter.
        
        Args:
            query: User question/query string
            product_category: Filter by product category (Credit Cards, Personal Loans, etc.)
            top_k: Number of chunks to retrieve (overrides default if provided)
        
        Returns:
            List of retrieved chunks (same format as retrieve())
        """
        # Retrieve more candidates if filtering
        retrieve_k = (top_k or self.top_k) * 3 if product_category else (top_k or self.top_k)
        
        # Embed and search
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        query_embedding_normalized = normalize(query_embedding, norm='l2', axis=1).astype('float32')
        distances, indices = self.index.search(query_embedding_normalized, retrieve_k)
        
        # Filter by product category if specified
        results = []
        for rank, (distance, idx) in enumerate(zip(distances[0], indices[0]), 1):
            if idx < len(self.chunks) and idx < len(self.metadata):
                metadata = self.metadata[idx]
                
                # Apply filter
                if product_category and metadata.get('product_category') != product_category:
                    continue
                
                results.append({
                    'chunk': self.chunks[idx],
                    'metadata': metadata,
                    'similarity_score': float(distance),
                    'rank': rank
                })
                
                # Stop when we have enough results
                if len(results) >= (top_k or self.top_k):
                    break
        
        return results

