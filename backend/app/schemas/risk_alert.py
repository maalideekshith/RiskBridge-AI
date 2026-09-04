from datetime import datetime

from pydantic import BaseModel


class RiskAlertResponse(BaseModel):
    id: int
    merchant_id: int
    payment_id: int
    assessment_id: int
    severity: str
    title: str
    message: str
    status: str
    created_at: datetime
    read_at: datetime | None
    resolved_at: datetime | None