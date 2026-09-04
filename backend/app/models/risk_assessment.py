from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    JSON,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    payment_id = Column(
        Integer,
        ForeignKey(
            "payments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    risk_score = Column(
        Integer,
        nullable=False,
    )

    risk_category = Column(
        String(30),
        nullable=False,
        index=True,
    )

    signals = Column(
        JSON,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    payment = relationship(
    "Payment",
    back_populates="risk_assessments",
)