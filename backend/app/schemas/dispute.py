from decimal import Decimal

from pydantic import BaseModel, Field


class DisputeCreate(BaseModel):
    dispute_reference: str = Field(
        min_length=3,
        max_length=100,
    )

    amount: Decimal = Field(
        gt=0,
    )

    status: str = "open"

    reason: str = Field(
        min_length=2,
        max_length=255,
    )

    evidence_status: str = "missing"


class DisputeResponse(BaseModel):
    id: int
    payment_id: int
    dispute_reference: str
    amount: Decimal
    status: str
    reason: str
    evidence_status: str

    model_config = {
        "from_attributes": True,
    }