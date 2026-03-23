from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class PipelineState:
    """Tracks execution state through the pipeline."""
    user_query: str
    normalized_query: Optional[str] = None
    intent: Optional[str] = None
    retrieved_products: List[Dict[str, Any]] = field(default_factory=list)
    query_result: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.0
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    final_response: Optional[str] = None
    error: Optional[str] = None
