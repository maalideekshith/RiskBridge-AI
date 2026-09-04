from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class RazorpayConnection(Base):
    __tablename__ = "razorpay_connections"

    id = Column(Integer, primary_key=True, index=True)

    merchant_id = Column(
        Integer,
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    provider = Column(
        String(50),
        nullable=False,
        default="razorpay",
    )

    status = Column(
        String(30),
        nullable=False,
        default="connected",
    )

    last_synced_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    merchant = relationship(
        "Merchant",
        back_populates="razorpay_connection",
    )