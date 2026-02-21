"""API endpoints for chat management."""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schema import ChatRequest, ChatHistoryResponse, Thread
from app.history import serialize_history
from app.db import (
    save_thread,
    get_user_threads,
    update_thread_title,
    get_thread_by_id,
    delete_thread,
)
from app.deps import get_graph, get_current_user
from app.errors import UnauthorizedError, ThreadNotFoundError
from langchain_core.messages import HumanMessage
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


async def verify_thread_ownership(thread_id: str, user_id: str) -> None:
    """Verify that the user owns the specified thread."""
    thread = await get_thread_by_id(thread_id)
    if not thread:
        raise ThreadNotFoundError(f"Thread {thread_id} not found")
    if thread["user_id"] != user_id:
        logger.warning(
            f"Unauthorized access attempt: user {user_id} tried to access thread {thread_id}"
        )
        raise UnauthorizedError("You do not have permission to access this thread")


@router.post("/chat", response_class=StreamingResponse)
@limiter.limit("10/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    user_id: str = Depends(get_current_user),
    graph=Depends(get_graph),
):
    """
    Process a chat message through the LangGraph agent and stream the response.

    Rate limit: 10 requests per minute per IP.
    """
    try:
        # Check if this is the first message in the thread
        config = {"configurable": {"thread_id": chat_request.thread_id}}
        state_snapshot = await graph.aget_state(config)
        is_first_message = (
            not state_snapshot.values
            or len(state_snapshot.values.get("messages", [])) == 0
        )

        # Save thread association
        await save_thread(chat_request.thread_id, user_id)

        # Generate title from first message if needed
        if is_first_message:
            title = await generate_thread_title(chat_request.message)
            await update_thread_title(chat_request.thread_id, title)
            logger.info(f"Generated title for thread {chat_request.thread_id}: {title}")

        input_message = HumanMessage(content=chat_request.message)

        async def event_generator():
            try:
                # Use astream_events to catch token-by-token generation from the 'agent' node
                # we filter for 'on_chat_model_stream' events from the 'agent' node specifically.
                async for event in graph.astream_events(
                    {"messages": [input_message]}, config=config, version="v1"
                ):
                    kind = event["event"]
                    node = event.get("metadata", {}).get("langgraph_node", "")

                    # Use strict filtering for the agent node to avoid streaming guardrail checks
                    if kind == "on_chat_model_stream" and node == "agent":
                        content = event["data"]["chunk"].content
                        if content:
                            yield content
            except Exception as e:
                logger.error(f"Error during streaming: {str(e)}", exc_info=True)
                yield f"Error: {str(e)}"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def generate_thread_title(first_message: str, max_length: int = 50) -> str:
    """
    Generate a concise thread title from the first user message.
    """
    # Take first part of message and clean it
    title = first_message.strip()

    # If message is too long, truncate at word boundary
    if len(title) > max_length:
        title = title[:max_length].rsplit(" ", 1)[0] + "..."

    # Replace newlines with spaces
    title = " ".join(title.split())

    return title if title else "New Chat"


@router.get("/threads", response_model=List[Thread])
@limiter.limit("30/minute")
async def list_threads(
    request: Request,
    user_id: str = Depends(get_current_user),
):
    """
    List all threads for the requested user.

    Rate limit: 30 requests per minute per IP.
    """
    try:
        threads = await get_user_threads(user_id)
        return threads
    except Exception as e:
        logger.error(
            f"Error listing threads for user {user_id}: {str(e)}", exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{thread_id}", response_model=ChatHistoryResponse)
@limiter.limit("30/minute")
async def get_history(
    request: Request,
    thread_id: str,
    user_id: str = Depends(get_current_user),
    graph=Depends(get_graph),
):
    """
    Retrieve chat history for a specific thread.

    Verifies thread ownership before returning history.
    Rate limit: 30 requests per minute per IP.
    """
    # Verify ownership
    await verify_thread_ownership(thread_id, user_id)

    config = {"configurable": {"thread_id": thread_id}}

    try:
        state_snapshot = await graph.aget_state(config)
        if not state_snapshot.values:
            return ChatHistoryResponse(thread_id=thread_id, messages=[])

        messages = state_snapshot.values.get("messages", [])
        serialized = serialize_history(messages)

        return ChatHistoryResponse(thread_id=thread_id, messages=serialized)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/threads/{thread_id}")
@limiter.limit("10/minute")
async def delete_thread_endpoint(
    request: Request, thread_id: str, user_id: str = Depends(get_current_user)
):
    """
    Delete a thread and its associated data.

    Verifies thread ownership before deletion.
    Rate limit: 10 requests per minute per IP.
    """
    # Verify ownership before deletion
    await verify_thread_ownership(thread_id, user_id)

    try:
        await delete_thread(thread_id)
        return {"status": "success", "message": f"Thread {thread_id} deleted"}
    except Exception as e:
        logger.error(f"Error deleting thread {thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
