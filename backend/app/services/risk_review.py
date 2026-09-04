def create_risk_review_case(
    merchant_id: int,
    risk_reason: str,
) -> dict:
    """
    Create a new risk-review case for a merchant.
    """

    if merchant_id <= 0:
        raise ValueError(
            "merchant_id must be greater than zero"
        )

    if not risk_reason or not risk_reason.strip():
        raise ValueError(
            "risk_reason cannot be empty"
        )

    return {
        "merchant_id": merchant_id,
        "risk_reason": risk_reason.strip(),
        "status": "open",
    }
def assign_risk_reason(
    case: dict,
    risk_reason: str,
) -> dict:
    """
    Assign a risk reason to an existing risk-review case.
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

    if not isinstance(risk_reason, str):
        raise ValueError(
            "risk_reason must be a string"
        )

    if not risk_reason.strip():
        raise ValueError(
            "risk_reason cannot be empty"
        )

    updated_case = case.copy()

    updated_case["risk_reason"] = risk_reason.strip()

    return updated_case
def attach_risk_assessment(
    case: dict,
    risk_assessment: dict,
) -> dict:
    """
    Attach a risk assessment to an existing
    risk-review case.
    """

    if not case:
        raise ValueError(
            "case cannot be empty"
        )

    required_case_fields = [
        "merchant_id",
        "risk_reason",
        "status",
    ]

    for field in required_case_fields:
        if field not in case:
            raise ValueError(
                f"case is missing required field: {field}"
            )

    if not risk_assessment:
        raise ValueError(
            "risk_assessment cannot be empty"
        )

    if not isinstance(risk_assessment, dict):
        raise ValueError(
            "risk_assessment must be a dictionary"
        )

    return {
        "merchant_id": case["merchant_id"],
        "risk_reason": case["risk_reason"],
        "status": case["status"],
        "risk_assessment": risk_assessment,
    }
def update_case_status(
    case: dict,
    status: str,
) -> dict:
    """
    Update the status of a risk-review case.
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

    if not isinstance(status, str):
        raise ValueError(
            "status must be a string"
        )

    status = status.strip().lower()

    allowed_statuses = [
        "open",
        "in_progress",
        "resolved",
        "closed",
    ]

    if status not in allowed_statuses:
        raise ValueError(
            "invalid case status"
        )

    updated_case = case.copy()
    updated_case["status"] = status

    return updated_case
def add_case_timeline_event(
    case: dict,
    event: str,
) -> dict:
    """
    Add an event to the timeline of a risk-review case.
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

    if not isinstance(event, str):
        raise ValueError(
            "event must be a string"
        )

    if not event.strip():
        raise ValueError(
            "event cannot be empty"
        )

    updated_case = case.copy()

    existing_timeline = updated_case.get(
        "timeline",
        [],
    )

    if not isinstance(existing_timeline, list):
        raise ValueError(
            "case timeline must be a list"
        )

    timeline = existing_timeline.copy()

    timeline.append(
        {
            "event": event.strip(),
            "status": updated_case["status"],
        }
    )

    updated_case["timeline"] = timeline
    updated_case["timeline_count"] = len(timeline)

    return updated_case