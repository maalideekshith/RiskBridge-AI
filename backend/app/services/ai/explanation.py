from app.services.ai.schemas import RiskInvestigationResponse


def explain_why_risk_increased(
    investigation: RiskInvestigationResponse,
) -> str:
    """
    Extract the AI-generated explanation for why risk increased.

    Phase 3, Step 1.
    """

    if not isinstance(
        investigation,
        RiskInvestigationResponse,
    ):
        raise TypeError(
            "Expected a validated RiskInvestigationResponse"
        )

    explanation = investigation.why_risk_increased.strip()

    if not explanation:
        raise ValueError(
            "AI explanation for why risk increased is empty"
        )

    return explanation


def explain_important_risk_signals(
    investigation: RiskInvestigationResponse,
) -> list[str]:
    """
    Extract the most important risk signals identified
    by the AI investigation.

    Phase 3, Step 2.
    """

    if not isinstance(
        investigation,
        RiskInvestigationResponse,
    ):
        raise TypeError(
            "Expected a validated RiskInvestigationResponse"
        )

    signals = [
        signal.strip()
        for signal in investigation.important_risk_signals
        if signal and signal.strip()
    ]

    if not signals:
        raise ValueError(
            "AI important risk signals cannot be empty"
        )

    return signals


def explain_risk_severity(
    investigation: RiskInvestigationResponse,
) -> str:
    """
    Extract the AI-generated risk severity explanation.

    Phase 3, Step 3.
    """

    if not isinstance(
        investigation,
        RiskInvestigationResponse,
    ):
        raise TypeError(
            "Expected a validated RiskInvestigationResponse"
        )

    severity = investigation.risk_severity.strip()

    if not severity:
        raise ValueError(
            "AI risk severity cannot be empty"
        )

    return severity


def explain_supporting_evidence(
    investigation: RiskInvestigationResponse,
) -> list[str]:
    """
    Extract the evidence supporting the AI risk assessment.

    Phase 3, Step 4.
    """

    if not isinstance(
        investigation,
        RiskInvestigationResponse,
    ):
        raise TypeError(
            "Expected a validated RiskInvestigationResponse"
        )

    evidence = [
        item.strip()
        for item in investigation.supporting_evidence
        if item and item.strip()
    ]

    if not evidence:
        raise ValueError(
            "AI supporting evidence cannot be empty"
        )

    return evidence
def explain_confidence_level(
    investigation: RiskInvestigationResponse,
) -> str:
    """
    Extract the AI-generated confidence level
    for the risk assessment.

    Phase 3, Step 5.
    """

    if not isinstance(
        investigation,
        RiskInvestigationResponse,
    ):
        raise TypeError(
            "Expected a validated RiskInvestigationResponse"
        )

    confidence = investigation.confidence_level.strip()

    if not confidence:
        raise ValueError(
            "AI confidence level cannot be empty"
        )

    return confidence