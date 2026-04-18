import faiss
import boto3
import os
import tempfile
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class VectorDB():
    def __init__(self, bucket: str, key: str, model_name: str = "all-MiniLM-L6-v2"):
        # 1. Khởi tạo Embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name
        )
        
        # 2. Load từ S3 LocalStack qua file tạm (Đã fix lỗi WinError 32)
        self.docs = self.load_from_s3(bucket, key)
        
        # 3. Chia nhỏ văn bản
        self.text_chunks = self.text_splitter(self.docs)
        
        # 4. Đưa vào FAISS
        self.vector_store = FAISS.from_documents(self.text_chunks, self.embeddings) 

    def load_from_s3(self, bucket: str, key: str):
        """Kết nối tới LocalStack, tải file về máy và nạp vào LangChain"""
        
        s3_client = boto3.client(
            's3',
            endpoint_url='http://127.0.0.1:4566',
            aws_access_key_id='test',
            aws_secret_access_key='test',
            region_name='us-east-1'
        )
        
        # BƯỚC FIX LỖI WINDOWS:
        # Tạo file tạm nhưng đóng nó ngay lập tức để giải phóng khóa (lock)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp_path = tmp.name
        tmp.close() # Đóng handle ngay để Windows cho phép các tiến trình khác ghi/đọc

        try:
            print(f"📥 Đang tải {key} từ S3 bucket {bucket}...")
            # Sử dụng download_file (truyền path) thay vì download_fileobj
            s3_client.download_file(bucket, key, tmp_path)
            
            # Bây giờ PyPDFLoader có thể mở file mà không bị xung đột
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()
            print(f"✅ Đã load thành công {len(documents)} trang từ PDF.")
            return documents
            
        except Exception as e:
            print(f"❌ Lỗi khi tương tác với S3: {e}")
            raise e
            
        finally:
            # Sau khi dữ liệu đã nằm trong RAM (biến documents), xóa file tạm trên ổ cứng
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                    print(f"🗑️ Đã dọn dẹp file tạm thành công.")
                except Exception as cleanup_error:
                    print(f"⚠️ Cảnh báo: Không thể xóa file tạm tại {tmp_path}: {cleanup_error}")

    def text_splitter(self, documents):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        return splitter.split_documents(documents)

    def save_db(self, store_path: str):        
        self.vector_store.save_local(store_path)
        print(f"💾 Vector DB đã được lưu tại thư mục: {store_path}")

# --- Thực thi ---
if __name__ == "__main__":
    BUCKET_NAME = "rag-data"
    FILE_KEY = "Employee-Handbook.pdf"
    
    try:
        my_db = VectorDB(bucket=BUCKET_NAME, key=FILE_KEY)
        my_db.save_db("faiss_index")
    except Exception as e:
        print(f"🚨 Project thất bại: {e}")