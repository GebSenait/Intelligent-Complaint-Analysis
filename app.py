"""
Gradio Chat Interface for Intelligent Complaint Analysis Platform.

This module provides a user-friendly web interface for querying the RAG system
and retrieving complaint insights with full source transparency.

Task 4: Interactive Chat Interface
"""

import gradio as gr
from typing import Tuple, List, Dict, Any, Optional
import sys
import re
import warnings
import logging
from pathlib import Path

# Suppress harmless asyncio warnings on Windows
warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("asyncio").setLevel(logging.ERROR)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.rag_pipeline import RAGPipeline

# Global pipeline instance (loaded once at startup)
pipeline: RAGPipeline = None


def initialize_pipeline():
    """Initialize the RAG pipeline once at startup."""
    global pipeline
    if pipeline is None:
        try:
            print("[INFO] Initializing RAG Pipeline...")
            pipeline = RAGPipeline(top_k=5)
            print("[OK] RAG Pipeline ready")
        except Exception as e:
            print(f"[ERROR] Failed to initialize RAG Pipeline: {e}")
            raise
    return pipeline


def validate_question_scope(question: str) -> Tuple[bool, str]:
    """
    Validate that the question is relevant to complaint analysis.

    Args:
        question: User's question string

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if question is relevant, False otherwise
        - error_message: Empty string if valid, helpful message if invalid
    """
    question_lower = question.lower().strip()

    # If question is too short or empty, it's invalid
    if len(question_lower) < 5:
        return False, "Please ask a more detailed question about customer complaints."

    # Keywords related to complaint analysis, financial products, customer service
    relevant_keywords = [
        # Complaint-related
        "complaint",
        "complaints",
        "issue",
        "issues",
        "problem",
        "problems",
        "customer",
        "customers",
        "consumer",
        "report",
        "reported",
        "reporting",
        # Financial products
        "credit card",
        "credit cards",
        "personal loan",
        "personal loans",
        "loan",
        "savings account",
        "savings accounts",
        "money transfer",
        "money transfers",
        "account",
        "accounts",
        "billing",
        "bill",
        "fee",
        "fees",
        "charge",
        "charges",
        # Financial services terms
        "transaction",
        "transactions",
        "payment",
        "payments",
        "fraud",
        "fraudulent",
        "unauthorized",
        "dispute",
        "disputes",
        "refund",
        "refunds",
        "balance",
        "statement",
        "statements",
        "interest",
        "apr",
        "credit",
        "debit",
        # Service-related
        "service",
        "services",
        "support",
        "customer service",
        "help",
        "assistance",
        "delay",
        "delays",
        "timely",
        "response",
        "respond",
        "resolve",
        "resolution",
        "approval",
        "approve",
        "denied",
        "denial",
        "application",
        "apply",
        # Complaint types
        "billing",
        "collection",
        "credit reporting",
        "debt",
        "identity theft",
        "loan servicing",
        "mortgage",
        "prepaid card",
        "student loan",
        "vehicle loan",
        "other financial service",
        # Action/query words that indicate complaint analysis
        "what",
        "how",
        "why",
        "when",
        "where",
        "common",
        "frequent",
        "trend",
        "pattern",
        "describe",
        "explain",
        "tell",
        "show",
        "find",
        "search",
        "analyze",
        "analysis",
        "summary",
        "overview",
        "most",
        "least",
        "often",
    ]

    # Check if question contains any relevant keywords
    has_relevant_keyword = any(
        keyword in question_lower for keyword in relevant_keywords
    )

    # Common off-topic keywords that indicate the question is out of scope
    off_topic_indicators = [
        # Technical/AI terms (outside complaint context)
        "llm",
        "large language model",
        "machine learning",
        "deep learning",
        "neural network",
        "ai model",
        "gpt",
        "transformer",
        "embedding",
        "vector",
        "rag",
        "prompt engineering",
        "nlp",
        "natural language processing",
        # General knowledge questions
        "definition",
        "define",
        "what is",
        "what are",
        "explain what",
        "tell me about",
        "history of",
        "how does work",
        "how does it work",
        # Completely unrelated topics
        "python",
        "programming",
        "code",
        "algorithm",
        "software",
        "technology",
        "weather",
        "sports",
        "movie",
        "news",
        "recipe",
        "cooking",
    ]

    # Check for off-topic indicators (but be careful - some might be legitimate)
    has_off_topic = any(
        indicator in question_lower for indicator in off_topic_indicators
    )

    # If question has off-topic indicators but no relevant keywords, it's likely out of scope
    if has_off_topic and not has_relevant_keyword:
        return False, (
            "This question appears to be outside the scope of the CrediTrust Complaint Analysis System. "
            "Please ask questions about:\n\n"
            "• Customer complaints and issues\n"
            "• Financial products (Credit Cards, Loans, Savings Accounts, Money Transfers)\n"
            "• Billing, fees, transactions, fraud\n"
            "• Customer service experiences\n"
            "• Complaint patterns and trends\n\n"
            "Example: 'What are the most common issues with Credit Cards?'"
        )

    # If no relevant keywords found at all, suggest scope-appropriate questions
    if not has_relevant_keyword:
        return False, (
            "This question doesn't appear to be related to customer complaints. "
            "Please ask questions about CrediTrust Financial complaints, such as:\n\n"
            "• What issues are customers reporting with [product]?\n"
            "• Are there complaints about [specific issue]?\n"
            "• What are common [product] complaints?\n"
            "• How do customers describe [issue type]?\n\n"
            "See the example questions on the right for guidance."
        )

    return True, ""


def clean_complaint_text(text: str) -> str:
    """
    Clean and format complaint text for better readability.

    Args:
        text: Raw complaint text

    Returns:
        Cleaned and formatted text
    """
    if not text or text == "N/A":
        return "N/A"

    # Remove leading/trailing whitespace
    text = text.strip()

    # Remove leading periods and spaces (common in complaint data)
    text = re.sub(r"^\.+\s*", "", text)
    text = text.strip()

    # Fix spacing: ensure space after periods (but not for decimals)
    text = re.sub(r"\.([A-Z])", r". \1", text)

    # Fix spacing: ensure space after commas
    text = re.sub(r",([A-Za-z])", r", \1", text)

    # Fix common contractions: "didn t" -> "didn't", "can t" -> "can't", etc.
    text = re.sub(r"(\w)\s+([tTsS])\s", r"\1'\2 ", text)
    text = re.sub(r"(\w)\s+([tTsS])\.", r"\1'\2.", text)

    # Fix multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Fix multiple periods
    text = re.sub(r"\.{2,}", ".", text)

    # Capitalize first letter if needed
    if text and len(text) > 0 and text[0].islower():
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()

    # Ensure text ends with proper punctuation
    text = text.strip()
    if text and text[-1] not in ".!?":
        text = text + "."

    return text.strip()


def format_source_display(chunk: Dict[str, Any], rank: int) -> str:
    """
    Format a single retrieved chunk for display with metadata and relevance indicators.

    Args:
        chunk: Retrieved chunk dictionary with 'chunk', 'metadata', 'similarity_score'
        rank: Rank of this chunk (1-indexed)

    Returns:
        Formatted HTML/markdown string for display
    """
    metadata = chunk.get("metadata", {})
    complaint_id = metadata.get("complaint_id", "N/A")
    product = metadata.get("product_category", "Unknown")
    issue = metadata.get("issue", "N/A")
    date = metadata.get("date_received", "N/A")
    similarity = chunk.get("similarity_score", 0.0)

    # Clean the complaint text
    raw_text = chunk.get("chunk", "N/A")
    cleaned_text = clean_complaint_text(raw_text)

    # Determine relevance level and emoji
    if similarity >= 0.6:
        relevance_label = "🔵 High Relevance"
        relevance_desc = f"{similarity:.1%} similarity"
    elif similarity >= 0.45:
        relevance_label = "🟡 Moderate Relevance"
        relevance_desc = f"{similarity:.1%} similarity"
    else:
        relevance_label = "🟠 Lower Relevance"
        relevance_desc = f"{similarity:.1%} similarity"

    # Format as a card-like structure with enhanced relevance display
    source_text = f"""
### Source #{rank}: {relevance_label} ({relevance_desc})

**Complaint ID:** `{complaint_id}` | **Product:** `{product}` | **Issue:** `{issue}` | **Date:** `{date}`

**Complaint Text:**
> {cleaned_text}

---
"""
    return source_text


def extract_product_category(question: str) -> Optional[str]:
    """
    Extract product category from question if mentioned.

    Returns:
        Product category name if detected, None otherwise
    """
    question_lower = question.lower()

    product_mapping = {
        "savings account": "Savings Accounts",
        "savings accounts": "Savings Accounts",
        "savings": "Savings Accounts",
        "credit card": "Credit Cards",
        "credit cards": "Credit Cards",
        "personal loan": "Personal Loans",
        "personal loans": "Personal Loans",
        "loan": "Personal Loans",
        "money transfer": "Money Transfers",
        "money transfers": "Money Transfers",
        "transfer": "Money Transfers",
    }

    for keyword, category in product_mapping.items():
        if keyword in question_lower:
            return category

    return None


def query_rag(question: str, history: List[List[str]]) -> Tuple[str, str]:
    """
    Process a user question through the RAG pipeline with relevance filtering.

    Args:
        question: User's question
        history: Chat history (Gradio format: [[user_msg, bot_msg], ...])

    Returns:
        Tuple of (answer_text, sources_display)
    """
    global pipeline

    if not question or not question.strip():
        return "", "Please enter a question to query the complaint analysis system."

    # Validate question scope
    is_valid, validation_message = validate_question_scope(question)
    if not is_valid:
        return f"**⚠️ Out of Scope Question**\n\n{validation_message}", ""

    try:
        # Initialize pipeline if not already done
        if pipeline is None:
            pipeline = initialize_pipeline()

        # Extract product category if mentioned in question
        product_category = extract_product_category(question)

        # Query the RAG pipeline (with optional product filtering)
        if product_category:
            result = pipeline.query(question.strip(), product_category=product_category)
        else:
            result = pipeline.query(question.strip())

        # Extract answer and sources
        answer = result.get("answer", "No answer generated.")
        retrieved_chunks = result.get("retrieved_chunks", [])

        # Filter sources by relevance (similarity threshold)
        # Cosine similarity with normalized embeddings: range is approximately 0.2-1.0
        # Threshold: 0.35 means sources must have at least moderate relevance
        MIN_SIMILARITY_THRESHOLD = 0.35
        relevant_chunks = [
            chunk
            for chunk in retrieved_chunks
            if chunk.get("similarity_score", 0.0) >= MIN_SIMILARITY_THRESHOLD
        ]

        # Validate product category matching if product was mentioned
        if product_category:
            category_matched = [
                c
                for c in relevant_chunks
                if c.get("metadata", {}).get("product_category") == product_category
            ]
            category_mismatch_count = len(relevant_chunks) - len(category_matched)

            # If most results match the category, use only matching ones
            if len(category_matched) >= 2:
                relevant_chunks = category_matched
        else:
            category_mismatch_count = 0

        # If we filtered out chunks, provide a warning
        filtered_count = len(retrieved_chunks) - len(relevant_chunks)

        # Calculate average similarity for quality assessment
        if relevant_chunks:
            avg_similarity = sum(
                c.get("similarity_score", 0.0) for c in relevant_chunks
            ) / len(relevant_chunks)
        else:
            avg_similarity = 0.0

        # Format answer with relevance quality indicator
        answer_text = f"**Answer:**\n\n{answer}\n\n"

        # Add quality indicator based on average similarity
        if relevant_chunks:
            if avg_similarity >= 0.6:
                quality_indicator = "✅ **High Relevance** - Sources are highly relevant to your question"
            elif avg_similarity >= 0.45:
                quality_indicator = "⚠️ **Moderate Relevance** - Sources have moderate relevance to your question"
            else:
                quality_indicator = "⚠️ **Lower Relevance** - Consider refining your question for better results"

            answer_text += f"**Relevance Quality:** {quality_indicator}\n\n"

        # Format sources with relevance validation
        if relevant_chunks:
            sources_display = f"### Retrieved Complaint Sources ({len(relevant_chunks)} relevant source{'s' if len(relevant_chunks) != 1 else ''})\n\n"

            # Add quality and filtering information
            quality_notes = []

            if product_category:
                matching_count = sum(
                    1
                    for c in relevant_chunks
                    if c.get("metadata", {}).get("product_category") == product_category
                )
                if matching_count == len(relevant_chunks):
                    quality_notes.append(
                        f"✅ All sources match requested product category: **{product_category}**"
                    )
                elif matching_count > 0:
                    quality_notes.append(
                        f"⚠️ {matching_count}/{len(relevant_chunks)} sources match requested product category: **{product_category}**"
                    )

            if filtered_count > 0:
                quality_notes.append(
                    f"⚠️ {filtered_count} source{'s were' if filtered_count > 1 else ' was'} filtered out due to low relevance (< {MIN_SIMILARITY_THRESHOLD:.2f} similarity)"
                )

            if quality_notes:
                sources_display += "\n".join(quality_notes) + "\n\n"

            for idx, chunk in enumerate(relevant_chunks, 1):
                sources_display += format_source_display(chunk, idx)
        elif retrieved_chunks:
            # We had chunks but they all failed the relevance threshold
            sources_display = (
                f"⚠️ **No High-Relevance Sources Found**\n\n"
                f"Retrieved {len(retrieved_chunks)} source(s), but none met the minimum relevance threshold "
                f"(≥ {MIN_SIMILARITY_THRESHOLD:.2f} similarity).\n\n"
                f"**Suggestions:**\n"
                f"- Refine your question to be more specific about complaints\n"
                f"- Use product-specific terms (Credit Cards, Savings Accounts, etc.)\n"
                f"- Try rephrasing your question with complaint-related keywords\n\n"
                f"**Low-Relevance Sources (for reference):**\n\n"
            )
            for idx, chunk in enumerate(
                retrieved_chunks[:3], 1
            ):  # Show top 3 as reference
                sources_display += format_source_display(chunk, idx)
        else:
            sources_display = "No sources retrieved for this query."

        return answer_text, sources_display

    except Exception as e:
        error_msg = f"**Error:** {str(e)}\n\nPlease ensure the vector store is properly initialized (complete Task 2)."
        return error_msg, ""


def clear_conversation() -> Tuple[str, str, str]:
    """Clear the conversation history and reset inputs."""
    return "", "", ""


def build_interface():
    """Build and configure the Gradio interface."""

    with gr.Blocks(title="CrediTrust Complaint Analysis") as demo:

        # Header
        gr.Markdown(
            """
            # 🏦 CrediTrust Financial - Complaint Analysis System
            
            Ask questions about customer complaints and receive evidence-backed insights.
            Each answer includes source complaints with full traceability.
            """
        )

        # Main chat interface
        with gr.Row():
            with gr.Column(scale=2):
                # Question input
                question_input = gr.Textbox(
                    label="Enter your question",
                    placeholder="e.g., What are the most common issues with Credit Cards?",
                    lines=2,
                    value="",
                )

                # Buttons
                with gr.Row():
                    submit_btn = gr.Button("Ask Question", variant="primary", scale=2)
                    clear_btn = gr.Button("Clear", variant="secondary", scale=1)

            with gr.Column(scale=1):
                gr.Markdown(
                    """
                    ### 💡 Example Questions
                    - What issues are customers reporting with Savings Accounts?
                    - Are there complaints about money transfer delays?
                    - What are common fraud-related complaints?
                    - How do customers describe billing issues?
                    """
                )

        # Answer display
        answer_output = gr.Markdown(
            label="Answer", elem_classes=["answer-box"], value=""
        )

        # Sources display
        sources_output = gr.Markdown(
            label="Source Complaints", elem_classes=["source-box"], value=""
        )

        # Chat history (hidden, for future use)
        chat_history = gr.State(value=[])

        # Event handlers
        submit_btn.click(
            fn=query_rag,
            inputs=[question_input, chat_history],
            outputs=[answer_output, sources_output],
        )

        question_input.submit(
            fn=query_rag,
            inputs=[question_input, chat_history],
            outputs=[answer_output, sources_output],
        )

        clear_btn.click(
            fn=clear_conversation,
            inputs=[],
            outputs=[question_input, answer_output, sources_output],
        )

        # Footer
        gr.Markdown(
            """
            ---
            **System Status:** Ready | **Vector Store:** Loaded | **Model:** RAG Pipeline v1.0
            """
        )

    return demo


def main():
    """Main entry point for the Gradio application."""
    # Suppress harmless asyncio warnings on Windows
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    print("=" * 80)
    print("CREDITRUST FINANCIAL - COMPLAINT ANALYSIS SYSTEM")
    print("Task 4: Interactive Chat Interface")
    print("=" * 80)

    try:
        # Initialize pipeline at startup
        print("\n[INFO] Initializing RAG Pipeline...")
        initialize_pipeline()

        # Build and launch interface
        print("\n[INFO] Building Gradio interface...")
        demo = build_interface()

        print("\n[OK] Starting web interface...")
        print("[INFO] The interface will open in your browser")
        print("[INFO] Press Ctrl+C to stop the server\n")

        # Custom CSS for better styling
        css = """
        .gradio-container {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .answer-box {
            font-size: 16px;
            line-height: 1.6;
        }
        .source-box {
            font-size: 14px;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
        }
        """

        # Launch with CSS (title is set via page title in the header)
        # Try port 7860 first, but allow Gradio to find an available port if needed
        try:
            demo.launch(
                server_name="127.0.0.1",
                server_port=7860,
                share=False,
                show_error=True,
                css=css,
                inbrowser=True,  # Automatically open browser
            )
            url = "http://127.0.0.1:7860"
        except OSError as port_error:
            # If port 7860 is occupied, let Gradio find an available port
            if "port" in str(port_error).lower() or "7860" in str(port_error):
                print(f"[WARN] Port 7860 is occupied. Finding an available port...")
                demo.launch(
                    server_name="127.0.0.1",
                    server_port=None,  # Let Gradio find available port automatically
                    share=False,
                    show_error=True,
                    css=css,
                    inbrowser=True,  # Automatically open browser
                )
                url = "http://127.0.0.1:7861 (or check terminal for actual port)"
            else:
                raise

        # Display URL clearly in case browser doesn't open automatically
        print("\n" + "=" * 80)
        print("GRADIO INTERFACE IS RUNNING")
        print("=" * 80)
        print("If your browser didn't open automatically, copy and paste this URL:")
        print(f"\n👉 {url}")
        print(
            "\n(Note: If port 7860 was occupied, check the Gradio output above for the actual port)"
        )
        print("\n" + "=" * 80 + "\n")

    except KeyboardInterrupt:
        print("\n[INFO] Shutting down gracefully...")
    except (ConnectionResetError, OSError) as conn_error:
        # Suppress harmless connection errors on Windows
        if "10054" in str(conn_error) or "connection" in str(conn_error).lower():
            print(
                "\n[INFO] Server connection closed (this is normal when stopping the server)"
            )
        else:
            print(f"\n[WARN] Connection warning (non-critical): {conn_error}")
    except Exception as e:
        print(f"\n[ERROR] Failed to start application: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
