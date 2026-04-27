from langchain_core.tools import Tool
from src.retrieval import Retriever


# Define function calling the retrieval function
# This function is used to search for documents relevant to a query.
retrieve = Retriever()

search_tool = Tool(
    name="search_docs",
    description="Search for documents relevant to a query",
    func=retrieve.retrieve,
)