from app.core.state import PipelineState
from app.query.query_handler import QueryHandler
from app.retrieval.retriever import Retriever
from app.diagnosis.diagnosis_engine import DiagnosisEngine
from app.diagnosis.response_builder import ResponseBuilder
from app.loop.clarification_engine import ClarificationEngine


class AutomotiveRAGPipeline:
    def __init__(self, settings):
        self.settings = settings
        self.query_handler = QueryHandler()
        self.retriever = Retriever(settings)
        self.diagnosis_engine = DiagnosisEngine(settings)
        self.response_builder = ResponseBuilder()
        self.clarification_engine = ClarificationEngine()

    def run(self, user_query: str) -> dict:
        state = PipelineState(user_query=user_query)

        state.query_payload = self.query_handler.process(user_query)
        state.rewritten_query = state.query_payload["normalized_query"]

        state.retrieved_docs = self.retriever.retrieve(state.query_payload)

        state.diagnosis_result = self.diagnosis_engine.diagnose(
            query_payload=state.query_payload,
            retrieved_docs=state.retrieved_docs,
        )

        clarification = self.clarification_engine.evaluate(state.diagnosis_result)
        state.needs_clarification = clarification["needs_clarification"]
        state.clarification_question = clarification["clarification_question"]

        state.final_response = self.response_builder.build(
            diagnosis_result=state.diagnosis_result,
            needs_clarification=state.needs_clarification,
            clarification_question=state.clarification_question,
        )

        return {
            "response": state.final_response,
            "needs_clarification": state.needs_clarification,
            "clarification_question": state.clarification_question,
            "diagnosis_result": state.diagnosis_result,
            "retrieved_docs": state.retrieved_docs,
        }