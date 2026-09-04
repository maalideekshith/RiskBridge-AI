import logging

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.payment import Payment
from app.models.risk_assessment import RiskAssessment
from app.services.kafka.consumer import KafkaEventConsumer
from app.services.kafka.producer import kafka_producer
from app.services.risk_engine import detect_amount_anomaly
from app.services.risk_alerts import create_risk_alert
from app.services.audit_log import create_audit_log
logger = logging.getLogger(__name__)


def calculate_risk(
    amount_anomaly: dict,
) -> tuple[int, str]:
    """
    Convert risk signals into a simple risk score
    and category.
    """

    if amount_anomaly["detected"]:
        return 80, "high"

    return 20, "low"


def process_payment_event(
    event: dict,
    db: Session,
) -> None:
    payment_id = event.get("payment_id")

    if not payment_id:
        logger.warning(
            "Payment event missing payment_id: %s",
            event,
        )
        return

    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        logger.warning(
            "Payment not found for payment_id=%s",
            payment_id,
        )
        return

    # --------------------------------------------------------
    # Run existing risk engine
    # --------------------------------------------------------

    amount_anomaly = detect_amount_anomaly(
        db,
        payment,
    )

    # --------------------------------------------------------
    # Calculate overall risk
    # --------------------------------------------------------

    risk_score, risk_category = calculate_risk(
        amount_anomaly,
    )

    # --------------------------------------------------------
    # Store risk assessment
    # --------------------------------------------------------

    assessment = RiskAssessment(
        payment_id=payment.id,
        risk_score=risk_score,
        risk_category=risk_category,
        signals={
            "amount_anomaly": {
                "detected": amount_anomaly["detected"],
                "current_amount": str(
                    amount_anomaly["current_amount"]
                ),
                "historical_average": (
                    str(amount_anomaly["historical_average"])
                    if amount_anomaly["historical_average"]
                    is not None
                    else None
                ),
                "ratio": (
                    str(amount_anomaly["ratio"])
                    if amount_anomaly["ratio"] is not None
                    else None
                ),
                "reason": amount_anomaly["reason"],
            }
        },
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    create_audit_log(
    db=db,
    merchant_id=payment.merchant_id,
    user_id=None,
    action="RISK_ASSESSMENT_CREATED",
    entity_type="risk_assessment",
    entity_id=assessment.id,
    description=(
        f"Risk assessment created with score "
        f"{assessment.risk_score} and category "
        f"{assessment.risk_category}"
    ),
)

    alert = create_risk_alert(
    db=db,
    assessment=assessment,
    payment=payment,
)

    if alert:
     logger.info(
        "Risk alert created: alert_id=%s payment_id=%s severity=%s",
        alert.id,
        payment.id,
        alert.severity,
    )

    logger.info(
        "Risk assessment stored: payment_id=%s "
        "risk_score=%s risk_category=%s",
        payment.id,
        risk_score,
        risk_category,
    )

    print(
        f"Risk assessment stored for "
        f"{payment.payment_reference}:"
    )

    print(
        {
            "risk_assessment_id": assessment.id,
            "payment_id": payment.id,
            "risk_score": risk_score,
            "risk_category": risk_category,
            "signals": assessment.signals,
        }
    )

    # --------------------------------------------------------
    # Publish risk result to Kafka
    # --------------------------------------------------------

    risk_event = {
    "event_type": "risk.assessed",
    "risk_assessment_id": assessment.id,
    "payment_id": payment.id,
    "payment_reference": payment.payment_reference,
    "merchant_id": payment.merchant_id,
    "risk_score": risk_score,
    "risk_category": risk_category,
    "signals": assessment.signals,
    "created_at": assessment.created_at.isoformat(),
}

    kafka_producer.publish(
        "risk-events",
        risk_event,
    )

    print(
        f"Risk result published for "
        f"{payment.payment_reference}"
    )

    print(risk_event)


def consume_payment_events() -> None:
    consumer = KafkaEventConsumer(
        topics=["payment-events"],
        group_id="riskbridge-risk-consumer",
    )

    db = SessionLocal()

    logger.info(
        "Starting RiskBridge payment risk consumer..."
    )

    try:
        for event in consumer.consume():
            process_payment_event(
                event,
                db,
            )

    except KeyboardInterrupt:
        logger.info(
            "Payment risk consumer stopped."
        )

    finally:
        db.close()
        consumer.close()
        kafka_producer.close()


if __name__ == "__main__":
    consume_payment_events()