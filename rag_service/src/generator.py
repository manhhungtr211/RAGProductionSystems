from src.tools import search_tool
from src.prompt import template
from langchain_core.messages import AIMessage
from langchain_core.tracers import ConsoleCallbackHandler
from src.settings import SETTINGS
from langchain_core.globals import set_verbose
from fastapi import APIRouter
from src.schemas import RetrievalInput
from langfuse.langchain import CallbackHandler
from langfuse import get_client,propagate_attributes

langfuse = get_client()


set_verbose(True)

async def generate(llm_with_tools, message: RetrievalInput):
    """Generate a response to a question using the LLM with tools."""
    # Format the messages using the template and the question
    langfuse_handler = CallbackHandler()
    messages = template.format_messages(question=message.user_input)

    with langfuse.start_as_current_observation(as_type="span", name="langchain-call"):
    # Propagate session_id to all observations
        with propagate_attributes(session_id=message.section_id):
            # Pass handler to the chain invocation
            ai_msg = await llm_with_tools.ainvoke(messages, config={"callbacks": [langfuse_handler]})

    # Create an AI message using the LLM with tools
    messages.append(ai_msg)
    
    # If the AI message contains tool calls, invoke the tools and append their responses
    if isinstance(ai_msg, AIMessage) and hasattr(ai_msg, "tool_calls"):
        for tool_call in ai_msg.tool_calls:
            # Parse message to arguments of the function calling
            selected_tool = {"search_docs": search_tool}[tool_call["name"].lower()]
            tool_msg = await selected_tool.ainvoke(tool_call, config={"callbacks": [langfuse_handler]})
            messages.append(tool_msg)
    
    # Finally, get response by invoking the LLM with the all messages
    # Currently, list of messages includes:
    # 1. User question  
    # 2. AI message with tool calls (if any) 
    # 3. Tool responses (if any)
    async for chunk in llm_with_tools.astream(messages, config={"callbacks": [langfuse_handler]}):
        yield chunk.content