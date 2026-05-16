"""
src/ingestion/splitter.py

Re-exports the Chunker for use in ingestion pipelines.
The actual chunking logic lives in src/chunking/chunker.py.
"""
from src.chunking.chunker import Chunker  # noqa: F401

__all__ = ["Chunker"]
