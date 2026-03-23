from app.core.state import PipelineState
from app.query.query_handler import QueryHandler
from app.retrieval.retriever import Retriever
from app.query_engine.product_query_engine import ProductQueryEngine
from app.loop.clarification_engine import ClarificationEngine
from app.loop.response_builder import ResponseBuilder
from app.config.logging_config import logger

class Pipeline:
    """Orchestrates the full query processing pipeline."""

    def __init__(self):
        """Initialize all pipeline components."""
        self.query_handler = QueryHandler()
        self.retriever = Retriever()
        self.query_engine = ProductQueryEngine()
        self.clarification_engine = ClarificationEngine()
        self.response_builder = ResponseBuilder()

    def run(self, user_query: str) -> PipelineState:
        """
        Execute the complete pipeline.

        Args:
            user_query: User's natural language query

        Returns:
            PipelineState with final response and results
        """
        state = PipelineState(user_query=user_query)

        try:
            logger.info(f"Processing query: {user_query}")

            # Step 1: Query normalization and intent detection
            state = self.query_handler.process(state)

            # Step 2: Retrieve relevant products
            state = self.retriever.retrieve(state)

            # Step 3: Query engine (LLM synthesis)
            state = self.query_engine.query(state)

            # Step 4: Clarification check
            state = self.clarification_engine.evaluate(state)

            # Step 5: Response formatting
            state = self.response_builder.build(state)

            logger.info(f"Query processed successfully. Confidence: {state.confidence_score}")

        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            state.error = str(e)

        return state
