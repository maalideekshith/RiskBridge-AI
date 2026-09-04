from decimal import Decimal

from pydantic import BaseModel, Field


class RefundCreate(BaseModel):
    refund_reference: str = Field(
        min_length=3,
        max_length=100,
    )

    amount: Decimal = Field(
        gt=0,
    )

    status: str = "requested"

    reason: str | None = None


class RefundResponse(BaseModel):
    id: int
    payment_id: int
    refund_reference: str
    amount: Decimal
    status: str
    reason: str | None

    model_config = {
        "from_attributes": True,
    }