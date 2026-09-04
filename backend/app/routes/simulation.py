from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.simulation import (
    RiskSimulationRequest,
    RiskSimulationResponse,
)
from app.services.risk_simulator import simulate_risk


router = APIRouter(
    prefix="/api/simulation",
    tags=["Risk Simulation"],
)


@router.post(
    "/risk",
    response_model=RiskSimulationResponse,
)
def run_risk_simulation(
    request: RiskSimulationRequest,
    db: Session = Depends(get_db),
):
    return simulate_risk(
        db=db,
        merchant_id=request.merchant_id,
        refund_rate=request.refund_rate,
        dispute_rate=request.dispute_rate,
        transaction_volume_change=request.transaction_volume_change,
        high_value_transactions=request.high_value_transactions,
        failed_payments=request.failed_payments,
    )