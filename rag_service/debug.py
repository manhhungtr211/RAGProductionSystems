"""
Debug script - chạy RAG pipeline từng bước trong terminal, không cần FastAPI.
Usage: python debug.py
"""
# Load .env TRƯỚC KHI import bất kỳ module nào khác
from dotenv import load_dotenv
load_dotenv()

import asyncio
from src.schemas import RetrievalInput

# ── BƯỚC 1: Khởi tạo LLM ─────────────────────────────────────────────────────
print("\n[1] Khởi tạo LLM (ChatOllama)...")
from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2", base_url="http://localhost:11434", temperature=0.5)
print("    ✓ LLM OK")

# ── BƯỚC 2: Khởi tạo Retriever ───────────────────────────────────────────────
print("\n[2] Khởi tạo Retriever (FAISS)...")
from src.retrieval import Retriever
retriever = Retriever()
print("    ✓ Retriever OK")

# ── BƯỚC 3: Tạo StructuredTool ───────────────────────────────────────────────
print("\n[3] Tạo StructuredTool...")
from langchain_core.tools import StructuredTool
from pydantic import BaseModel

class SearchInput(BaseModel):
    query: str

search_tool = StructuredTool.from_function(
    name="search_docs",
    description="Search for documents relevant to a query",
    func=retriever.retrieve,
    args_schema=SearchInput,
)
llm_with_tools = llm.bind_tools([search_tool])
print("    ✓ Tool + bind_tools OK")

# ── BƯỚC 4: Test retriever trực tiếp ─────────────────────────────────────────
QUERY = "What is Germany?"
print(f"\n[4] Test retriever với query: '{QUERY}'")
result = retriever.retrieve(QUERY)
print(f"    Kết quả retriever:\n    {result[:200]}...")

# ── BƯỚC 5 & 6: Gộp tất cả async vào MỘT asyncio.run() duy nhất ─────────────
from src.prompt import template
from src.generator import generate

async def main():
    # Bước 5: Test LLM invoke
    print("\n[5] Test LLM ainvoke với tool binding...")
    messages = template.format_messages(question=QUERY)
    print(f"    Messages: {[type(m).__name__ for m in messages]}")
    print(f"Message:{messages}")

    ai_msg = await llm_with_tools.ainvoke(messages)
    print(f"ai_msg:{ai_msg}")
    print(f"    AI response type: {type(ai_msg).__name__}")
    print(f"    Tool calls: {ai_msg.tool_calls}")
    print(f"    Content: {str(ai_msg.content)[:200]}")

    # Bước 6: Test full generate pipeline
    print("\n[6] Test full generate pipeline (stream)...")
    message = RetrievalInput(
        user_input=QUERY,
        session_id="debug-session",
        user_id="debug-user",
    )
    full_response = ""
    async for chunk in generate(llm_with_tools, message):
        print(chunk, end="", flush=True)
        full_response += chunk
    print(f"\n\n    ✓ Total chars: {len(full_response)}")

asyncio.run(main())
print("\n[DONE] Pipeline chạy thành công!")
