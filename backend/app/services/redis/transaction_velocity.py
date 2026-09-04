import time

from app.services.redis.client import redis_client


VELOCITY_KEY_PREFIX = "riskbridge:velocity:merchant:"
DEFAULT_WINDOW_SECONDS = 60


def _get_velocity_key(merchant_id: int) -> str:
    return f"{VELOCITY_KEY_PREFIX}{merchant_id}"


def record_transaction(
    merchant_id: int,
    payment_id: int,
) -> None:
    key = _get_velocity_key(merchant_id)

    now = time.time()

    redis_client.zadd(
        key,
        {
            str(payment_id): now,
        },
    )

    redis_client.expire(
        key,
        DEFAULT_WINDOW_SECONDS * 2,
    )


def get_transaction_velocity(
    merchant_id: int,
    window_seconds: int = DEFAULT_WINDOW_SECONDS,
) -> int:
    key = _get_velocity_key(merchant_id)

    now = time.time()
    cutoff = now - window_seconds

    redis_client.zremrangebyscore(
        key,
        0,
        cutoff,
    )

    return redis_client.zcard(key)


def clear_transaction_velocity(
    merchant_id: int,
) -> None:
    key = _get_velocity_key(merchant_id)
    redis_client.delete(key)