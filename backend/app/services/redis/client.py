import redis


REDIS_URL = "redis://localhost:6379/0"


redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)


def check_redis_connection() -> bool:
    try:
        return redis_client.ping()
    except redis.RedisError:
        return False