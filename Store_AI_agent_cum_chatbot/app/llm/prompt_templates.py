from typing import Dict, List, Any

def build_product_query_prompt(query: str, products: List[Dict[str, Any]]) -> str:
    """
    Build prompt for product query processing.

    Args:
        query: User's natural language query
        products: Retrieved products with metadata

    Returns:
        Formatted prompt for LLM
    """
    products_str = "\n".join([
        f"- ID: {p.get('product_id')}, Price: ${p['metadata'].get('price')}, "
        f"Quantity: {p['metadata'].get('quantity')}, Rating: {p['metadata'].get('rating')}/5"
        for p in products
    ])

    prompt = f"""You are a helpful store assistant. Analyze the user's query and the retrieved products.

User Query: {query}

Retrieved Products:
{products_str}

Analyze these products and create a JSON response with:
1. query_summary: Brief summary of what the user is looking for
2. filtered_products: Array of products that match the user's criteria, with reason for each
3. recommendations: Helpful suggestions or clarifications
4. confidence: Your confidence level (0-1) that you understood and answered correctly

Respond ONLY with valid JSON, no additional text.

JSON Schema:
{{
  "query_summary": "string",
  "filtered_products": [
    {{"id": "string", "price": number, "quantity": number, "rating": number, "reason": "string"}}
  ],
  "recommendations": "string",
  "confidence": number
}}"""

    return prompt


def build_clarification_prompt(query: str, confidence: float) -> str:
    """
    Build prompt to determine if clarification is needed.

    Args:
        query: User's query
        confidence: Current confidence score

    Returns:
        Clarification evaluation prompt
    """
    return f"""Based on this query and your low confidence ({confidence:.2f}), should you ask for clarification?

Query: {query}

Respond with JSON:
{{
  "needs_clarification": boolean,
  "question": "string or null"
}}"""
