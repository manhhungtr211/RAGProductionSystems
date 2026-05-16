from src.utils import logger
import json
import faiss
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langfuse import observe, propagate_attributes, get_client
from src.cache import SemanticCache
from src.settings import SETTINGS

langfuse = get_client()

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class Retriever:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name
        )
        self.vector_store = FAISS.load_local(
            "src/faiss_index", self.embeddings, allow_dangerous_deserialization=True
        )
        self.cache = SemanticCache(
            embeddings=self.embeddings,
            threshold=SETTINGS.REDIS_CACHE_THRESHOLD,
        )

    @observe(name="Retrieval Step")
    def retrieve(self, question, k: int = 2):
        """Truy xuất tài liệu và đẩy context chi tiết lên Langfuse để LLM-as-a-judge đánh giá."""
        # Tool.ainvoke() có thể truyền args là dict {"query": "..."} thay vì string
        if isinstance(question, dict):
            question = question.get("query") or question.get("question") or str(question)

        # Thực hiện tìm kiếm FAISS
        docs = self.vector_store.similarity_search(question, k)
        for doc in docs:
            print(doc.page_content)

        # Chuẩn bị retrieved context dưới dạng có cấu trúc
        retrieved_passages = [
            {"content": doc.page_content, "metadata": doc.metadata}
            for doc in docs
        ]
        context_texts = [d["content"] for d in retrieved_passages]

        # @observe tạo span → dùng update_current_span
        # input/output → evaluator LLM-as-a-judge map biến {{input}}, {{output}}
        langfuse.update_current_span(
            input={"query": question},
            output={"context": context_texts},
            metadata={
                "k_value": k,
                "embedding_model": EMBEDDING_MODEL,
                "num_docs_retrieved": len(docs),
                "context": context_texts,
            },
        )
        # Trả về JSON string cho LangChain tool (giữ nguyên format cũ)
        return json.dumps(context_texts)