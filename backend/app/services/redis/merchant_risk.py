import json

from app.services.redis.client import redis_client


RISK_PROFILE_TTL = 300


def _get_key(merchant_id: int) -> str:
    return f"riskbridge:risk_profile:merchant:{merchant_id}"


def cache_merchant_risk_profile(
    merchant_id: int,
    profile: dict,
) -> None:
    key = _get_key(merchant_id)

    redis_client.setex(
        key,
        RISK_PROFILE_TTL,
        json.dumps(profile),
    )


def get_merchant_risk_profile(
    merchant_id: int,
) -> dict | None:
    key = _get_key(merchant_id)

    value = redis_client.get(key)

    if value is None:
        return None

    return json.loads(value)


def clear_merchant_risk_profile(
    merchant_id: int,
) -> None:
    key = _get_key(merchant_id)

    redis_client.delete(key)