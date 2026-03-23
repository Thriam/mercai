from typing import Optional
from app.core.state import PipelineState
from app.core.pipeline import Pipeline

class StoreAIOrchestrator:
    """Main orchestrator for the Store AI Agent pipeline."""

    def __init__(self):
        """Initialize the orchestrator with pipeline."""
        self.pipeline = Pipeline()

    def run(self, user_query: str) -> PipelineState:
        """
        Execute the full pipeline for a user query.

        Args:
            user_query: The user's question about products

        Returns:
            PipelineState with all results
        """
        return self.pipeline.run(user_query)
