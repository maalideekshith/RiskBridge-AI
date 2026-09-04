from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.merchant import Merchant
from app.models.risk_alert import RiskAlert
from app.models.user import User
from app.schemas.risk_alert import RiskAlertResponse


router = APIRouter(
    prefix="/risk-alerts",
    tags=["Risk Alerts"],
)


@router.get(
    "/{merchant_id}",
    response_model=list[RiskAlertResponse],
)
def list_risk_alerts(
    merchant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    merchant = (
        db.query(Merchant)
        .filter(Merchant.id == merchant_id)
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found",
        )

    if merchant.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this merchant",
        )

    return (
        db.query(RiskAlert)
        .filter(RiskAlert.merchant_id == merchant_id)
        .order_by(RiskAlert.created_at.desc())
        .all()
    )