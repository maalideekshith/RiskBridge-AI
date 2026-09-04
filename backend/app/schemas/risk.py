from decimal import Decimal

from pydantic import BaseModel


class AmountAnomalyResponse(BaseModel):
    payment_id: int
    signal: str
    detected: bool
    current_amount: Decimal
    historical_average: Decimal | None
    ratio: Decimal | None
    reason: str