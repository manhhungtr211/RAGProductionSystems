from .tools import search_tool
from src.generation.prompt_builder import template, langfuse_prompt
from langchain_core.messages import AIMessage
from config.settings import SETTINGS
from langchain_core.globals import set_verbose
from src.api.schemas import RetrievalInput
from langfuse import observe, get_client
from langfuse.langchain import CallbackHandler
import uuid

set_verbose(True)
langfuse = get_client()

def extract_text(content) -> str:
    """Normalize LLM chunk content to plain string.
    Gemini can return a list of dicts: [{'type': 'text', 'text': '...'}]
    """
    if isinstance(content, list):
        return "".join(
            part.get("text", "") for part in content if isinstance(part, dict)
        )
    return content or ""

@observe(as_type="generation", name="langchain-call")
async def generate(llm_with_tools, input: RetrievalInput, search_tool, callbacks=None):
    """Generate a response to a question using the LLM with tools."""
    # Format the messages using the template and the question
    langfuse_handler = CallbackHandler
    combined_callbacks = [langfuse_handler] if langfuse_handler else []
    if callbacks:
        combined_callbacks.extend(callbacks)
    
    messages = template.format_messages(question=input.user_input)
    langfuse.update_current_generation(prompt=langfuse_prompt)
    ai_msg = await llm_with_tools.ainvoke(messages, config={"callbacks": combined_callbacks})
    # Create an AI message using the LLM with tools
    messages.append(ai_msg)
    has_tool_calls = isinstance(ai_msg, AIMessage) and bool(ai_msg.tool_calls)
    if has_tool_calls:
        # Invoke each tool and collect results
        for tool_call in ai_msg.tool_calls:
            print(f"Tool call: {tool_call}")
            args = tool_call["args"]
            for key, value in args.items():
                if isinstance(value, dict):
                    args[key] = value.get("value") or value.get("content") or str(value)
            # Parse message to arguments of the function calling
            selected_tool = {"search_docs": search_tool}.get(tool_call["name"].lower())
            if selected_tool is None:
                continue
            tool_msg = await selected_tool.ainvoke(tool_call, config={"callbacks": combined_callbacks})
            messages.append(tool_msg)
    
    # Finally, get response by invoking the LLM with the all messages
    async for chunk in llm_with_tools.astream(messages, config={"callbacks": combined_callbacks}):
        text = extract_text(chunk.content)
        if text:
            yield text
