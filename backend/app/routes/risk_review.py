from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.services.audit_log import create_audit_log
from app.services.risk_review import (
    create_risk_review_case,
    assign_risk_reason,
    attach_risk_assessment,
    update_case_status,
    add_case_timeline_event,
)


router = APIRouter(
    prefix="/risk-review",
    tags=["Risk Review"],
)


@router.post("/cases")
def create_case(
    merchant_id: int,
    risk_reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new risk-review case.
    """

    merchant = current_user.merchant

    if merchant is None:
        raise HTTPException(
            status_code=400,
            detail="No merchant profile found for this user",
        )

    if merchant.id != merchant_id:
        raise HTTPException(
            status_code=403,
            detail="You can only create cases for your own merchant",
        )

    case = create_risk_review_case(
        merchant_id,
        risk_reason,
    )

    create_audit_log(
        db=db,
        merchant_id=merchant.id,
        user_id=current_user.id,
        action="RISK_REVIEW_CASE_CREATED",
        entity_type="risk_review_case",
        entity_id=None,
        description=(
            f"Risk review case created: "
            f"{risk_reason.strip()}"
        ),
    )

    return case

@router.post("/cases/reason")
def assign_case_reason(
    case: dict,
    risk_reason: str,
):
    """
    Assign a risk reason to an existing case.
    """

    return assign_risk_reason(
        case,
        risk_reason,
    )


@router.post("/cases/assessment")
def attach_case_assessment(
    case: dict,
    risk_assessment: dict,
):
    """
    Attach a risk assessment to an existing case.
    """

    return attach_risk_assessment(
        case,
        risk_assessment,
    )


@router.patch("/cases/status")
def change_case_status(
    case: dict,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the status of a risk-review case.
    """

    merchant = current_user.merchant

    if merchant is None:
        raise HTTPException(
            status_code=400,
            detail="No merchant profile found for this user",
        )

    if case.get("merchant_id") != merchant.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update cases for your own merchant",
        )

    old_status = case.get("status")

    updated_case = update_case_status(
        case,
        status,
    )

    new_status = updated_case["status"]

    if old_status != new_status:
        create_audit_log(
            db=db,
            merchant_id=merchant.id,
            user_id=current_user.id,
            action="RISK_REVIEW_CASE_STATUS_CHANGED",
            entity_type="risk_review_case",
            entity_id=None,
            description=(
                f"Risk review case status changed "
                f"from {old_status} to {new_status}"
            ),
        )

    return updated_case


@router.post("/cases/timeline")
def add_case_timeline(
    case: dict,
    event: str,
):
    """
    Add an event to the risk-review case timeline.
    """

    return add_case_timeline_event(
        case,
        event,
    )