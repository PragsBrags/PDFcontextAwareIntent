import ollama
from typing import List, Dict, Any
from services.memory import get_chat_history, message_whistory, append_to_history
from services.rag import search_relevant_chunks, qdrant_client

from pydantic import BaseModel

class BookingExtractor(BaseModel):
    name: str
    email: str
    date: str
    time: str

def book_interview(name: str, email: str, date: str, time: str) -> str:
    """
    Call this tool ONLY when the user explicitly wants to book, schedule, or reserve an interview slot,
    AND they have provided all required information (name, email, date, time).
    Do NOT call this tool if any of these pieces of information are missing.
    """
    # This string acts as an instructional docstring that the LLM uses for intent detection
    return "Intent Captured: Processing database transaction."


async def handle_agent_turn(session_id: str, user_message: str, db_session: Session) -> str:
    """
    The orchestrator service that evaluates user intent on EVERY turn, managing
    multi-turn conversational context, vector searches, and system actions.
    """
    chat_history: List[Dict[str, str]] = await message_whistory(session_id)
    
    context_str = "Corporate Policy: Interviews are held Mon-Fri. Candidates must reserve standard slots."

    system_prompt = {
        "role": "system",
        "content": (
            "You are an intelligent HR Assistant. Your goals are to answer user inquiries using "
            f"the provided Document Context below, or guide them through booking an interview.\n\n"
            f"DOCUMENT CONTEXT:\n{context_str}\n\n"
            "CRITICAL: If the user wants to book an interview but hasn't provided their name, email, "
            "date, or time, do NOT call the tool. Instead, ask them conversationally for the missing details."
        )
    }

    messages = [system_prompt] + chat_history + [{"role": "user", "content": user_message}]

    response = ollama.chat(
        model="llama3.1",  # tool-use capable model
        messages=messages,
        tools=[book_interview], 
    )

    if response.message.tool_calls:
        for tool in response.message.tool_calls:
            if tool.function.name == "book_interview":
                # Intent Detected: Execute Booking Pipeline
                try:
                    extracted_data = BookingExtractor(**tool.function.arguments)
                    
                    # Store inside your traditional SQL Database
                    new_booking = InterviewBooking(
                        name=extracted_data.name,
                        email=extracted_data.email,
                        booking_date=extracted_data.date,
                        time=extracted_data.time
                    )
                    db_session.add(new_booking)
                    db_session.commit()
                    db_session.refresh(new_booking)
                    
                    bot_reply = f"Thank you! Your interview has been securely scheduled for {extracted_data.date} at {extracted_data.time}."
                except Exception as e:
                    bot_reply = "I ran into an issue finalizing your booking. Could you verify the details?"
                
                # Commit conversational turn to Redis memory and return response
                await append_to_history(client, session_id, user_message, bot_reply)
                return bot_reply

    # Intent Detected: Regular Conversation or Missing Slot Request
    bot_reply = response.message.content
    await append_to_history(client, session_id, user_message, bot_reply)
    return bot_reply


