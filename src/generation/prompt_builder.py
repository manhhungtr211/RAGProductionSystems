from langfuse import get_client
from langchain_core.prompts import ChatPromptTemplate

langfuse = get_client()
try:
    langfuse.create_prompt(
        name="rag-assistant",
        type="chat",
        prompt=[
            {
                "role": "system",
                "content": (
                    "You are a helpful, factual assistant answering user questions using retrieved context. "
                    "To fetch relevant documents, you will use the `search_docs` tool. "
                    "Respond in a concise, neutral tone for a general audience. "
                    "Use a maximum of 3 short sentences."
                    "If the answer isn't in the context, say you don't know."
                )
            },
            {"role": "user", "content": "{{question}}"}
        ],
        tags=["staging"],
        labels=["production"]
    )
except Exception as e:
    print(f"[prompt_builder.py] create_prompt skipped: {e}")

langfuse_prompt = langfuse.get_prompt("rag-assistant", type="chat")
# Convert sang LangChain format
# Langfuse dùng {{var}}, LangChain dùng {var} → get_langchain_prompt() tự convert
template = ChatPromptTemplate.from_messages(
    langfuse_prompt.get_langchain_prompt()
)
