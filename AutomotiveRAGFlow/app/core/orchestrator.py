from app.core.pipeline import AutomotiveRAGPipeline


class AutomotiveRAGOrchestrator:
    def __init__(self, settings):
        self.pipeline = AutomotiveRAGPipeline(settings)

    def handle_query(self, user_query: str) -> dict:
        return self.pipeline.run(user_query)