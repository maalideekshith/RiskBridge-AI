import json
from typing import Any

from app.services.redis.client import redis_client


RECENT_TRANSACTIONS_LIMIT = 10


def store_recent_transaction(
    merchant_id: int,
    transaction: dict[str, Any],
) -> None:
    """
    Store a recent transaction for a merchant in Redis.

    Only the latest RECENT_TRANSACTIONS_LIMIT transactions
    are retained.
    """

    key = f"riskbridge:transactions:merchant:{merchant_id}"

    transaction_json = json.dumps(
        transaction,
        default=str,
    )

    redis_client.lpush(
        key,
        transaction_json,
    )

    redis_client.ltrim(
        key,
        0,
        RECENT_TRANSACTIONS_LIMIT - 1,
    )


def get_recent_transactions(
    merchant_id: int,
) -> list[dict[str, Any]]:
    """
    Return recent transactions for a merchant.
    """

    key = f"riskbridge:transactions:merchant:{merchant_id}"

    transactions = redis_client.lrange(
        key,
        0,
        RECENT_TRANSACTIONS_LIMIT - 1,
    )

    return [
        json.loads(transaction)
        for transaction in transactions
    ]


def clear_recent_transactions(
    merchant_id: int,
) -> None:
    """
    Remove cached recent transactions for a merchant.
    """

    key = f"riskbridge:transactions:merchant:{merchant_id}"

    redis_client.delete(key)