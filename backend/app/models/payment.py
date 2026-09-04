from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    merchant_id = Column(
        Integer,
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    payment_reference = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    customer_reference = Column(
        String(100),
        nullable=False,
        index=True,
    )

    amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    currency = Column(
        String(10),
        nullable=False,
        default="INR",
    )

    status = Column(
        String(30),
        nullable=False,
        default="created",
        index=True,
    )

    payment_method = Column(
        String(50),
        nullable=False,
    )

    ip_address = Column(
        String(100),
        nullable=True,
    )

    device_reference = Column(
        String(255),
        nullable=True,
    )

    country = Column(
        String(100),
        nullable=True,
    )

    failure_reason = Column(
        String(255),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    merchant = relationship(
        "Merchant",
        back_populates="payments",
    )

    refunds = relationship(
        "Refund",
        back_populates="payment",
        cascade="all, delete-orphan",
    )

    disputes = relationship(
        "Dispute",
        back_populates="payment",
        cascade="all, delete-orphan",
    )
    risk_assessments = relationship(
    "RiskAssessment",
    back_populates="payment",
    cascade="all, delete-orphan",
)