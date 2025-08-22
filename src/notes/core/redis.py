from redis.asyncio import from_url
from notes.core.config import settings

_client = None

async def get_redis():
    global _client
    if _client is None:
        url = getattr(settings, "REDIS_URL", "redis://redis:6379/0")
        _client = from_url(url, decode_responses=True)
    return _client
