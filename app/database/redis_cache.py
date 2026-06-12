from redis import Redis

from config import settings


# initialize redis client lazily to avoid import-time errors in tests
redis_client: Redis | None = None

def get_redis_client() -> Redis:
	global redis_client
	if redis_client is None:
		redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
	return redis_client