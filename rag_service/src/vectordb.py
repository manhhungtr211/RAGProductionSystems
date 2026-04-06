import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class VectorDB():
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", file_path: str = "../Germany.pdf"):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name
        )
        self.docs = self.load_pdf(file_path)
        self.text_chunks = self.text_splitter(self.docs)
        self.vector_store= FAISS.from_documents(self.text_chunks, self.embeddings) 

    def load_pdf(self, file_path: str):
        loader = PyPDFLoader(file_path)
        return loader.load()

    def text_splitter(self, documents):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        return splitter.split_documents(documents)
    def save_db(self, store_path: str):        
        self.vector_store.save_local(store_path)

