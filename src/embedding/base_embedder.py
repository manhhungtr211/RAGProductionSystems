"""
src/embedding/base_embedder.py

Provides a factory function and base wrapper for embedding models.
Currently wraps HuggingFaceEmbeddings — swap out for OpenAI, Cohere, etc.
"""
from langchain_huggingface import HuggingFaceEmbeddings

DEFAULT_MODEL = "all-MiniLM-L6-v2"


def get_embeddings(model_name: str = DEFAULT_MODEL) -> HuggingFaceEmbeddings:
    """
    Return a LangChain-compatible embeddings instance.

    Args:
        model_name: HuggingFace model identifier (or path to local model).

    Returns:
        HuggingFaceEmbeddings instance ready for embed_query / embed_documents.
    """
    return HuggingFaceEmbeddings(model_name=model_name)
