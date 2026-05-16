from langchain_core.tools import StructuredTool
from pydantic import BaseModel


class SearchInput(BaseModel):
    query: str


def search_tool(retrieve_tool):
    """Tạo search tool từ Retriever instance được truyền vào (tránh double init)."""
    return StructuredTool.from_function(
        name="search_docs",
        description="Search for documents relevant to a query",
        func=retrieve_tool.retrieve,
        args_schema=SearchInput,
    )
