from datetime import datetime, timezone
import json
from typing import Any

from sqlalchemy.orm import Session

from app.models import Dispute, Payment, Refund, WebhookEvent


SUPPORTED_EVENTS = {
    "payment.authorized",
    "payment.captured",
    "payment.failed",
    "refund.created",
    "refund.processed",
    "refund.failed",
    "payment.dispute.created",
}


def _timestamp_to_datetime(timestamp: int | float | None) -> datetime:
    if timestamp is None:
        return datetime.now(timezone.utc)

    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def _amount_to_decimal(amount: int | float | str | None):
    from decimal import Decimal

    if amount is None:
        return Decimal("0.00")

    return Decimal(str(amount)) / Decimal("100")


def parse_webhook_event(raw_body: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON webhook payload") from exc

    if not isinstance(payload, dict):
        raise ValueError("Webhook payload must be a JSON object")

    event = payload.get("event")

    if not event:
        raise ValueError("Webhook event is missing")

    return payload


def get_webhook_event_name(payload: dict[str, Any]) -> str:
    return str(payload["event"])


def is_supported_event(event: str) -> bool:
    return event in SUPPORTED_EVENTS
def _record_webhook_event(
    db: Session,
    merchant_id: int,
    event_id: str,
    event_type: str,
) -> WebhookEvent:
    webhook_event = WebhookEvent(
        merchant_id=merchant_id,
        event_id=event_id,
        event_type=event_type,
    )

    db.add(webhook_event)
    db.commit()
    db.refresh(webhook_event)

    return webhook_event


def process_webhook_event(
    db: Session,
    merchant_id: int,
    payload: dict[str, Any],
    event_id: str,
) -> dict[str, Any]:
    event = get_webhook_event_name(payload)

    existing_event = (
        db.query(WebhookEvent)
        .filter(
            WebhookEvent.merchant_id == merchant_id,
            WebhookEvent.event_id == event_id,
        )
        .first()
    )

    if existing_event is not None:
        return {
            "event": event,
            "status": "ignored",
            "reason": "Duplicate webhook event",
            "event_id": event_id,
        }

    if not is_supported_event(event):
        return {
            "event": event,
            "status": "ignored",
            "reason": "Unsupported event",
        }

    if event in {"payment.authorized", "payment.captured", "payment.failed"}:
        result = _process_payment_event(
            db=db,
            merchant_id=merchant_id,
            event=event,
            payload=payload,
        )

    elif event in {"refund.created", "refund.processed", "refund.failed"}:
        result = _process_refund_event(
            db=db,
            merchant_id=merchant_id,
            event=event,
            payload=payload,
        )

    elif event == "payment.dispute.created":
        result = _process_dispute_event(
            db=db,
            merchant_id=merchant_id,
            payload=payload,
        )

    else:
        return {
            "event": event,
            "status": "ignored",
            "reason": "No handler",
        }

    if result.get("status") == "processed":
        webhook_event = WebhookEvent(
            merchant_id=merchant_id,
            event_id=event_id,
            event_type=event,
        )

        db.add(webhook_event)
        db.commit()

    return result

def _process_payment_event(
    db: Session,
    merchant_id: int,
    event: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    entity = (
        payload
        .get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    payment_reference = entity.get("id")

    if not payment_reference:
        return {
            "event": event,
            "status": "ignored",
            "reason": "Payment ID missing",
        }

    payment = (
        db.query(Payment)
        .filter(
            Payment.payment_reference == payment_reference,
            Payment.merchant_id == merchant_id,
        )
        .first()
    )

    if payment is None:
        return {
            "event": event,
            "status": "ignored",
            "reason": "Payment not found for merchant",
            "payment_reference": payment_reference,
        }

    payment.status = entity.get("status", payment.status)

    payment.payment_method = entity.get(
        "method",
        payment.payment_method,
    )

    if event == "payment.failed":
     payment.failure_reason = (
        entity.get("error_description")
        or entity.get("error_reason")
        or entity.get("error_code")
        or payment.failure_reason
    )
    else:
     payment.failure_reason = None

    if entity.get("amount") is not None:
        payment.amount = _amount_to_decimal(entity["amount"])

    if entity.get("currency"):
        payment.currency = entity["currency"]

    if entity.get("created_at") is not None:
        payment.created_at = _timestamp_to_datetime(
            entity["created_at"]
        )

    db.commit()

    return {
    "event": event,
    "status": "processed",
    "payment_id": payment.id,
    "payment_reference": payment.payment_reference,
}


def _process_refund_event(
    db: Session,
    merchant_id: int,
    event: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    entity = (
        payload
        .get("payload", {})
        .get("refund", {})
        .get("entity", {})
    )

    refund_reference = entity.get("id")
    payment_reference = entity.get("payment_id")

    if not refund_reference or not payment_reference:
        return {
            "event": event,
            "status": "ignored",
            "reason": "Refund ID or payment ID missing",
        }

    payment = (
        db.query(Payment)
        .filter(
            Payment.payment_reference == payment_reference,
            Payment.merchant_id == merchant_id,
        )
        .first()
    )

    if payment is None:
        return {
            "event": event,
            "status": "ignored",
            "reason": "Payment not found for merchant",
            "payment_reference": payment_reference,
        }

    refund = (
        db.query(Refund)
        .filter(
            Refund.refund_reference == refund_reference,
        )
        .first()
    )

    if refund is None:
        refund = Refund(
            payment_id=payment.id,
            refund_reference=refund_reference,
            amount=_amount_to_decimal(entity.get("amount")),
            status=entity.get("status", "requested"),
            reason=(
                entity.get("notes", {}).get("reason")
                if isinstance(entity.get("notes"), dict)
                else entity.get("notes")),
            created_at=_timestamp_to_datetime(
                entity.get("created_at")
            ),
        )
        db.add(refund)
    else:
        refund.payment_id = payment.id
        refund.amount = _amount_to_decimal(entity.get("amount"))
        refund.status = entity.get("status", refund.status)
        notes = entity.get("notes")

        if isinstance(notes, dict):
         refund.reason = notes.get("reason", refund.reason)
        elif notes is not None:
         refund.reason = str(notes)

        if entity.get("created_at") is not None:
            refund.created_at = _timestamp_to_datetime(
                entity["created_at"]
            )

    db.commit()

    return {
        "event": event,
        "status": "processed",
        "refund_id": refund.id,
        "refund_reference": refund.refund_reference,
        "payment_id": payment.id,
    }


def _process_dispute_event(
    db: Session,
    merchant_id: int,
    payload: dict[str, Any],
) -> dict[str, Any]:
    event = "payment.dispute.created"

    entity = (
        payload
        .get("payload", {})
        .get("dispute", {})
        .get("entity", {})
    )

    dispute_reference = entity.get("id")
    payment_reference = entity.get("payment_id")

    if not dispute_reference or not payment_reference:
        return {
            "event": event,
            "status": "ignored",
            "reason": "Dispute ID or payment ID missing",
        }

    payment = (
        db.query(Payment)
        .filter(
            Payment.payment_reference == payment_reference,
            Payment.merchant_id == merchant_id,
        )
        .first()
    )

    if payment is None:
        return {
            "event": event,
            "status": "ignored",
            "reason": "Payment not found for merchant",
            "payment_reference": payment_reference,
        }

    dispute = (
        db.query(Dispute)
        .filter(
            Dispute.dispute_reference == dispute_reference,
        )
        .first()
    )

    if dispute is None:
        dispute = Dispute(
            payment_id=payment.id,
            dispute_reference=dispute_reference,
            amount=_amount_to_decimal(entity.get("amount")),
            status=entity.get("status", "open"),
            reason=entity.get("reason", "Unknown"),
            evidence_status="missing",
            created_at=_timestamp_to_datetime(
                entity.get("created_at")
            ),
        )
        db.add(dispute)
    else:
        dispute.payment_id = payment.id
        dispute.amount = _amount_to_decimal(entity.get("amount"))
        dispute.status = entity.get("status", dispute.status)
        dispute.reason = entity.get("reason", dispute.reason)

    db.commit()

    return {
        "event": event,
        "status": "processed",
        "dispute_id": dispute.id,
        "dispute_reference": dispute.dispute_reference,
        "payment_id": payment.id,
    }