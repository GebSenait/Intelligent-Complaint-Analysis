"""
Evaluation Module

Qualitative evaluation of RAG pipeline with business questions.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from .rag_pipeline import RAGPipeline


class RAGEvaluator:
    """Evaluates RAG pipeline with qualitative business questions."""
    
    # Representative business questions for evaluation
    EVALUATION_QUESTIONS = [
        {
            "question": "What are the most common issues reported for Credit Cards?",
            "category": "Product Analysis",
            "expected_focus": "Credit card issues, fraud, billing, etc."
        },
        {
            "question": "Are there complaints about delayed money transfers?",
            "category": "Operational",
            "expected_focus": "Money transfer delays, processing times"
        },
        {
            "question": "What problems do customers face with Personal Loans?",
            "category": "Product Analysis",
            "expected_focus": "Loan application, repayment, interest rates"
        },
        {
            "question": "How many complaints mention fraud or unauthorized transactions?",
            "category": "Security & Compliance",
            "expected_focus": "Fraud, unauthorized access, security breaches"
        },
        {
            "question": "What issues are customers reporting with Savings Accounts?",
            "category": "Product Analysis",
            "expected_focus": "Account access, fees, interest rates"
        },
        {
            "question": "Are there complaints about poor customer service?",
            "category": "Service Quality",
            "expected_focus": "Customer service, response times, support quality"
        },
        {
            "question": "What billing or fee-related complaints exist?",
            "category": "Financial",
            "expected_focus": "Unexpected fees, billing errors, charges"
        },
        {
            "question": "Do customers report issues with account access or login problems?",
            "category": "Technical",
            "expected_focus": "Account access, login, technical issues"
        },
        {
            "question": "What are the main concerns about Money Transfer services?",
            "category": "Product Analysis",
            "expected_focus": "Money transfer issues, delays, fees"
        },
        {
            "question": "Are there complaints about loan approval or rejection processes?",
            "category": "Process",
            "expected_focus": "Loan approval, application process, rejection reasons"
        }
    ]
    
    def __init__(self, rag_pipeline: RAGPipeline):
        """
        Initialize evaluator.
        
        Args:
            rag_pipeline: Initialized RAGPipeline instance
        """
        self.rag_pipeline = rag_pipeline
        self.results: List[Dict[str, Any]] = []
    
    def evaluate_all(self) -> List[Dict[str, Any]]:
        """
        Run evaluation on all questions.
        
        Returns:
            List of evaluation results
        """
        print("=" * 80)
        print("RAG PIPELINE QUALITATIVE EVALUATION")
        print("=" * 80)
        print(f"\nEvaluating {len(self.EVALUATION_QUESTIONS)} business questions...\n")
        
        self.results = []
        
        for i, q_info in enumerate(self.EVALUATION_QUESTIONS, 1):
            question = q_info["question"]
            category = q_info["category"]
            
            print(f"[{i}/{len(self.EVALUATION_QUESTIONS)}] Processing: {question}")
            
            # Run RAG pipeline
            result = self.rag_pipeline.query(question)
            
            # Evaluate quality (manual scoring guide)
            # This would ideally be done by human evaluators
            # For now, we provide a framework
            
            evaluation_result = {
                "question": question,
                "category": category,
                "generated_answer": result["answer"],
                "retrieved_sources": [
                    {
                        "rank": chunk["rank"],
                        "chunk_preview": chunk["chunk"][:200] + "..." if len(chunk["chunk"]) > 200 else chunk["chunk"],
                        "metadata": chunk["metadata"],
                        "similarity_score": chunk["similarity_score"]
                    }
                    for chunk in result["retrieved_chunks"]
                ],
                "num_retrieved": len(result["retrieved_chunks"]),
                "quality_score": None,  # To be filled manually or by evaluator
                "analysis": None,  # To be filled manually
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(evaluation_result)
            print(f"  [OK] Retrieved {len(result['retrieved_chunks'])} chunks")
            print(f"  [OK] Generated answer ({len(result['answer'])} chars)\n")
        
        print("=" * 80)
        print("EVALUATION COMPLETE")
        print("=" * 80)
        
        return self.results
    
    def generate_markdown_table(self, output_path: Optional[Path] = None) -> str:
        """
        Generate Markdown evaluation table.
        
        Args:
            output_path: Optional path to save the table
        
        Returns:
            Markdown table as string
        """
        if not self.results:
            self.evaluate_all()
        
        # Build markdown table
        md_lines = [
            "# RAG Pipeline Evaluation Results",
            "",
            f"**Evaluation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Questions**: {len(self.results)}",
            "",
            "## Evaluation Table",
            "",
            "| # | Question | Generated Answer | Retrieved Sources | Quality Score | Analysis / Comments |",
            "|---|----------|------------------|-------------------|---------------|---------------------|"
        ]
        
        for i, result in enumerate(self.results, 1):
            question = result["question"]
            answer = result["generated_answer"][:300] + "..." if len(result["generated_answer"]) > 300 else result["generated_answer"]
            
            # Format sources
            sources_list = []
            for src in result["retrieved_sources"][:3]:  # Show top 3
                src_text = f"Rank {src['rank']}: {src['chunk_preview']}"
                sources_list.append(src_text)
            sources = "<br>".join(sources_list)
            if len(result["retrieved_sources"]) > 3:
                sources += f"<br>... and {len(result['retrieved_sources']) - 3} more"
            
            quality_score = result.get("quality_score", "TBD")
            analysis = result.get("analysis", "Pending evaluation") or "Pending evaluation"
            
            # Escape pipe characters in content
            question = question.replace("|", "\\|")
            answer = answer.replace("|", "\\|").replace("\n", " ")
            sources = sources.replace("|", "\\|")
            analysis = str(analysis).replace("|", "\\|")
            
            md_lines.append(
                f"| {i} | {question} | {answer} | {sources} | {quality_score} | {analysis} |"
            )
        
        md_content = "\n".join(md_lines)
        
        # Add detailed section
        md_content += "\n\n## Detailed Results\n\n"
        
        for i, result in enumerate(self.results, 1):
            md_content += f"### Question {i}: {result['question']}\n\n"
            md_content += f"**Category**: {result['category']}\n\n"
            md_content += f"**Generated Answer**:\n\n{result['generated_answer']}\n\n"
            md_content += f"**Retrieved Sources** ({result['num_retrieved']} total):\n\n"
            
            for src in result["retrieved_sources"]:
                md_content += f"- **Rank {src['rank']}** (Similarity: {src['similarity_score']:.3f})\n"
                md_content += f"  - Complaint ID: {src['metadata'].get('complaint_id', 'N/A')}\n"
                md_content += f"  - Product: {src['metadata'].get('product_category', 'N/A')}\n"
                md_content += f"  - Issue: {src['metadata'].get('issue', 'N/A')}\n"
                md_content += f"  - Preview: {src['chunk_preview']}\n\n"
            
            md_content += f"**Quality Score**: {result.get('quality_score', 'TBD')}\n\n"
            md_content += f"**Analysis**: {result.get('analysis', 'Pending evaluation')}\n\n"
            md_content += "---\n\n"
        
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"[OK] Evaluation table saved to {output_path}")
        
        return md_content
    
    def save_results_json(self, output_path: Path):
        """Save evaluation results as JSON."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Evaluation results saved to {output_path}")

