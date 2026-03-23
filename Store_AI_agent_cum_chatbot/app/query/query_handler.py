from app.core.state import PipelineState
from app.query.intent_detector import IntentDetector
from app.query.query_rewriter import QueryRewriter
from app.config.logging_config import logger

class QueryHandler:
    """Handle query preprocessing and normalization."""

    def __init__(self):
        """Initialize query handler."""
        self.intent_detector = IntentDetector()
        self.query_rewriter = QueryRewriter()

    def process(self, state: PipelineState) -> PipelineState:
        """
        Process and normalize user query.

        Args:
            state: Pipeline state

        Returns:
            Updated state with normalized_query and intent
        """
        # Rewrite query
        state.normalized_query = self.query_rewriter.rewrite(state.user_query)

        # Detect intent
        state.intent = self.intent_detector.detect(state.user_query)

        logger.info(f"Query processed. Intent: {state.intent}")
        return state
