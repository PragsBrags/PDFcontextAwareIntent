import json
from redis import Redis
from typing import List, Dict


def get_history(client: Redis, session_id: str) -> List[Dict[str, str]]:
    raw_messages = client.lrange(f"chat:{session_id}", 0, -1)
    return [json.loads(message) for message in raw_messages]


def append_to_history(
    client: Redis,
    session_id: str,
    user_message: str,
    assistant_message: str,
) -> None:
    key = f"chat:{session_id}"
    client.rpush(key, json.dumps({"role": "user", "content": user_message}))
    client.rpush(key, json.dumps({"role": "assistant", "content": assistant_message}))
    client.expire(key, 60 * 60 * 24)
