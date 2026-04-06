from langchain.chat_models import init_chat_model
from src.settings import SETTINGS
from langchain_core.tools import Tool
from src.retrieval import Retriever
from src.generator import generate
# Initialize the LLM with the specified model and settings
# This code initializes a chat model using the OpenAI API with specific parameters.
# The model used is "gemini-2.5-flash", with a temperature setting of 0.7 for response variability.
class Rag():
    def __init__(self): 
        self.llm = init_chat_model(
        "gemini-2.5-flash",
        api_key=SETTINGS.API_KEY,
        temperature=0.5,
        model_provider="google_genai",
        )
        self.retrieve = Retriever()
        self.search_tool = Tool(
            name="search_docs",
            description="Search for documents relevant to a query",
            func=self.retrieve.retrieve,
        )
        self.llm_with_tools = self.llm.bind_tools([self.search_tool])

    async def get_sse_response(self, query):
        async for chunk in generate(self.llm_with_tools, query):
            yield f"data: {chunk}\n\n"
        
