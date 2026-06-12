import ollama

from datetime import datetime
from typing import List, Dict, Any
from services.memory import get_history, append_to_history
from services.rag import search_relevant_chunks
from services.ingestion import embedding_chunks
from models.documents import InterviewInfo
from database.redis_cache import get_redis_client
from sqlalchemy.orm import Session
from config import settings

from pydantic import BaseModel


class BookingExtractor(BaseModel):
    id: str
    session_id: str

    name: str
    email: str
    booking_date: datetime
    booking_time: datetime
    created_at: datetime


def book_interview(
    id: str,
    session_id: str,
    name: str,
    email: str,
    booking_date: str,
    booking_time: str,
    created_at: str,
) -> str:
    return "Intent Captured: Processing database transaction."


async def handle_agent_turn(session_id: str, user_message: str, db_session: Session) -> str:
    redis_client = get_redis_client()

    embeddings = embedding_chunks([user_message], settings.embedding_model)
    query_embedding = embeddings[0] if embeddings else []

    document_context = search_relevant_chunks(query_embedding)
    chat_history = get_history(redis_client, session_id)

    messages = [
        {
            "role": "system",
            "content": (
                "You are an HR assistant. Answer using the document context when relevant. "
                "If the user wants to book an interview, collect name, email, date, and time. "
                "Only call the booking tool when all fields are present.\n\n"
                f"DOCUMENT CONTEXT:\n{document_context}"
            ),
        },
        *chat_history,
        {"role": "user", "content": user_message},
    ]

    response = ollama.chat(model=settings.chat_model, messages=messages, tools=[book_interview])

    # handle tool calls if present
    tool_calls = []
    if hasattr(response, "message") and getattr(response.message, "tool_calls", None):
        tool_calls = response.message.tool_calls

    if tool_calls:
        for tool in tool_calls:
            if getattr(tool.function, "name", None) == "book_interview":
                booking_data = BookingExtractor(**tool.function.arguments)

                booking = InterviewInfo(
                    id=str(booking_data.id),
                    session_id=session_id,
                    name=booking_data.name,
                    email=str(booking_data.email),
                    booking_date=booking_data.booking_date,
                    booking_time=booking_data.booking_time,
                    created_at=booking_data.created_at,
                )
                db_session.add(booking)
                db_session.commit()

                reply = (
                    f"Thank you, {booking_data.name}. Your interview is booked for "
                    f"{booking_data.booking_date} at {booking_data.booking_time}."
                )
                append_to_history(redis_client, session_id, user_message, reply)
                return reply

    reply = getattr(response.message, "content", None) or "I could not generate a response."
    append_to_history(redis_client, session_id, user_message, reply)
    return reply