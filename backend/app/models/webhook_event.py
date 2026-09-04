from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint

from app.database import Base


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)

    merchant_id = Column(Integer, nullable=False, index=True)

    event_id = Column(String(100), nullable=False)

    event_type = Column(String(100), nullable=False)

    processed_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint(
            "merchant_id",
            "event_id",
            name="uq_webhook_events_merchant_event",
        ),
    )