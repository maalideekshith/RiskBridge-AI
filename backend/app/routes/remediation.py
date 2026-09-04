from fastapi import APIRouter, HTTPException

from app.schemas.remediation import (
    HighestImpactRequest,
    HighestImpactResponse,
    RemediationPlanResponse,
    PrioritizedRemediationPlanResponse,
    RiskReductionResponse,
    RemediationStatusResponse,
)
from app.services.remediation import (
    identify_highest_impact_problem,
    generate_remediation_plan,
    prioritize_remediation_actions,
    estimate_risk_reduction,
    track_remediation_status,
)


router = APIRouter(
    prefix="/remediation",
    tags=["Remediation Agent"],
)


@router.post(
    "/highest-impact",
    response_model=HighestImpactResponse,
    summary="Identify Highest Impact Problem",
    description=(
        "Identifies the highest-impact risk problem from "
        "projected What-If or risk simulation results."
    ),
)
def identify_highest_impact(
    request: HighestImpactRequest,
):
    """
    Day 6 Phase 3 — Step 1.
    """

    try:
        impact = request.impact

        return identify_highest_impact_problem(
            impact
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "/plan",
    response_model=RemediationPlanResponse,
    summary="Generate Remediation Plan",
    description=(
        "Generates a practical remediation plan "
        "for the highest-impact risk problem."
    ),
)
def generate_plan(
    highest_impact: HighestImpactResponse,
):
    """
    Day 6 Phase 3 — Step 2.
    """

    try:
        return generate_remediation_plan(
            highest_impact.model_dump()
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "/prioritize",
    response_model=PrioritizedRemediationPlanResponse,
    summary="Prioritize Remediation Actions",
    description=(
        "Prioritizes remediation actions based on "
        "the identified highest-impact risk problem."
    ),
)
def prioritize_actions(
    remediation_plan: RemediationPlanResponse,
):
    """
    Day 6 Phase 3 — Step 3.
    """

    try:
        return prioritize_remediation_actions(
            remediation_plan.model_dump()
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.post(
    "/risk-reduction",
    response_model=RiskReductionResponse,
    summary="Estimate Risk Reduction",
    description=(
        "Estimates the potential risk reduction from "
        "prioritized remediation actions."
    ),
)
def estimate_risk_reduction_endpoint(
    prioritized_plan: PrioritizedRemediationPlanResponse,
):
    """
    Day 6 Phase 3 — Step 4.
    """

    try:
        return estimate_risk_reduction(
            prioritized_plan.model_dump()
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "/status",
    response_model=RemediationStatusResponse,
    summary="Track Remediation Status",
    description=(
        "Tracks remediation progress, completed actions, "
        "completion percentage, and current remediation status."
    ),
)
def track_status(
    risk_reduction_plan: RiskReductionResponse,
    completed_actions: int = 0,
    status: str = "pending",
):
    """
    Day 6 Phase 3 — Step 5.
    """

    try:
        return track_remediation_status(
            risk_reduction_plan.model_dump(),
            completed_actions=completed_actions,
            status=status,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc