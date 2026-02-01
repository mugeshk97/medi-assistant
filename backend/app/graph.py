from typing import Annotated, Literal, TypedDict
import logging

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from app.guardrails import validate_input
from app.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    is_safe: bool


llm = ChatOpenAI(model=settings.MODEL_NAME, api_key=settings.OPENAI_API_KEY)


async def check_input(state: State):
    """
    Node to check if the last user message is safe.
    """
    messages = state["messages"]
    last_user_message = messages[-1]

    logger.debug(
        f"Checking input safety for message: {last_user_message.content[:50]}..."
    )
    is_safe = await validate_input(last_user_message.content)

    if not is_safe:
        logger.warning("Input deemed unsafe by guardrail")
        return {"is_safe": False}

    logger.debug("Input passed safety check")
    return {"is_safe": True}


async def call_model(state: State):
    """
    Node that calls the LLM.
    """
    if not state.get("is_safe", True):
        # Should not get here if routed correctly, but safe fallback
        logger.error("call_model invoked with unsafe input - this should not happen")
        return {
            "messages": [
                AIMessage(
                    content="I cannot process that request due to safety policies."
                )
            ]
        }

    logger.debug("Invoking LLM...")
    response = await llm.ainvoke(state["messages"])
    logger.debug(f"LLM response received: {len(response.content)} characters")

    # Output guardrail removed for streaming support
    return {"messages": [response]}


def route_safety(state: State) -> Literal["agent", "unsafe_input"]:
    if state.get("is_safe"):
        return "agent"
    return "unsafe_input"


async def unsafe_input_response(state: State):
    return {
        "messages": [
            AIMessage(
                content="I cannot process that request as it violates safety guidelines."
            )
        ]
    }


# Build Graph
builder = StateGraph(State)

builder.add_node("guardrail_check", check_input)
builder.add_node("agent", call_model)
builder.add_node("unsafe_input", unsafe_input_response)

builder.add_edge(START, "guardrail_check")
builder.add_conditional_edges("guardrail_check", route_safety)
builder.add_edge("agent", END)
builder.add_edge("unsafe_input", END)
