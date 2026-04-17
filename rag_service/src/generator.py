from src.tools import search_tool
from src.prompt import template, langfuse_prompt
from langchain_core.messages import AIMessage
from langchain_core.tracers import ConsoleCallbackHandler
from src.settings import SETTINGS
from langchain_core.globals import set_verbose
from fastapi import APIRouter
from src.schemas import RetrievalInput
from langfuse.langchain import CallbackHandler
from langfuse import get_client,propagate_attributes
import uuid

langfuse = get_client()
set_verbose(True)

def _extract_text(content) -> str:
    """Normalize LLM chunk content to plain string.
    Gemini can return a list of dicts: [{'type': 'text', 'text': '...'}]
    """
    if isinstance(content, list):
        return "".join(
            part.get("text", "") for part in content if isinstance(part, dict)
        )
    return content or ""

#check vì sao Gen lại > langchain-call (có phải do TTFT)
async def generate(llm_with_tools, input: RetrievalInput):
    """Generate a response to a question using the LLM with tools."""
    # Format the messages using the template and the question
    langfuse_handler = CallbackHandler()
    messages = template.format_messages(question=input.user_input)

    with langfuse.start_as_current_observation(as_type="span", name="langchain-call"):
        langfuse.update_current_generation(prompt=langfuse_prompt)
        with propagate_attributes(session_id=input.session_id, user_id=input.user_id):
            ai_msg = await llm_with_tools.ainvoke(messages, config={"callbacks": [langfuse_handler]})

    # Create an AI message using the LLM with tools
    messages.append(ai_msg)
    
    has_tool_calls = isinstance(ai_msg, AIMessage) and bool(ai_msg.tool_calls)

    if has_tool_calls:
        # Invoke each tool and collect results
        for tool_call in ai_msg.tool_calls:
            # Parse message to arguments of the function calling
            selected_tool = {"search_docs": search_tool}.get(tool_call["name"].lower())
            if selected_tool is None:
                continue
            tool_msg = await selected_tool.ainvoke(tool_call, config={"callbacks": [langfuse_handler]})
            messages.append(tool_msg)
            print(messages)
    
    # Finally, get response by invoking the LLM with the all messages
    # Currently, list of messages includes:
    # 1. User question
    # 2. AI message with tool calls (if any)
    # 3. Tool responses (if any)
    async for chunk in llm_with_tools.astream(messages, config={"callbacks": [langfuse_handler]}):
        text = _extract_text(chunk.content)
        if text:
            yield text