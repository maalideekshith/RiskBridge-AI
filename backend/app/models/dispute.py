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


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    payment_id = Column(
        Integer,
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    dispute_reference = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
        default="open",
        index=True,
    )

    reason = Column(
        String(255),
        nullable=False,
    )

    evidence_status = Column(
        String(30),
        nullable=False,
        default="missing",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    payment = relationship(
        "Payment",
        back_populates="disputes",
    )