"""
RAG Pipeline Module

Orchestrates the complete RAG pipeline: retrieval + generation.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from .vector_store_loader import VectorStoreLoader
from .retriever import Retriever
from .prompt_template import PromptTemplate
from .generator import Generator


class RAGPipeline:
    """Complete RAG pipeline orchestrator."""

    def __init__(
        self,
        vector_store_dir: Optional[Path] = None,
        top_k: int = 5,
        generator_model: str = "gpt2",
    ):
        """
        Initialize the RAG pipeline.

        Args:
            vector_store_dir: Path to vector store directory
            top_k: Number of chunks to retrieve
            generator_model: LLM model name for generation
        """
        # Load vector store
        self.vector_store_loader = VectorStoreLoader(vector_store_dir)
        if not self.vector_store_loader.load():
            raise RuntimeError(
                "Failed to load vector store. Ensure Task 2 has been completed."
            )

        # Initialize components
        self.retriever = Retriever(self.vector_store_loader, top_k=top_k)
        self.generator = Generator(model_name=generator_model)
        self.prompt_template = PromptTemplate()

        print("[OK] RAG Pipeline initialized successfully")

    def query(
        self,
        question: str,
        product_category: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Process a user question through the RAG pipeline.

        Args:
            question: User's question
            product_category: Optional product category filter
            top_k: Optional override for number of chunks to retrieve

        Returns:
            Dictionary containing:
                - answer: Generated answer
                - retrieved_chunks: List of retrieved chunks with metadata
                - prompt: Full prompt used for generation
        """
        # Step 1: Retrieve relevant chunks
        if product_category:
            retrieved_chunks = self.retriever.retrieve_with_filter(
                question, product_category=product_category, top_k=top_k
            )
        else:
            retrieved_chunks = self.retriever.retrieve(question, top_k=top_k)

        # Step 2: Build prompt
        prompt = self.prompt_template.build_prompt_with_metadata(
            question, retrieved_chunks
        )

        # Step 3: Generate answer
        answer = self.generator.generate(prompt)

        return {
            "answer": answer,
            "retrieved_chunks": retrieved_chunks,
            "prompt": prompt,
            "question": question,
        }

    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get information about the pipeline configuration."""
        summary = self.vector_store_loader.get_summary()
        return {
            "vector_store": summary,
            "retriever_top_k": self.retriever.top_k,
            "generator_model": self.generator.model_name,
            "total_chunks": len(self.vector_store_loader.chunks),
        }
