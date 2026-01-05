"""
Prompt Template Module

Designs prompts that position the LLM as a CrediTrust financial analyst
and ensures evidence-backed responses.
"""

from typing import List, Dict, Any


class PromptTemplate:
    """Prompt template for CrediTrust financial analyst role."""

    SYSTEM_ROLE = """You are a senior financial analyst at CrediTrust Financial, a digital finance company operating in East Africa. Your role is to analyze customer complaints and provide concise, evidence-backed insights to Product, Support, and Compliance teams.

Your responses must:
1. Use ONLY the provided complaint evidence - never guess or make assumptions
2. Be concise and actionable
3. Cite specific complaint details when relevant
4. Clearly state when the provided context is insufficient to answer
5. Focus on business insights: trends, patterns, and actionable recommendations"""

    @staticmethod
    def format_context(chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks into context string.

        Args:
            chunks: List of retrieved chunk dictionaries with 'chunk' and 'metadata' keys

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, result in enumerate(chunks, 1):
            chunk = result["chunk"]
            metadata = result.get("metadata", {})
            similarity = result.get("similarity_score", 0.0)

            # Extract metadata fields
            complaint_id = metadata.get("complaint_id", "N/A")
            product = metadata.get("product_category", "Unknown")
            issue = metadata.get("issue", "N/A")
            date = metadata.get("date_received", "N/A")

            context_parts.append(
                f"[Complaint {i}]\n"
                f"Complaint ID: {complaint_id}\n"
                f"Product: {product}\n"
                f"Issue: {issue}\n"
                f"Date: {date}\n"
                f"Relevance Score: {similarity:.3f}\n"
                f"Narrative: {chunk}\n"
            )

        return "\n---\n".join(context_parts)

    @staticmethod
    def build_prompt(query: str, context: str) -> str:
        """
        Build the complete prompt for the LLM.

        Args:
            query: User's question
            context: Formatted context from retrieved chunks

        Returns:
            Complete prompt string
        """
        prompt = f"""{PromptTemplate.SYSTEM_ROLE}

## User Question:
{query}

## Relevant Complaint Evidence:
{context if context else "No relevant complaints found in the database."}

## Instructions:
Based on the complaint evidence above, provide a concise answer to the user's question. If the evidence is insufficient, clearly state that you cannot answer based on the available information.

## Your Analysis:"""

        return prompt

    @staticmethod
    def build_prompt_with_metadata(query: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Convenience method to build prompt directly from chunks.

        Args:
            query: User's question
            chunks: List of retrieved chunk dictionaries

        Returns:
            Complete prompt string
        """
        context = PromptTemplate.format_context(chunks)
        return PromptTemplate.build_prompt(query, context)
