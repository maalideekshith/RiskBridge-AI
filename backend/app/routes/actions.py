from fastapi import APIRouter, HTTPException

from app.schemas.actions import (
    CreateActionRequest,
    ActionResponse,
    MarkActionPendingRequest,
    MarkActionPendingResponse,
    MarkActionCompletedRequest,
    MarkActionCompletedResponse,
    CalculateUpdatedRiskRequest,
    CalculateUpdatedRiskResponse,
    MaintainActionHistoryRequest,
    MaintainActionHistoryResponse,
)
from app.services.actions import (
    create_action,
    mark_action_pending,
    mark_action_completed,
    calculate_updated_risk,
    maintain_action_history,
)

router = APIRouter(
    prefix="/actions",
    tags=["Action System"],
)


@router.post(
    "/",
    response_model=ActionResponse,
    summary="Create Action",
    description=(
        "Creates a remediation action from a "
        "Phase 3 prioritized remediation recommendation."
    ),
)
def create_action_route(
    request: CreateActionRequest,
):
    """
    Day 6 Phase 4 — Step 1.
    """

    try:
        return create_action(
            problem=request.problem,
            action=request.action,
            priority=request.priority,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.post(
    "/pending",
    response_model=MarkActionPendingResponse,
    summary="Mark Action Pending",
    description=(
        "Marks an existing remediation action as pending."
    ),
)
def mark_pending(
    request: MarkActionPendingRequest,
):
    """
    Day 6 Phase 4 — Step 2.
    """

    try:
        return mark_action_pending(
            request.model_dump()
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.post(
    "/completed",
    response_model=MarkActionCompletedResponse,
    summary="Mark Action Completed",
    description=(
        "Marks an existing remediation action as completed."
    ),
)
def mark_completed(
    request: MarkActionCompletedRequest,
):
    """
    Day 6 Phase 4 — Step 3.
    """

    try:
        return mark_action_completed(
            request.model_dump()
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.post(
    "/updated-risk",
    response_model=CalculateUpdatedRiskResponse,
    summary="Calculate Updated Risk",
    description=(
        "Calculates the updated risk after completed "
        "remediation actions."
    ),
)
def calculate_updated_risk_route(
    request: CalculateUpdatedRiskRequest,
):
    """
    Day 6 Phase 4 — Step 4.
    """

    try:
        return calculate_updated_risk(
            remediation_result=request.remediation_result,
            completed_actions=request.completed_actions,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.post(
    "/history",
    response_model=MaintainActionHistoryResponse,
    summary="Maintain Action History",
    description=(
        "Maintains the history of remediation action "
        "state transitions."
    ),
)
def maintain_history(
    request: MaintainActionHistoryRequest,
):
    """
    Day 6 Phase 4 — Step 5.
    """

    try:
        return maintain_action_history(
            action=request.action,
            history=request.history,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc