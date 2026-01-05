"""
Run RAG Pipeline Evaluation

Script to execute qualitative evaluation of the RAG pipeline.
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_pipeline import RAGPipeline
from src.evaluation import RAGEvaluator


def main():
    """Run the evaluation."""
    print("=" * 80)
    print("RAG PIPELINE EVALUATION SCRIPT")
    print("=" * 80)
    print()

    # Check for vector store before attempting to initialize
    vector_store_dir = Path(__file__).parent.parent / "vector_store"
    index_path = vector_store_dir / "complaint_embeddings.index"
    metadata_path = vector_store_dir / "chunk_metadata.pkl"

    if not index_path.exists() or not metadata_path.exists():
        print("[WARNING] Vector store not found. Cannot run evaluation.")
        print("\n" + "=" * 80)
        print("PREREQUISITE: Task 2 Must Be Completed First")
        print("=" * 80)
        print("\nThe evaluation script requires the vector store from Task 2.")
        print("\nTo proceed:")
        print("  1. Open and run: notebooks/task-2-embeddings-vectorstore.ipynb")
        print("  2. Ensure all cells complete successfully")
        print("  3. Verify these files exist:")
        print(f"     - {index_path}")
        print(f"     - {metadata_path}")
        print("\nAfter Task 2 is complete, run this evaluation script again.")
        print("=" * 80 + "\n")
        return 1

    # Initialize RAG pipeline
    print("Initializing RAG pipeline...")
    try:
        pipeline = RAGPipeline(
            top_k=5, generator_model="gpt2"  # Can be changed to better models
        )
        print("[OK] RAG pipeline initialized\n")
    except RuntimeError as e:
        print(f"\n[ERROR] Error initializing pipeline: {e}")
        print("\nThis usually means the vector store files are missing or corrupted.")
        print(
            "Please complete Task 2 first (notebooks/task-2-embeddings-vectorstore.ipynb)"
        )
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback

        print("\nFull traceback:")
        traceback.print_exc()
        return 1

    # Run evaluation
    evaluator = RAGEvaluator(pipeline)
    results = evaluator.evaluate_all()

    # Generate outputs
    output_dir = Path(__file__).parent.parent / "docs"
    output_dir.mkdir(exist_ok=True)

    # Save markdown table
    md_path = output_dir / "task-3-evaluation-results.md"
    evaluator.generate_markdown_table(md_path)

    # Save JSON results
    json_path = output_dir / "task-3-evaluation-results.json"
    evaluator.save_results_json(json_path)

    print(f"\n[OK] Evaluation complete!")
    print(f"  - Markdown table: {md_path}")
    print(f"  - JSON results: {json_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
