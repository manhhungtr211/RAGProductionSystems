"""
src/chunking/chunker.py

Text splitting / chunking logic extracted from the old vectordb.py.
Wraps LangChain's RecursiveCharacterTextSplitter for easy configuration.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter


class Chunker:
    """
    Splits LangChain Document objects into smaller chunks suitable for
    embedding and vector storage.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def split(self, documents: list) -> list:
        """Split a list of LangChain Documents into smaller chunks."""
        chunks = self.splitter.split_documents(documents)
        print(f"✂️ Split {len(documents)} documents into {len(chunks)} chunks.")
        return chunks
