from app.core.state import PipelineState
from app.llm.llm_client import LLMClient
from app.llm.prompt_templates import build_product_query_prompt
from app.query_engine.confidence_scorer import ConfidenceScorer
from app.config.logging_config import logger

class ProductQueryEngine:
    """Engine for processing product queries with LLM."""

    def __init__(self):
        """Initialize query engine."""
        self.llm_client = LLMClient()
        self.confidence_scorer = ConfidenceScorer()

    def query(self, state: PipelineState) -> PipelineState:
        """
        Process query with LLM and retrieved products.

        Args:
            state: Pipeline state with retrieved_products set

        Returns:
            Updated state with query_result and confidence_score
        """
        if not state.retrieved_products:
            logger.warning("No products retrieved for query")
            state.query_result = {
                'query_summary': state.user_query,
                'filtered_products': [],
                'recommendations': 'No products found matching your criteria.',
                'confidence': 0.0
            }
            state.confidence_score = 0.0
            return state

        try:
            # Build prompt
            prompt = build_product_query_prompt(
                state.normalized_query,
                state.retrieved_products
            )

            # Generate LLM response
            response = self.llm_client.generate(prompt)

            # Parse JSON response
            state.query_result = self.llm_client.parse_json_response(response)

            # Score confidence
            state.confidence_score = self.confidence_scorer.score(
                state.retrieved_products,
                state.query_result
            )

            logger.info(f"Query engine completed. Confidence: {state.confidence_score:.2f}")

        except Exception as e:
            logger.error(f"Query engine error: {str(e)}")
            state.error = str(e)
            state.query_result = {
                'query_summary': state.user_query,
                'filtered_products': [],
                'recommendations': 'An error occurred processing your query.',
                'confidence': 0.0
            }
            state.confidence_score = 0.0

        return state
