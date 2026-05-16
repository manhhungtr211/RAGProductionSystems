"""
src/reranking/base_reranker.py

Abstract base class for rerankers.
Implement this interface to add new reranking backends (Cohere, cross-encoder, etc.).
"""
from abc import ABC, abstractmethod


class BaseReranker(ABC):
    """
    Interface for all rerankers.

    A reranker takes an original query and a list of retrieved passages,
    then returns them in a new order based on relevance scores.
    """

    @abstractmethod
    def rerank(self, query: str, passages: list[str], top_n: int = 3) -> list[str]:
        """
        Rerank the given passages for the query.

        Args:
            query:    The user's original question.
            passages: List of retrieved text passages.
            top_n:    Number of top passages to return after reranking.

        Returns:
            Reranked list of passages (most relevant first), limited to top_n.
        """
        ...
