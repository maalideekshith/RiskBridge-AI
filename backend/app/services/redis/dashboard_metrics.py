import json

from app.services.redis.client import redis_client


DASHBOARD_METRICS_TTL = 300


def _dashboard_key(merchant_id: int) -> str:
    return f"riskbridge:dashboard:merchant:{merchant_id}"


def cache_dashboard_metrics(
    merchant_id: int,
    metrics: dict,
) -> None:
    key = _dashboard_key(merchant_id)

    redis_client.setex(
        key,
        DASHBOARD_METRICS_TTL,
        json.dumps(metrics),
    )


def get_dashboard_metrics(
    merchant_id: int,
) -> dict | None:
    key = _dashboard_key(merchant_id)

    value = redis_client.get(key)

    if value is None:
        return None

    return json.loads(value)


def clear_dashboard_metrics(
    merchant_id: int,
) -> None:
    key = _dashboard_key(merchant_id)

    redis_client.delete(key)