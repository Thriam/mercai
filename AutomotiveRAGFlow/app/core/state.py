from dataclasses import dataclass, field
from typing import Any


@dataclass
class PipelineState:
    user_query: str
    rewritten_query: str = ""
    query_payload: dict[str, Any] = field(default_factory=dict)
    retrieved_docs: list[dict[str, Any]] = field(default_factory=list)
    diagnosis_result: dict[str, Any] = field(default_factory=dict)
    final_response: str = ""
    needs_clarification: bool = False
    clarification_question: str = ""