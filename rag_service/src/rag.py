from langchain_ollama import ChatOllama
from src.settings import SETTINGS
from langchain_core.tools import StructuredTool
from pydantic import BaseModel
from src.retrieval import Retriever
from src.generator import generate
from src.cache import SemanticCache
from langfuse import get_client
from src.schemas import RetrievalInput

langfuse = get_client()

class SearchInput(BaseModel):
    query: str


class Rag():
    def __init__(self): 
        self.llm = ChatOllama(
            model="llama3.2",
            base_url="http://localhost:11434",
            temperature=0.5,
        )
        self.retrieve = Retriever()
        self.search_tool = StructuredTool.from_function(
            name="search_docs",
            description="Search for documents relevant to a query",
            func=self.retrieve.retrieve,
            args_schema=SearchInput,
        )
        self.llm_with_tools = self.llm.bind_tools([self.search_tool])

        # Response cache – cache câu trả lời cuối cùng của LLM
        self.response_cache = SemanticCache(
            embeddings=self.retrieve.embeddings,
            key_prefix="rag:response:",
        )

    async def get_sse_response(self, query: RetrievalInput):
        # ── Tầng 1: Response cache ─────────────────────────────────────
        cached_answer = self.response_cache.get(query.user_input)
        if cached_answer is not None:
            yield cached_answer
            return
        # ─────────────────────────────────────────────────────────────
        # MISS → tạo trace thủ công (không dùng @observe vì async generator
        # không tương thích — context bị drop sau mỗi yield)
        trace = langfuse.start_trace(
            name="RAG Pipeline",
            session_id=query.session_id,
            user_id=query.user_id,
            input={"question": query.user_input},
        )

        full_response = ""
        async for chunk in generate(self.llm_with_tools, query):
            full_response += chunk
            yield f"{chunk} "

        # Log final answer sau khi stream kết thúc
        if full_response:
            trace.update(output={"answer": full_response})
            self.response_cache.set(query.user_input, full_response)
