from src.utils import logger
import json
import faiss
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langfuse import observe, propagate_attributes, get_client

langfuse = get_client()


class Retriever:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name
        )
        self.vector_store = FAISS.load_local(
            "src/faiss_index", self.embeddings, allow_dangerous_deserialization=True
        )
    @observe(name="Retrieval Step")
    def retrieve(self, question: str, k: int = 2):
        """Truy xuất tài liệu và đẩy metadata chi tiết lên Langfuse."""
        # Thực hiện tìm kiếm
        docs = self.vector_store.similarity_search(question, k)
            # Chuyển đổi format để log
        retrieved_content = [
            {"content": doc.page_content, "metadata": doc.metadata} 
            for doc in docs
        ]
        langfuse.set_current_trace_io(input={"query": question}, output={"result": retrieved_content})
        # NÂNG CẤP V4: Cập nhật thông tin chi tiết vào Span hiện tại
        with propagate_attributes(
            trace_name = "trace-name",
            metadata={"k_value": k, "model": "all-MiniLM-L6-v2"}
        ):
            return json.dumps([d["content"] for d in retrieved_content])
