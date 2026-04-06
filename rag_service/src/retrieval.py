from src.utils import logger
import json
import faiss
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

class Retriever:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name
        )
        self.vector_store = FAISS.load_local(
            "src/faiss_index", self.embeddings, allow_dangerous_deserialization=True
        )
    # Define the retrieval function
    def retrieve(self, question: str, k: int = 2):
        """Generate tool call for retrieval or respond."""

        # Perform the retrieval using the vector store
        # retrieved_docs = vector_store.similarity_search(question])
        logger.debug(f"Retrieving documents for question: {question}")
        docs = self.vector_store.similarity_search(question, k)
        retrieved_docs = [doc.page_content for doc in docs]
        return json.dumps(retrieved_docs)  # Return as JSON string for compatibility with LangChain tools
