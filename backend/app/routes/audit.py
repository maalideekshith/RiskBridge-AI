from fastapi import APIRouter

from app.services.audit import (
    record_risk_decision,
    record_ai_recommendation,
    record_merchant_action,
    record_case_change,
    create_audit_timeline,
)


router = APIRouter(
    prefix="/risk-review",
    tags=["Audit"],
)


@router.post("/audit/risk-decision")
def create_risk_decision(
    case: dict,
    decision: str,
):
    """
    Record a risk decision for a risk-review case.
    """

    return record_risk_decision(
        case,
        decision,
    )


@router.post("/audit/ai-recommendation")
def create_ai_recommendation(
    case: dict,
    recommendation: str,
):
    """
    Record an AI recommendation for a risk-review case.
    """

    return record_ai_recommendation(
        case,
        recommendation,
    )


@router.post("/audit/merchant-action")
def create_merchant_action(
    case: dict,
    action: str,
):
    """
    Record a merchant action for a risk-review case.
    """

    return record_merchant_action(
        case,
        action,
    )


@router.post("/audit/case-change")
def create_case_change(
    case: dict,
    change: str,
):
    """
    Record a change made to a risk-review case.
    """

    return record_case_change(
        case,
        change,
    )


@router.post("/audit/timeline")
def create_case_audit_timeline(
    case: dict,
    events: list[dict],
):
    """
    Create an audit timeline for a risk-review case.
    """

    return create_audit_timeline(
        case,
        events,
    )