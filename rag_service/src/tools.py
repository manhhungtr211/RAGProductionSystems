from langchain_core.tools import StructuredTool
from pydantic import BaseModel


class SearchInput(BaseModel):
    query: str


def make_search_tool(retriever):
    """Tạo search tool từ Retriever instance được truyền vào (tránh double init)."""
    return StructuredTool.from_function(
        name="search_docs",
        description="Search for documents relevant to a query",
        func=retriever.retrieve,
        args_schema=SearchInput,
    )