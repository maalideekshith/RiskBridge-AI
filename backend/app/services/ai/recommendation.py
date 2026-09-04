from app.services.ai.schemas import RiskInvestigationResponse


def recommend_immediate_actions(
    investigation: RiskInvestigationResponse,
) -> list[str]:
    """
    Generate immediate actions based on the validated
    AI risk investigation.

    Phase 4, Step 1.
    """

    if not isinstance(
        investigation,
        RiskInvestigationResponse,
    ):
        raise TypeError(
            "Expected a validated RiskInvestigationResponse"
        )

    severity = investigation.risk_severity.strip().lower()

    signals = investigation.important_risk_signals

    if not signals:
        raise ValueError(
            "Risk investigation contains no risk signals"
        )

    actions = []

    if "high" in severity or "critical" in severity:
        actions.append(
            "Review and investigate the affected transactions immediately."
        )
        actions.append(
            "Consider temporarily restricting suspicious transaction activity."
        )

    elif "medium" in severity:
        actions.append(
            "Review the affected transactions and monitor new payment activity closely."
        )
        actions.append(
            "Verify the most important risk signals before allowing continued activity."
        )

    else:
        actions.append(
            "Continue monitoring recent transaction activity for unusual patterns."
        )
        actions.append(
            "Review the identified risk signals if the transaction pattern continues."
        )

    if any(
        "ip" in signal.lower()
        for signal in signals
    ):
        actions.append(
            "Review repeated IP activity associated with the recent transactions."
        )

    if any(
        "velocity" in signal.lower()
        or "cluster" in signal.lower()
        or "transaction" in signal.lower()
        for signal in signals
    ):
        actions.append(
            "Monitor transaction velocity and repeated payment activity."
        )

    return actions
def recommend_preventive_actions(
    investigation: RiskInvestigationResponse,
) -> list[str]:
    """
    Generate preventive actions based on the validated
    AI risk investigation.

    Phase 4, Step 2.
    """

    if not isinstance(
        investigation,
        RiskInvestigationResponse,
    ):
        raise TypeError(
            "Expected a validated RiskInvestigationResponse"
        )

    signals = investigation.important_risk_signals

    if not signals:
        raise ValueError(
            "Risk investigation contains no risk signals"
        )

    actions = []

    signal_text = " ".join(signals).lower()

    if (
        "velocity" in signal_text
        or "transaction" in signal_text
        or "cluster" in signal_text
    ):
        actions.append(
            "Establish transaction velocity monitoring "
            "to identify unusual bursts of payment activity."
        )

    if "ip" in signal_text:
        actions.append(
            "Monitor repeated IP activity and investigate "
            "unusual concentration of payments from the same IP."
        )

    if "device" in signal_text:
        actions.append(
            "Monitor device activity for repeated or unusual "
            "payment patterns."
        )

    if "amount" in signal_text or "anomaly" in signal_text:
        actions.append(
            "Continue monitoring transaction amounts against "
            "the merchant's historical payment behavior."
        )

    if not actions:
        actions.append(
            "Continue monitoring future transactions and "
            "reassess risk when additional evidence becomes available."
        )

    return actions
def prioritize_actions(
    immediate_actions: list[str],
    preventive_actions: list[str],
) -> list[str]:
    """
    Order recommended actions by priority.

    Phase 4, Step 3.
    """

    if not immediate_actions:
        raise ValueError(
            "Immediate actions cannot be empty"
        )

    if not preventive_actions:
        raise ValueError(
            "Preventive actions cannot be empty"
        )

    all_actions = immediate_actions + preventive_actions

    priority_order = []

    high_priority_keywords = (
        "restrict",
        "block",
        "investigate",
        "review",
        "verify",
        "immediately",
    )

    monitoring_keywords = (
        "monitor",
        "watch",
        "continue monitoring",
    )

    preventive_keywords = (
        "establish",
        "configure",
        "implement",
        "prevent",
    )

    # Highest priority: actions requiring investigation,
    # verification, restriction, or immediate review.
    for action in all_actions:
        action_lower = action.lower()

        if any(
            keyword in action_lower
            for keyword in high_priority_keywords
        ):
            if action not in priority_order:
                priority_order.append(action)

    # Next: monitoring actions.
    for action in all_actions:
        action_lower = action.lower()

        if any(
            keyword in action_lower
            for keyword in monitoring_keywords
        ):
            if action not in priority_order:
                priority_order.append(action)

    # Finally: longer-term preventive actions.
    for action in all_actions:
        action_lower = action.lower()

        if any(
            keyword in action_lower
            for keyword in preventive_keywords
        ):
            if action not in priority_order:
                priority_order.append(action)

    # Safety fallback: include anything not classified.
    for action in all_actions:
        if action not in priority_order:
            priority_order.append(action)

    return priority_order
def explain_expected_impact(
    priority_order: list[str],
) -> list[str]:
    """
    Explain the expected impact of each prioritized action.

    The returned list corresponds to priority_order
    in the same order.

    Phase 4, Step 4.
    """

    if not priority_order:
        raise ValueError(
            "Priority order cannot be empty"
        )

    impacts = []

    for action in priority_order:
        action_lower = action.lower()

        if (
            "review" in action_lower
            or "investigate" in action_lower
            or "verify" in action_lower
        ):
            impacts.append(
                "Helps identify potentially risky activity "
                "early and supports timely investigation."
            )

        elif (
            "ip" in action_lower
            or "device" in action_lower
        ):
            impacts.append(
                "Helps detect repeated or unusual activity "
                "associated with the same source or device."
            )

        elif (
            "velocity" in action_lower
            or "transaction" in action_lower
            or "monitor" in action_lower
        ):
            impacts.append(
                "Improves detection of unusual transaction "
                "patterns and short-term activity spikes."
            )

        elif (
            "amount" in action_lower
            or "anomaly" in action_lower
        ):
            impacts.append(
                "Helps identify transaction amounts that "
                "deviate from expected merchant behavior."
            )

        elif (
            "establish" in action_lower
            or "configure" in action_lower
            or "prevent" in action_lower
        ):
            impacts.append(
                "Creates a preventive control that can reduce "
                "the likelihood of similar risk patterns."
            )

        else:
            impacts.append(
                "Provides additional risk visibility and "
                "supports earlier response to unusual activity."
            )

    return impacts
def explain_merchant_friendly(
    priority_order: list[str],
    expected_impact: list[str],
) -> str:
    """
    Convert technical risk recommendations and their expected
    impacts into a concise, merchant-friendly explanation.

    Phase 4, Step 5.
    """

    if not priority_order:
        raise ValueError(
            "Priority order cannot be empty"
        )

    if not expected_impact:
        raise ValueError(
            "Expected impact cannot be empty"
        )

    if len(priority_order) != len(expected_impact):
        raise ValueError(
            "Priority order and expected impact must have "
            "the same number of items"
        )

    explanation_parts = [
        "Your recent payment activity shows patterns "
        "that are worth monitoring.",
    ]

    explanation_parts.append(
        f"We identified {len(priority_order)} recommended "
        "actions to help you manage the current risk."
    )

    explanation_parts.append(
        "The most important actions should be reviewed first, "
        "followed by ongoing monitoring and preventive controls."
    )

    explanation_parts.append(
        "These recommendations are intended to help identify "
        "unusual payment activity earlier and reduce the chance "
        "of similar risk patterns continuing."
    )

    return " ".join(explanation_parts)