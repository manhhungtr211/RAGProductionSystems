from langchain_ollama import ChatOllama
# pyrefly: ignore [missing-import]
from config.settings import SETTINGS
from src.retrieval.retrieve_tool import Retrieve_Tool
from src.generation.llm_client import generate
from src.embedding.cache import SemanticCache
from src.api.schemas import RetrievalInput
from langchain_groq import ChatGroq
import httpx
from src.generation.tools import search_tool
from langfuse import observe, propagate_attributes, get_client

langfuse = get_client()
def is_ollama_available(base_url="http://localhost:11434"):
    try:
        response = httpx.get(f"{base_url}/api/tags", timeout=2.0)
        print("Ollama is available")
        return response.status_code == 200
    except Exception:
        print("Ollama is not available")
        return False

class Rag():
    def __init__(self):
        if is_ollama_available():
            self.llm = ChatOllama(
                model="llama3.2",
                base_url="http://localhost:11434",
                temperature=0.5,
            )
        else:
            self.llm = ChatGroq(
                model="llama-3.1-8b-instant",
                api_key=SETTINGS.API_KEY.get_secret_value(),
                temperature=0.5,
            ) 
        self.retrieve = Retrieve_Tool()
        self.search_tool = search_tool(self.retrieve)
        self.llm_with_tools = self.llm.bind_tools([self.search_tool])
        self.response_cache = SemanticCache(
            embeddings=self.retrieve.embeddings,
            key_prefix="rag:response:",
        )
        
    @observe(name="RAG Systems")
    async def get_sse_response(self, query: RetrievalInput):
        # Thiết lập session và user cho Trace hiện tại
        with propagate_attributes(
            session_id=query.session_id,
            user_id=query.user_id
        ):        
            result = self.response_cache.get(query.user_input)
        if result is not None:
            yield result
            return
 
        full_response = ""
        async for chunk in generate(self.llm_with_tools, query, self.search_tool):
            full_response += chunk
            yield f"{chunk} "

        if full_response:
            self.response_cache.set(query.user_input, full_response)
            langfuse.set_current_trace_io(input={query.user_input}, output={full_response})
