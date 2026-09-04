
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.what_if import (
    WhatIfRequest,
    WhatIfInterpretation,
    WhatIfExplanationRequest,
    WhatIfRecommendationRequest,
)
from app.services.what_if import (
    accept_what_if_scenario,
    interpret_what_if_scenario,
    calculate_what_if_impact,
    explain_what_if_result,
    recommend_what_if_action,
)
router = APIRouter(
    prefix="/what-if",
    tags=["What If"],
)


@router.post("/")
def create_what_if_scenario(
    request: WhatIfRequest,
):
    """
    Accept a natural-language What-If risk scenario.
    """

    return accept_what_if_scenario(
        request.scenario
    )
@router.post("/interpret")
def interpret_what_if(
    request: WhatIfRequest,
):
    """
    Phase 2 Step 2 — Interpret a natural-language
    What-If risk scenario using AI.
    """

    return interpret_what_if_scenario(
        request.scenario
    )
@router.post("/impact/{merchant_id}")
def calculate_what_if(
    merchant_id: int,
    interpretation: WhatIfInterpretation,
    db: Session = Depends(get_db),
):
    """
    Phase 2 Step 3 — Calculate the projected risk impact
    using the deterministic RiskBridge risk engine.
    """

    return calculate_what_if_impact(
        db=db,
        merchant_id=merchant_id,
        interpretation=interpretation.model_dump(),
    )

@router.post("/explain")
def explain_what_if(
    request: WhatIfExplanationRequest,
):
    """
    Phase 2 Step 4 — Explain the projected What-If
    risk impact in merchant-friendly language.
    """

    return {
        "scenario": request.scenario,
        "explanation": explain_what_if_result(
            scenario=request.scenario,
            impact=request.impact,
        ),
    }
@router.post("/recommend")
def recommend_what_if(
    request: WhatIfRecommendationRequest,
):
    """
    Phase 2 Step 5 — Recommend a practical merchant
    action based on the What-If risk scenario.
    """

    return {
        "scenario": request.scenario,
        "recommendation": recommend_what_if_action(
            scenario=request.scenario,
            interpretation=request.interpretation.model_dump(),
            impact=request.impact,
        ),
    }