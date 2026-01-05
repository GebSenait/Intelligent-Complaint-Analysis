"""
Update Markdown Evaluation File from JSON

Regenerates the markdown evaluation table from the updated JSON file
with quality scores and analysis.
"""

import json
from pathlib import Path
from datetime import datetime


def generate_markdown_from_json(json_path: Path, output_path: Path):
    """Generate markdown table from JSON evaluation results."""
    with open(json_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Build markdown table
    md_lines = [
        "# RAG Pipeline Evaluation Results",
        "",
        f"**Evaluation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Questions**: {len(results)}",
        "",
        "## Evaluation Table",
        "",
        "| # | Question | Generated Answer | Retrieved Sources | Quality Score | Analysis / Comments |",
        "|---|----------|------------------|-------------------|---------------|---------------------|"
    ]
    
    for i, result in enumerate(results, 1):
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
    
    for i, result in enumerate(results, 1):
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
        
        quality_score = result.get('quality_score', 'TBD')
        analysis = result.get('analysis', 'Pending evaluation') or 'Pending evaluation'
        
        md_content += f"**Quality Score**: {quality_score}\n\n"
        md_content += f"**Analysis**: {analysis}\n\n"
        md_content += "---\n\n"
    
    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"[OK] Updated markdown file: {output_path}")


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    json_path = project_root / "docs" / "task-3-evaluation-results.json"
    md_path = project_root / "docs" / "task-3-evaluation-results.md"
    
    generate_markdown_from_json(json_path, md_path)

