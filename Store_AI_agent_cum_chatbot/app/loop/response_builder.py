from app.core.state import PipelineState
from app.config.logging_config import logger

class ResponseBuilder:
    """Build final formatted response."""

    def build(self, state: PipelineState) -> PipelineState:
        """
        Format final response for display.

        Args:
            state: Pipeline state

        Returns:
            Updated state with final_response
        """
        if state.error:
            state.final_response = f"Error: {state.error}"
            return state

        # Build response text
        lines = []
        lines.append("=" * 60)
        lines.append("QUERY RESULT")
        lines.append("=" * 60)
        lines.append(f"\nQuery: {state.user_query}")
        lines.append(f"Summary: {state.query_result.get('query_summary', '')}")
        lines.append(f"\nMatching Products:")

        products = state.query_result.get('filtered_products', [])
        if products:
            for p in products:
                lines.append(
                    f"  • ID: {p.get('id')}, "
                    f"Price: ${p.get('price')}, "
                    f"Rating: {p.get('rating')}/5, "
                    f"Stock: {p.get('quantity')}"
                )
                lines.append(f"    Reason: {p.get('reason')}")
        else:
            lines.append("  No products matched your criteria.")

        lines.append(f"\nRecommendations: {state.query_result.get('recommendations', '')}")
        lines.append(f"Confidence: {state.confidence_score:.2%}")

        if state.needs_clarification:
            lines.append(f"\nWould you like to clarify: {state.clarification_question}")

        lines.append("\n" + "=" * 60)

        state.final_response = "\n".join(lines)
        logger.info("Response built successfully")
        return state
