from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.database import Base


class RiskAlert(Base):
    __tablename__ = "risk_alerts"

    id = Column(Integer, primary_key=True, index=True)

    merchant_id = Column(
        Integer,
        ForeignKey("merchants.id"),
        nullable=False,
        index=True,
    )

    payment_id = Column(
        Integer,
        ForeignKey("payments.id"),
        nullable=False,
        index=True,
    )

    assessment_id = Column(
        Integer,
        ForeignKey("risk_assessments.id"),
        nullable=False,
        index=True,
    )

    severity = Column(String(30), nullable=False, index=True)

    title = Column(String(255), nullable=False)

    message = Column(Text, nullable=False)

    status = Column(
        String(30),
        nullable=False,
        default="open",
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    read_at = Column(DateTime(timezone=True), nullable=True)

    resolved_at = Column(DateTime(timezone=True), nullable=True)
