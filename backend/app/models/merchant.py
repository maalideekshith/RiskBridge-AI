from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    business_name = Column(String(255), nullable=False)
    business_type = Column(String(100), nullable=False)
    website = Column(String(500), nullable=True)
    country = Column(String(100), nullable=False, default="India")
    currency = Column(String(10), nullable=False, default="INR")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="merchant",
    )
    payments = relationship(
        "Payment",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )
    razorpay_connection = relationship(
        "RazorpayConnection",
        back_populates="merchant",
        uselist=False,
        cascade="all, delete-orphan",
    )