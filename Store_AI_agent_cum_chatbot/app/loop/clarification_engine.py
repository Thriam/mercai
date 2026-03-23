from app.core.state import PipelineState
from app.config.logging_config import logger

class ClarificationEngine:
    """Evaluate if clarification is needed."""

    CONFIDENCE_THRESHOLD = 0.6

    def evaluate(self, state: PipelineState) -> PipelineState:
        """
        Determine if user clarification is needed.

        Args:
            state: Pipeline state

        Returns:
            Updated state with clarification info
        """
        if state.confidence_score < self.CONFIDENCE_THRESHOLD:
            state.needs_clarification = True
            state.clarification_question = self._generate_clarification_question(state)
            logger.info("Clarification needed due to low confidence")
        else:
            state.needs_clarification = False

        return state

    @staticmethod
    def _generate_clarification_question(state: PipelineState) -> str:
        """Generate a clarification question based on intent."""
        intent = state.intent

        questions = {
            'price_filter': 'Could you specify a price range (e.g., under $100)?',
            'rating_filter': 'What minimum rating are you looking for (e.g., 4 stars)?',
            'stock_check': 'Are you looking for products with specific quantity levels?',
            'compare': 'Which products would you like to compare?',
            'recommendations': 'What criteria matter most to you (price, rating, availability)?',
        }

        return questions.get(intent, 'Could you provide more details about what you\'re looking for?')
