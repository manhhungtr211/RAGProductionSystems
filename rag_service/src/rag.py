from langchain_ollama import ChatOllama
from src.settings import SETTINGS
from langchain_core.tools import StructuredTool
from pydantic import BaseModel
from src.retrieval import Retriever
from src.generator import generate

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

    async def get_sse_response(self, query):
        async for chunk in generate(self.llm_with_tools, query):
            yield f"{chunk} "
        
