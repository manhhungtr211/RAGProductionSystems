"""
src/reranking/cohere_reranker.py

Cohere-backed reranker using the rerank-english-v3.0 model.
Placeholder — requires `cohere` package and COHERE_API_KEY in .env.

TODO:
    - pip install cohere
    - Add COHERE_API_KEY to .env
    - Uncomment and test the implementation below
"""
from src.reranking.base_reranker import BaseReranker


class CohereReranker(BaseReranker):
    """
    Reranker backed by Cohere's rerank API.

    TODO: Implement using the cohere SDK:
        import cohere
        co = cohere.Client(api_key=SETTINGS.COHERE_API_KEY.get_secret_value())
        results = co.rerank(query=query, documents=passages, top_n=top_n, model="rerank-english-v3.0")
        return [r.document["text"] for r in results.results]
    """

    def __init__(self, top_n: int = 3):
        self.top_n = top_n

    def rerank(self, query: str, passages: list[str], top_n: int = 3) -> list[str]:
        raise NotImplementedError("CohereReranker is not yet implemented. See TODO in this file.")
