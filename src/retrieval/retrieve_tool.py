import json
import logging
import faiss
from langchain_community.vectorstores import FAISS
from langfuse import observe, get_client
from src.embedding.base_embedder import get_embeddings
from src.embedding.cache import SemanticCache
from config.settings import SETTINGS
from langfuse.langchain import CallbackHandler

logger = logging.getLogger(__name__)
# langfuse client is removed here as it is not needed for @observe usage
langfuse = get_client()

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
FAISS_INDEX_PATH = "data/vectordb/faiss_index"


class Retrieve_Tool:
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.embeddings = get_embeddings(model_name)
        self.vector_store = FAISS.load_local(
            FAISS_INDEX_PATH, self.embeddings, allow_dangerous_deserialization=True
        )
        self.cache = SemanticCache(
            embeddings=self.embeddings,
            threshold=SETTINGS.REDIS_CACHE_THRESHOLD,
        )

    @observe(name="Retrieval Step")
    def retrieve(self, query, k: int = 2):
        """Retrieve documents and push detailed context to Langfuse for LLM-as-a-judge evaluation."""
        # Tool.ainvoke() may pass args as dict {"query": "..."} instead of string
        #handler = CallbackHandler()
        if isinstance(query, dict):
            query = query.get("query") or query.get("question") or str(query)

        # FAISS similarity search
        docs = self.vector_store.similarity_search(query, k)
        for doc in docs:
            print(doc.page_content)

        # Prepare retrieved context in structured form
        retrieved_passages = [
            {"content": doc.page_content, "metadata": doc.metadata}
            for doc in docs
        ]
        context_texts = [d["content"] for d in retrieved_passages]

        # @observe creates a span → use update_current_span
        # input/output → LLM-as-a-judge evaluator maps {{input}}, {{output}} variables
        langfuse.update_current_generation(
            metadata={
                "k_value": k,
                "embedding_model": EMBEDDING_MODEL,
                "num_docs_retrieved": len(docs),
                "context": context_texts,
            },
        )
        # Return JSON string for LangChain tool (preserve original format)
        return json.dumps(context_texts)
