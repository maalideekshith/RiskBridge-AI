
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class MerchantProfileResponse(BaseModel):
    merchant_id: int
    user_id: int
    business_name: str
    business_type: str
    website: str | None
    country: str | None
    currency: str


class TransactionHistoryItem(BaseModel):
    payment_id: int
    payment_reference: str
    customer_reference: str
    amount: str
    currency: str
    status: str
    payment_method: str
    ip_address: str | None
    device_reference: str | None
    country: str | None
    failure_reason: str | None
    created_at: datetime


class RefundHistoryItem(BaseModel):
    refund_id: int
    payment_id: int
    refund_reference: str
    amount: str
    status: str
    reason: str | None
    created_at: datetime


class DisputeHistoryItem(BaseModel):
    dispute_id: int
    payment_id: int
    dispute_reference: str
    amount: str
    status: str
    reason: str
    evidence_status: str
    created_at: datetime


class RiskSignalItem(BaseModel):
    assessment_id: int
    payment_id: int
    risk_score: int
    risk_category: str
    signals: object
    created_at: datetime
