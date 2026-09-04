from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.services.audit_log import create_audit_log

from app.services.evidence_agent import (
    analyze_case,
    identify_missing_evidence,
    generate_evidence_checklist,
    generate_case_summary,
    generate_recommended_response,
)


router = APIRouter(
    prefix="/risk-review",
    tags=["AI Evidence Agent"],
)


@router.post("/ai/analyze")
def analyze_risk_review_case(
    case: dict,
    evidence: dict,
):
    """
    Analyze a risk-review case using collected evidence.
    """

    return analyze_case(
        case,
        evidence,
    )


@router.post("/ai/missing-evidence")
def identify_case_missing_evidence(
    evidence: dict,
):
    """
    Identify missing evidence for a risk-review case.
    """

    return identify_missing_evidence(
        evidence,
    )


@router.post("/ai/checklist")
def generate_case_evidence_checklist(
    missing: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate an evidence collection checklist.
    """

    merchant = current_user.merchant

    if merchant is None:
        raise HTTPException(
            status_code=400,
            detail="No merchant profile found for this user",
        )

    checklist = generate_evidence_checklist(
        missing,
    )

    missing_items = missing.get("missing_evidence", [])

    create_audit_log(
        db=db,
        merchant_id=merchant.id,
        user_id=current_user.id,
        action="AI_EVIDENCE_CHECKLIST_GENERATED",
        entity_type="risk_review_case",
        entity_id=None,
        description=(
            f"AI evidence checklist generated with "
            f"{len(missing_items)} missing evidence item(s)"
        ),
    )

    return checklist


@router.post("/ai/summary")
def generate_case_summary_api(
    analysis: dict,
    evidence: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a summary of the risk-review case.
    """

    merchant = current_user.merchant

    if merchant is None:
        raise HTTPException(
            status_code=400,
            detail="No merchant profile found for this user",
        )

    if analysis.get("merchant_id") != merchant.id:
        raise HTTPException(
            status_code=403,
            detail="You can only generate summaries for your own merchant",
        )

    summary = generate_case_summary(
        analysis,
        evidence,
    )

    create_audit_log(
        db=db,
        merchant_id=merchant.id,
        user_id=current_user.id,
        action="AI_CASE_SUMMARY_GENERATED",
        entity_type="risk_review_case",
        entity_id=None,
        description=(
            f"AI case summary generated for "
            f"risk review case: {analysis.get('risk_reason')}"
        ),
    )

    return summary


@router.post("/ai/recommendation")
def generate_case_recommendation(
    analysis: dict,
    summary: dict,
    checklist: dict,
):
    """
    Generate a recommended response for the risk-review case.
    """

    return generate_recommended_response(
        analysis,
        summary,
        checklist,
    )