class AutomotiveRAGFlowError(Exception):
    """Base application exception."""


class VectorStoreEmptyError(AutomotiveRAGFlowError):
    """Raised when retrieval is attempted on an empty vector store."""