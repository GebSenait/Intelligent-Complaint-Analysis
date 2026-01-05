"""
Vector Store Loader Module

Loads the pre-built FAISS index and associated metadata for RAG retrieval.
"""

import pickle
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize


class VectorStoreLoader:
    """Loads and manages the FAISS vector store and metadata."""

    def __init__(self, vector_store_dir: Optional[Path] = None):
        """
        Initialize the vector store loader.

        Args:
            vector_store_dir: Path to vector store directory. Defaults to project_root/vector_store
        """
        if vector_store_dir is None:
            # Determine project root
            current_path = Path(__file__).resolve()
            if current_path.parent.name == "src":
                project_root = current_path.parent.parent
            else:
                project_root = current_path
            vector_store_dir = project_root / "vector_store"

        self.vector_store_dir = Path(vector_store_dir)
        self.index: Optional[faiss.Index] = None
        self.chunks: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.embedding_model: Optional[SentenceTransformer] = None
        self.model_name: Optional[str] = None
        self.embedding_dimension: Optional[int] = None

    def load(self) -> bool:
        """
        Load the FAISS index and metadata from disk.

        Returns:
            True if loading was successful, False otherwise
        """
        try:
            # Check for required files first
            index_path = self.vector_store_dir / "complaint_embeddings.index"
            metadata_path = self.vector_store_dir / "chunk_metadata.pkl"

            missing_files = []
            if not index_path.exists():
                missing_files.append(str(index_path))
            if not metadata_path.exists():
                missing_files.append(str(metadata_path))

            if missing_files:
                print("\n" + "=" * 80)
                print("VECTOR STORE FILES NOT FOUND")
                print("=" * 80)
                print(f"\nMissing files:")
                for file in missing_files:
                    print(f"  [X] {file}")
                print(f"\nExpected location: {self.vector_store_dir}")
                print("\nTo create the vector store:")
                print(
                    "  1. Complete Task 2: Run notebooks/task-2-embeddings-vectorstore.ipynb"
                )
                print("  2. Ensure the notebook generates:")
                print("     - vector_store/complaint_embeddings.index")
                print("     - vector_store/chunk_metadata.pkl")
                print("     - vector_store/sampling_summary.json")
                print("=" * 80 + "\n")
                return False

            # Load FAISS index
            print(f"Loading FAISS index from {index_path}...")
            self.index = faiss.read_index(str(index_path))
            print(
                f"[OK] Loaded FAISS index: {self.index.ntotal:,} vectors, dimension {self.index.d}"
            )

            # Load metadata
            print(f"Loading metadata from {metadata_path}...")
            with open(metadata_path, "rb") as f:
                metadata_dict = pickle.load(f)

            self.chunks = metadata_dict.get("chunks", [])
            self.metadata = metadata_dict.get("metadata", [])
            self.model_name = metadata_dict.get(
                "model_name", "sentence-transformers/all-MiniLM-L6-v2"
            )
            self.embedding_dimension = metadata_dict.get("embedding_dimension", 384)

            print(f"[OK] Loaded {len(self.chunks):,} chunks with metadata")

            # Load embedding model
            print(f"Loading embedding model: {self.model_name}...")
            self.embedding_model = SentenceTransformer(self.model_name)
            print(
                f"[OK] Embedding model loaded (dimension: {self.embedding_model.get_sentence_embedding_dimension()})"
            )

            # Verify consistency
            if len(self.chunks) != self.index.ntotal:
                print(
                    f"Warning: Mismatch between chunks ({len(self.chunks)}) and index vectors ({self.index.ntotal})"
                )

            if self.embedding_model.get_sentence_embedding_dimension() != self.index.d:
                print(
                    f"Warning: Embedding dimension mismatch: model={self.embedding_model.get_sentence_embedding_dimension()}, index={self.index.d}"
                )

            return True

        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary information about the loaded vector store.

        Returns:
            Dictionary with summary statistics
        """
        summary_path = self.vector_store_dir / "sampling_summary.json"
        if summary_path.exists():
            with open(summary_path, "r") as f:
                return json.load(f)
        else:
            return {
                "total_chunks": len(self.chunks),
                "total_vectors": self.index.ntotal if self.index else 0,
                "embedding_model": self.model_name,
                "embedding_dimension": self.embedding_dimension,
            }

    def is_loaded(self) -> bool:
        """Check if vector store is loaded."""
        return self.index is not None and len(self.chunks) > 0
