import os
import sys

# Ensure src/ can be imported when running script from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.vectorstores import FAISS
from src.ingestion.loader import load_from_s3
from src.chunking.chunker import Chunker
from src.embedding.base_embedder import get_embeddings

def build_and_save_index(bucket: str, key: str, save_path: str, model_name: str = "all-MiniLM-L6-v2"):
    """
    Load document from S3, split it, embed it, and save the FAISS index.
    """
    print(f"🚀 Starting index build for {key} in bucket {bucket}")
    
    # 1. Load data
    docs = load_from_s3(bucket, key)
    
    # 2. Chunk data
    chunker = Chunker(chunk_size=1000, chunk_overlap=100)
    text_chunks = chunker.split(docs)
    
    # 3. Embed and store
    print("🧠 Creating embeddings and building FAISS index...")
    embeddings = get_embeddings(model_name)
    vector_store = FAISS.from_documents(text_chunks, embeddings)
    
    # 4. Save to disk
    os.makedirs(save_path, exist_ok=True)
    vector_store.save_local(save_path)
    print(f"💾 Vector DB successfully saved to {save_path}")

if __name__ == "__main__":
    BUCKET_NAME = "rag-data"
    FILE_KEY = "Employee-Handbook.pdf"
    SAVE_PATH = "data/vectordb/faiss_index"
    
    try:
        build_and_save_index(bucket=BUCKET_NAME, key=FILE_KEY, save_path=SAVE_PATH)
    except Exception as e:
        print(f"🚨 Index build failed: {e}")
