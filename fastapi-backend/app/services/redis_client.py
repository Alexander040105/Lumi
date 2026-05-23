import os

from redis.asyncio import Redis


def get_redis() -> Redis:
    redis_url = os.getenv("UPSTASH_REDIS_URL")
    return Redis.from_url(redis_url, decode_responses=True)
