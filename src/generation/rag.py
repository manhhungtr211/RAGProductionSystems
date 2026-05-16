from langchain_ollama import ChatOllama
from config.settings import SETTINGS
from src.retrieval.retrieve_tool import Retrieve_Tool
from src.generation.llm_client import generate
from src.embedding.embedding_cache import SemanticCache
from src.api.schemas import RetrievalInput
from src.generation.tools import search_tool
from langfuse import observe, propagate_attributes, get_client

langfuse = get_client()
class Rag():
    def __init__(self): 
        self.llm = ChatOllama(
            model="llama3.2",
            base_url="http://localhost:11434",
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
 
        full_response = ""
        async for chunk in generate(self.llm_with_tools, query, self.search_tool):
            full_response += chunk
            yield f"{chunk} "

        if full_response:
            self.response_cache.set(query.user_input, full_response)
            langfuse.set_current_trace_io(input={"query": query.user_input}, output={"result": full_response})
