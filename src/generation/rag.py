from langchain_ollama import ChatOllama
from config.settings import SETTINGS
from src.retrieval.retriever import Retriever
from src.generation.llm_client import generate
from src.embedding.embedding_cache import SemanticCache
from langfuse import get_client
from src.api.schemas import RetrievalInput
from src.tools import make_search_tool

langfuse = get_client()

class Rag():
    def __init__(self): 
        self.llm = ChatOllama(
            model="llama3.2",
            base_url="http://localhost:11434",
            temperature=0.5,
        )
        self.retrieve = Retriever()
        self.search_tool = make_search_tool(self.retrieve)
        self.llm_with_tools = self.llm.bind_tools([self.search_tool])

        # Response cache – cache LLM final answer
        self.response_cache = SemanticCache(
            embeddings=self.retrieve.embeddings,
            key_prefix="rag:response:",
        )

    async def get_sse_response(self, query: RetrievalInput):
        # ── Level 1: Response cache ─────────────────────────────────────
        cached_answer = self.response_cache.get(query.user_input)
        if cached_answer is not None:
            yield cached_answer
            return
        # ─────────────────────────────────────────────────────────────
        # MISS → manual trace creation
        trace = langfuse.start_trace(
            name="RAG Pipeline",
            session_id=query.session_id,
            user_id=query.user_id,
            input={"question": query.user_input},
        )

        full_response = ""
        async for chunk in generate(self.llm_with_tools, query, self.search_tool):
            full_response += chunk
            yield f"{chunk} "

        # Log final answer after streaming
        if full_response:
            trace.update(output={"answer": full_response})
            self.response_cache.set(query.user_input, full_response)
