from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_redis import RedisChatMessageHistory

def get_chat_history(session_id:str, client) -> BaseChatMessageHistory:
    return RedisChatMessageHistory(session_id=session_id, redis_client=client)

def message_whistory(chain):
    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history=get_chat_history,
        input_message_key="question",
        history_message_key="history",
    )

def append_to_history(client, session_id:str, user_message:str, agent_response:str) -> None:
    history = RedisChatMessageHistory(
        session_id = session_id,
        redis_client = client
    )

    history.add_user_message(user_message)
    history.add_ai_message(agent_response)
