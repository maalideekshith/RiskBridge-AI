def categorize_risk(score: int) -> str:
    if score <= 24:
        return "Low"

    if score <= 49:
        return "Medium"

    if score <= 74:
        return "High"

    return "Critical"