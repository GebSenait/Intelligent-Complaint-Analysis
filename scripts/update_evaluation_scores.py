"""
Update Evaluation Results with Quality Scores and Analysis

This script updates the evaluation JSON and markdown files with manually
reviewed quality scores and analysis.
"""

import json
from pathlib import Path

# Quality scores and analysis based on review
evaluation_updates = [
    {
        "question": "What are the most common issues reported for Credit Cards?",
        "quality_score": 2,
        "analysis": "Retrieval: Excellent (4/5) - Found relevant credit card issues. Generation: Poor (1/5) - Answer is incoherent, doesn't summarize common issues. GPT-2 fails to synthesize retrieved context."
    },
    {
        "question": "Are there complaints about delayed money transfers?",
        "quality_score": 2,
        "analysis": "Retrieval: Excellent (5/5) - Found relevant money transfer delay complaints. Generation: Poor (1/5) - Mentions bitcoin/real estate (irrelevant). GPT-2 cannot follow instructions to use context."
    },
    {
        "question": "What problems do customers face with Personal Loans?",
        "quality_score": 2,
        "analysis": "Retrieval: Good (4/5) - Found loan-related complaints. Generation: Poor (1/5) - Incoherent answer, doesn't extract problems. Needs instruction-tuned model to synthesize patterns."
    },
    {
        "question": "How many complaints mention fraud or unauthorized transactions?",
        "quality_score": 2,
        "analysis": "Retrieval: Excellent (5/5) - Found fraud-related complaints. Generation: Poor (1/5) - Doesn't answer quantitative question. Should state exact counts require DB queries, but can provide qualitative insights."
    },
    {
        "question": "What issues are customers reporting with Savings Accounts?",
        "quality_score": 2,
        "analysis": "Retrieval: Good (4/5) - Found relevant account issues. Generation: Poor (1/5) - Long but incoherent, doesn't extract specific issues. GPT-2 fails to organize information."
    },
    {
        "question": "Are there complaints about poor customer service?",
        "quality_score": 3,
        "analysis": "Retrieval: Excellent (5/5) - Perfect matches for customer service complaints. Generation: Marginal (2/5) - Mentions customer service but doesn't clearly answer yes/no with examples. Slightly better than others."
    },
    {
        "question": "What billing or fee-related complaints exist?",
        "quality_score": 2,
        "analysis": "Retrieval: Excellent (5/5) - Found specific fee complaints. Generation: Poor (1/5) - Very short, irrelevant answer. Complete failure to use context."
    },
    {
        "question": "Do customers report issues with account access or login problems?",
        "quality_score": 2,
        "analysis": "Retrieval: Good (4/5) - Found account access/login complaints. Generation: Poor (1/5) - Mentions IT/HR (irrelevant), doesn't confirm issues from context. GPT-2 cannot recognize patterns."
    },
    {
        "question": "What are the main concerns about Money Transfer services?",
        "quality_score": 2,
        "analysis": "Retrieval: Good (4/5) - Found money transfer complaints. Generation: Poor (1/5) - Incoherent, doesn't extract concerns. Needs instruction-tuned model to synthesize themes."
    },
    {
        "question": "Are there complaints about loan approval or rejection processes?",
        "quality_score": 3,
        "analysis": "Retrieval: Excellent (5/5) - Found relevant loan process complaints. Generation: Marginal (2/5) - Mentions loan context but incoherent. Slightly better but still poor."
    }
]


def update_json_file(json_path: Path):
    """Update JSON file with quality scores and analysis."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create lookup dictionary
    updates_lookup = {item['question']: item for item in evaluation_updates}
    
    # Update each result
    for result in data:
        question = result['question']
        if question in updates_lookup:
            update = updates_lookup[question]
            result['quality_score'] = update['quality_score']
            result['analysis'] = update['analysis']
    
    # Save updated file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Updated {json_path} with quality scores and analysis")


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    json_path = project_root / "docs" / "task-3-evaluation-results.json"
    
    update_json_file(json_path)
    print("\nNote: Markdown file will be regenerated when evaluation is re-run")
    print("Or manually update docs/task-3-evaluation-results.md with the scores")

