
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.audit_log import create_audit_log
from app.services.ai.context import (
    gather_merchant_profile,
    gather_transaction_history,
    gather_refund_history,
    gather_dispute_history,
    gather_risk_signals,
)
from app.schemas.ai_context import (
    MerchantProfileResponse,
    TransactionHistoryItem,
    RefundHistoryItem,
    DisputeHistoryItem,
    RiskSignalItem,
)
from app.services.ai.prompt import (
    build_risk_investigation_prompt,
)

from app.services.ai.agent import (
    generate_risk_investigation,
)
from app.services.ai.explanation import (
    explain_why_risk_increased,
    explain_important_risk_signals,
    explain_risk_severity,
    explain_supporting_evidence,
    explain_confidence_level,
)

from app.services.ai.recommendation import (
    recommend_immediate_actions,
    recommend_preventive_actions,
    prioritize_actions,
    explain_expected_impact,
    explain_merchant_friendly,
)

from app.services.ai.schemas import (
    RiskInvestigationResponse,
    RiskRecommendationResponse,
)

router = APIRouter(
    prefix="/risk/ai/context",
    tags=["AI Risk Investigation"],
)


@router.get(
    "/merchant/{merchant_id}",
    response_model=MerchantProfileResponse,
    summary="Gather Merchant Profile",
)
def get_merchant_profile(
    merchant_id: int,
    db: Session = Depends(get_db),
):
    try:
        return gather_merchant_profile(
            db,
            merchant_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get(
    "/transactions/{merchant_id}",
    response_model=list[TransactionHistoryItem],
    summary="Gather Transaction History",
)
def get_transaction_history(
    merchant_id: int,
    db: Session = Depends(get_db),
):
    return gather_transaction_history(
        db,
        merchant_id,
    )


@router.get(
    "/refunds/{merchant_id}",
    response_model=list[RefundHistoryItem],
    summary="Gather Refund History",
)
def get_refund_history(
    merchant_id: int,
    db: Session = Depends(get_db),
):
    return gather_refund_history(
        db,
        merchant_id,
    )


@router.get(
    "/disputes/{merchant_id}",
    response_model=list[DisputeHistoryItem],
    summary="Gather Dispute History",
)
def get_dispute_history(
    merchant_id: int,
    db: Session = Depends(get_db),
):
    return gather_dispute_history(
        db,
        merchant_id,
    )


@router.get(
    "/risk-signals/{merchant_id}",
    response_model=list[RiskSignalItem],
    summary="Gather Risk Signals",
)
def get_risk_signals(
    merchant_id: int,
    db: Session = Depends(get_db),
):
    return gather_risk_signals(
        db,
        merchant_id,
    )
@router.post(
    "/investigate/{merchant_id}",
    response_model=RiskInvestigationResponse,
    summary="Generate AI Risk Investigation",
    description=(
        "Runs the complete AI Risk Investigation Agent flow. "
        "Gathers merchant profile, transaction history, refund "
        "history, dispute history, and risk signals; builds a "
        "structured risk prompt; sends the context to the LLM; "
        "generates the investigation; and validates the structured "
        "AI response."
    ),
)
def investigate_risk(
    merchant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Day 5 Phase 2 — Risk Investigation Agent.
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
            detail="You can only investigate your own merchant",
        )

    try:
        # Step 1 — Gather AI context
        merchant_profile = gather_merchant_profile(
            db,
            merchant_id,
        )

        transaction_history = gather_transaction_history(
            db,
            merchant_id,
        )

        refund_history = gather_refund_history(
            db,
            merchant_id,
        )

        dispute_history = gather_dispute_history(
            db,
            merchant_id,
        )

        risk_signals = gather_risk_signals(
            db,
            merchant_id,
        )

        # Step 2 — Build structured risk prompt
        prompt = build_risk_investigation_prompt(
            merchant_profile=merchant_profile,
            transaction_history=transaction_history,
            refund_history=refund_history,
            dispute_history=dispute_history,
            risk_signals=risk_signals,
        )

        # Steps 3, 4, 5
        # Send context to LLM
        # Generate investigation
        # Validate structured response
        investigation = generate_risk_investigation(
            prompt,
        )

        create_audit_log(
            db=db,
            merchant_id=merchant.id,
            user_id=current_user.id,
            action="AI_RISK_INVESTIGATION_GENERATED",
            entity_type="merchant",
            entity_id=merchant.id,
            description=(
                f"AI risk investigation generated for merchant "
                f"{merchant.id}"
            ),
        )

        return investigation

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

@router.post(
    "/explain/{merchant_id}",
    response_model=RiskInvestigationResponse,
    summary="Generate AI Risk Explanation",
    description=(
        "Generates a structured AI explanation of merchant risk. "
        "Explains why risk increased, identifies the most important "
        "risk signals, determines risk severity, provides supporting "
        "evidence, and reports the confidence level."
    ),
)
def explain_risk(
    merchant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Day 5 Phase 3 — AI Explanation.
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
            detail="You can only explain risk for your own merchant",
        )
    try:
        # Reuse the verified Phase 1 AI context engine
        merchant_profile = gather_merchant_profile(
            db,
            merchant_id,
        )

        transaction_history = gather_transaction_history(
            db,
            merchant_id,
        )

        refund_history = gather_refund_history(
            db,
            merchant_id,
        )

        dispute_history = gather_dispute_history(
            db,
            merchant_id,
        )

        risk_signals = gather_risk_signals(
            db,
            merchant_id,
        )

        # Reuse the verified Phase 2 structured prompt
        prompt = build_risk_investigation_prompt(
            merchant_profile=merchant_profile,
            transaction_history=transaction_history,
            refund_history=refund_history,
            dispute_history=dispute_history,
            risk_signals=risk_signals,
        )

        # Reuse the verified Phase 2 AI investigation
        investigation = generate_risk_investigation(
            prompt,
        )

        # Phase 3 — execute all five explanation steps
        explain_why_risk_increased(investigation)

        explain_important_risk_signals(
            investigation,
        )

        explain_risk_severity(
            investigation,
        )

        explain_supporting_evidence(
            investigation,
        )

        explain_confidence_level(
            investigation,
        )

        create_audit_log(
            db=db,
            merchant_id=merchant.id,
            user_id=current_user.id,
            action="AI_RISK_EXPLANATION_GENERATED",
            entity_type="merchant",
            entity_id=merchant.id,
            description=(
                f"AI risk explanation generated for merchant "
                f"{merchant.id}"
            ),
        )

        return investigation

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc
@router.post(
    "/recommend/{merchant_id}",
    response_model=RiskRecommendationResponse,
    summary="Generate AI Risk Recommendations",
    description=(
        "Generates structured risk recommendations from the AI risk "
        "investigation. Produces immediate actions, preventive actions, "
        "priority order, expected impact, and a merchant-friendly "
        "explanation."
    ),
)
def recommend_risk_actions(
    merchant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Day 5 Phase 4 — AI Recommendations.
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
            detail="You can only generate recommendations for your own merchant",
        )
    try:
        # Reuse the verified Phase 1 AI context engine
        merchant_profile = gather_merchant_profile(
            db,
            merchant_id,
        )

        transaction_history = gather_transaction_history(
            db,
            merchant_id,
        )

        refund_history = gather_refund_history(
            db,
            merchant_id,
        )

        dispute_history = gather_dispute_history(
            db,
            merchant_id,
        )

        risk_signals = gather_risk_signals(
            db,
            merchant_id,
        )

        # Reuse the verified Phase 2 structured prompt
        prompt = build_risk_investigation_prompt(
            merchant_profile=merchant_profile,
            transaction_history=transaction_history,
            refund_history=refund_history,
            dispute_history=dispute_history,
            risk_signals=risk_signals,
        )

        # Reuse the verified Phase 2 AI investigation
        investigation = generate_risk_investigation(
            prompt,
        )

        # Phase 4 — generate recommendations
        immediate_actions = recommend_immediate_actions(
            investigation,
        )

        preventive_actions = recommend_preventive_actions(
            investigation,
        )

        priority_order = prioritize_actions(
            immediate_actions,
            preventive_actions,
        )

        expected_impact = explain_expected_impact(
            priority_order,
        )

        # Execute Phase 4 Step 5 validation/generation.
        # The current response schema does not contain a separate
        # merchant-friendly explanation field, so this is intentionally
        # not returned in the API response.
        explain_merchant_friendly(
            priority_order,
            expected_impact,
        )

        recommendation = RiskRecommendationResponse(
            immediate_actions=immediate_actions,
            preventive_actions=preventive_actions,
            priority_order=priority_order,
            expected_impact=expected_impact,
        )

        create_audit_log(
            db=db,
            merchant_id=merchant.id,
            user_id=current_user.id,
            action="AI_RISK_RECOMMENDATION_GENERATED",
            entity_type="merchant",
            entity_id=merchant.id,
            description=(
                f"AI risk recommendation generated for merchant "
                f"{merchant.id}"
            ),
        )

        return recommendation

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc