from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.risk_alert import RiskAlert
from app.models.risk_assessment import RiskAssessment
from app.services.audit_log import create_audit_log

def create_risk_alert(
    db: Session,
    assessment: RiskAssessment,
    payment: Payment,
) -> RiskAlert | None:
    if assessment.risk_score >= 80:
        severity = "high"
        title = "High payment risk detected"
    elif assessment.risk_score >= 60:
        severity = "medium"
        title = "Medium payment risk detected"
    else:
        return None

    message = (
        f"Payment {payment.payment_reference} has a "
        f"risk score of {assessment.risk_score} "
        f"({assessment.risk_category})."
    )

    alert = RiskAlert(
        merchant_id=payment.merchant_id,
        payment_id=payment.id,
        assessment_id=assessment.id,
        severity=severity,
        title=title,
        message=message,
        status="open",
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    create_audit_log(
    db=db,
    merchant_id=payment.merchant_id,
    user_id=None,
    action="RISK_ALERT_CREATED",
    entity_type="risk_alert",
    entity_id=alert.id,
    description=(
        f"Risk alert created with severity "
        f"{alert.severity} for assessment "
        f"#{assessment.id}"
    ),
)

    return alert
