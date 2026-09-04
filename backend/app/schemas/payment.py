from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    payment_reference: str = Field(
        min_length=3,
        max_length=100,
    )

    customer_reference: str = Field(
        min_length=1,
        max_length=100,
    )

    amount: Decimal = Field(
        gt=0,
    )

    currency: str = "INR"

    status: str = "created"

    payment_method: str = Field(
        min_length=2,
        max_length=50,
    )

    ip_address: str | None = None

    device_reference: str | None = None

    country: str | None = None

    failure_reason: str | None = None


class PaymentResponse(BaseModel):
    id: int
    payment_reference: str
    customer_reference: str
    amount: Decimal
    currency: str
    status: str
    payment_method: str
    ip_address: str | None
    device_reference: str | None
    country: str | None
    failure_reason: str | None

    model_config = {
        "from_attributes": True,
    }