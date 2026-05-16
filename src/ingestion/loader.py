"""
src/ingestion/loader.py

Responsible for loading raw documents from local filesystem or remote
storage (e.g., AWS S3 / LocalStack) and returning LangChain Document objects.
"""
import os
import tempfile

import boto3
from langchain_community.document_loaders import PyPDFLoader


def load_pdf_local(file_path: str):
    """Load a PDF from the local filesystem."""
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    print(f"✅ Loaded {len(documents)} pages from local PDF: {file_path}")
    return documents


def load_from_s3(bucket: str, key: str):
    """
    Connect to LocalStack S3, download a file, and load it via LangChain.

    Windows fix: creates a NamedTemporaryFile, closes it immediately to
    release the OS lock, then passes the path to PyPDFLoader.
    """
    s3_client = boto3.client(
        "s3",
        endpoint_url="http://127.0.0.1:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
    )

    # Create temp file and close it immediately (Windows lock fix)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_path = tmp.name
    tmp.close()

    try:
        print(f"📥 Downloading {key} from S3 bucket {bucket}...")
        s3_client.download_file(bucket, key, tmp_path)

        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        print(f"✅ Successfully loaded {len(documents)} pages from PDF.")
        return documents

    except Exception as e:
        print(f"❌ Error interacting with S3: {e}")
        raise

    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
                print("🗑️ Cleaned up temporary file.")
            except Exception as cleanup_error:
                print(f"⚠️ Warning: Could not delete temp file {tmp_path}: {cleanup_error}")
