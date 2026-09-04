from pydantic import BaseModel, Field


class RiskSimulationRequest(BaseModel):
    merchant_id: int = Field(gt=0)

    refund_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )

    dispute_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )

    transaction_volume_change: float | None = Field(
        default=None,
        ge=-100.0,
    )

    high_value_transactions: int | None = Field(
        default=None,
        ge=0,
    )

    failed_payments: int | None = Field(
        default=None,
        ge=0,
    )


class RiskSimulationResponse(BaseModel):
    merchant_id: int

    current_risk_score: float
    projected_risk_score: float
    risk_change: float

    current_refund_rate: float
    projected_refund_rate: float

    current_dispute_rate: float
    projected_dispute_rate: float

    current_transaction_volume: int
    projected_transaction_volume: int

    projected_high_value_transactions: int
    projected_failed_payments: int

    status: str