import os
import sys

# Ensure src/ can be imported when running script from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.vectorstores import FAISS
from src.ingestion.loader import load_from_s3, load_pdf_local
from src.chunking.chunker import Chunker
from src.embedding.base_embedder import get_embeddings
import requests

def build_and_save_index(bucket: str, key: str, save_path: str, model_name: str = "all-MiniLM-L6-v2"):
    """
    Load document from S3, split it, embed it, and save the FAISS index.
    """
    print(f"🚀 Starting index build for {key} in bucket {bucket}")
    url = "http://127.0.0.1:4566"
    # 1. Load data
    try:
        # Cố gắng gõ cửa S3 trong 2 giây
        check_s3 = requests.get(url, timeout=2)
        
        # Nếu gõ cửa thành công và S3 trả lời OK (200)
        if check_s3.status_code == 200:
            print("✅ LocalStack S3 is available, loading from S3")
            docs = load_from_s3(bucket, key)
        else:
            # S3 có chạy nhưng bị lỗi gì đó (vd: 403, 500...)
            print(f"⚠️ S3 error (Status: {check_s3.status_code}), loading from local")
            docs = load_pdf_local(f"./data/raw/{key}")

    except requests.exceptions.RequestException:
        # BẮT TẤT CẢ CÁC LỖI: Sập mạng, Timeout, Server tắt...
        # Thay vì crash app, nó sẽ nhảy vào đây chạy local
        print("❌ LocalStack S3 is offline or timed out, loading from local")
        docs = load_pdf_local(f"./data/raw/{key}")
    print(docs)
    
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
