def record_risk_decision(
    case: dict,
    decision: str,
) -> dict:
    """
    Record a risk decision for a risk-review case.
    """

    if not case:
        raise ValueError(
            "case cannot be empty"
        )

    required_fields = [
        "merchant_id",
        "risk_reason",
        "status",
    ]

    for field in required_fields:
        if field not in case:
            raise ValueError(
                f"case is missing required field: {field}"
            )

    if not isinstance(decision, str):
        raise ValueError(
            "decision must be a string"
        )

    decision = decision.strip().lower()

    allowed_decisions = [
        "approve",
        "reject",
        "monitor",
        "escalate",
    ]

    if decision not in allowed_decisions:
        raise ValueError(
            "invalid risk decision"
        )

    return {
        "merchant_id": case["merchant_id"],
        "risk_reason": case["risk_reason"],
        "decision": decision,
        "status": "decision_recorded",
    }
def record_ai_recommendation(
    case: dict,
    recommendation: str,
) -> dict:
    """
    Record an AI-generated recommendation for a
    risk-review case.
    """

    if not case:
        raise ValueError(
            "case cannot be empty"
        )

    required_fields = [
        "merchant_id",
        "risk_reason",
        "status",
    ]

    for field in required_fields:
        if field not in case:
            raise ValueError(
                f"case is missing required field: {field}"
            )

    if not isinstance(recommendation, str):
        raise ValueError(
            "recommendation must be a string"
        )

    if not recommendation.strip():
        raise ValueError(
            "recommendation cannot be empty"
        )

    return {
        "merchant_id": case["merchant_id"],
        "risk_reason": case["risk_reason"],
        "recommendation": recommendation.strip(),
        "status": "ai_recommendation_recorded",
    }
def record_merchant_action(
    case: dict,
    action: str,
) -> dict:
    """
    Record an action taken by the merchant for a
    risk-review case.
    """

    if not case:
        raise ValueError(
            "case cannot be empty"
        )

    required_fields = [
        "merchant_id",
        "risk_reason",
        "status",
    ]

    for field in required_fields:
        if field not in case:
            raise ValueError(
                f"case is missing required field: {field}"
            )

    if not isinstance(action, str):
        raise ValueError(
            "action must be a string"
        )

    if not action.strip():
        raise ValueError(
            "action cannot be empty"
        )

    return {
        "merchant_id": case["merchant_id"],
        "risk_reason": case["risk_reason"],
        "action": action.strip(),
        "status": "merchant_action_recorded",
    }
def record_case_change(
    case: dict,
    change: str,
) -> dict:
    """
    Record a change made to a risk-review case.
    """

    if not case:
        raise ValueError(
            "case cannot be empty"
        )

    required_fields = [
        "merchant_id",
        "risk_reason",
        "status",
    ]

    for field in required_fields:
        if field not in case:
            raise ValueError(
                f"case is missing required field: {field}"
            )

    if not isinstance(change, str):
        raise ValueError(
            "change must be a string"
        )

    if not change.strip():
        raise ValueError(
            "change cannot be empty"
        )

    return {
        "merchant_id": case["merchant_id"],
        "risk_reason": case["risk_reason"],
        "case_status": case["status"],
        "change": change.strip(),
        "status": "case_change_recorded",
    }
def create_audit_timeline(
    case: dict,
    events: list,
) -> dict:
    """
    Create an audit timeline containing all recorded
    events for a risk-review case.
    """

    if not case:
        raise ValueError(
            "case cannot be empty"
        )

    required_fields = [
        "merchant_id",
        "risk_reason",
        "status",
    ]

    for field in required_fields:
        if field not in case:
            raise ValueError(
                f"case is missing required field: {field}"
            )

    if not isinstance(events, list):
        raise ValueError(
            "events must be a list"
        )

    if not events:
        raise ValueError(
            "events cannot be empty"
        )

    for event in events:
        if not isinstance(event, dict):
            raise ValueError(
                "Each audit event must be a dictionary"
            )

    return {
        "merchant_id": case["merchant_id"],
        "risk_reason": case["risk_reason"],
        "case_status": case["status"],
        "timeline": events.copy(),
        "event_count": len(events),
        "status": "audit_timeline_created",
    }