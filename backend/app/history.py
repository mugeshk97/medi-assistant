from typing import Any, Dict, List

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


def serialize_history(messages: List[BaseMessage]) -> List[Dict[str, Any]]:
    """
    Converts a list of LangChain messages to a JSON-serializable format.
    """
    history = []
    for msg in messages:
        role = "unknown"
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        elif msg.type == "human":
            role = "user"
        elif msg.type == "ai":
            role = "assistant"

        history.append({"role": role, "content": msg.content, "id": msg.id})
    return history
