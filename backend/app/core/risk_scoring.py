from app.core.risk_weights import (
    RISK_SIGNAL_WEIGHTS,
    TOTAL_WEIGHT,
)


def calculate_risk_score(
    signals: dict[str, bool],
) -> dict:
    raw_score = 0

    signal_scores = {}

    for signal_name, weight in RISK_SIGNAL_WEIGHTS.items():
        detected = signals.get(signal_name, False)

        contribution = weight if detected else 0

        raw_score += contribution

        signal_scores[signal_name] = {
            "detected": detected,
            "weight": weight,
            "contribution": contribution,
        }

    if TOTAL_WEIGHT == 0:
        score = 0
    else:
        score = round(
            (raw_score / TOTAL_WEIGHT) * 100
        )

    score = max(0, min(100, score))

    return {
        "score": score,
        "raw_score": raw_score,
        "max_score": TOTAL_WEIGHT,
        "signals": signal_scores,
    }