
import json

from sqlalchemy.orm import Session

from app.schemas.what_if import WhatIfInterpretation
from app.services.ai.agent import get_ai_client
from app.services.risk_simulator import simulate_risk


def accept_what_if_scenario(
    scenario: str,
) -> dict:
    """
    Accept a natural-language What-If scenario.

    Phase 2 Step 1 only accepts and validates the user's
    scenario. Interpretation and risk calculation are
    implemented in later steps.
    """

    if not scenario or not scenario.strip():
        raise ValueError(
            "What-If scenario cannot be empty"
        )

    return {
        "scenario": scenario.strip(),
        "status": "received",
    }


def interpret_what_if_scenario(
    scenario: str,
) -> dict:
    """
    Interpret a natural-language What-If scenario
    into structured risk simulation parameters.
    """

    if not scenario or not scenario.strip():
        raise ValueError(
            "What-If scenario cannot be empty"
        )

    client = get_ai_client()

    prompt = f"""
Interpret the following RiskBridge What-If scenario.

Scenario:
{scenario}

Extract only the hypothetical changes explicitly
described by the user.

Possible fields:

- refund_rate: percentage from 0 to 100
- dispute_rate: percentage from 0 to 100
- transaction_volume_change: percentage change,
  where positive means increase and negative means decrease

Rules:

- Do not invent values.
- If a value is not mentioned, return null.
- "refunds reach 10%" means refund_rate = 10.
- "disputes reach 5%" means dispute_rate = 5.
- "transactions increase by 50%" means transaction_volume_change = 50.
- "transactions decrease by 20%" means transaction_volume_change = -20.
- Return only valid JSON.
- Do not use Markdown.

Return exactly:

{{
  "refund_rate": null,
  "dispute_rate": null,
  "transaction_volume_change": null
}}
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a financial risk scenario "
                        "interpretation assistant for RiskBridge. "
                        "Extract only explicitly stated "
                        "hypothetical changes."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={"type": "json_object"},
            max_tokens=500,
            temperature=0,
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "OpenRouter returned an empty interpretation"
            )

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "OpenRouter returned invalid JSON"
            ) from exc

        interpretation = WhatIfInterpretation.model_validate(
            parsed
        )

        return interpretation.model_dump()

    except Exception as exc:
        raise RuntimeError(
            f"Failed to interpret What-If scenario: {exc}"
        ) from exc


def calculate_what_if_impact(
    db: Session,
    merchant_id: int,
    interpretation: dict,
) -> dict:
    """
    Calculate the risk impact of an interpreted
    What-If scenario using the deterministic
    risk simulator.
    """

    if merchant_id <= 0:
        raise ValueError(
            "merchant_id must be greater than 0"
        )

    if not interpretation:
        raise ValueError(
            "What-If interpretation cannot be empty"
        )

    return simulate_risk(
        db=db,
        merchant_id=merchant_id,
        refund_rate=interpretation.get(
            "refund_rate"
        ),
        dispute_rate=interpretation.get(
            "dispute_rate"
        ),
        transaction_volume_change=interpretation.get(
            "transaction_volume_change"
        ),
    )


def explain_what_if_result(
    scenario: str,
    impact: dict,
) -> str:
    """
    Explain a What-If risk simulation result
    in clear, merchant-friendly language.
    """

    if not scenario or not scenario.strip():
        raise ValueError("scenario must not be empty")

    if not impact:
        raise ValueError("impact must not be empty")

    required_fields = [
        "current_risk_score",
        "projected_risk_score",
        "risk_change",
        "status",
    ]

    for field in required_fields:
        if field not in impact:
            raise ValueError(
                f"impact is missing required field: {field}"
            )

    current_risk = float(
        impact["current_risk_score"]
    )

    projected_risk = float(
        impact["projected_risk_score"]
    )

    risk_change = float(
        impact["risk_change"]
    )

    status = impact["status"]

    if status == "increased":
        explanation = (
            f"If {scenario.strip()}, the projected risk score "
            f"would increase from {current_risk:.2f} to "
            f"{projected_risk:.2f}, a change of +{risk_change:.2f}. "
            "This means the scenario would increase the merchant's "
            "overall risk exposure and should be monitored closely."
        )

    elif status == "decreased":
        explanation = (
            f"If {scenario.strip()}, the projected risk score "
            f"would decrease from {current_risk:.2f} to "
            f"{projected_risk:.2f}, a change of "
            f"{risk_change:.2f}. "
            "This indicates that the scenario would reduce the "
            "merchant's overall risk exposure."
        )

    else:
        explanation = (
            f"If {scenario.strip()}, the projected risk score "
            f"would remain at {projected_risk:.2f}. "
            "This scenario does not materially change the "
            "merchant's projected risk level."
        )

    return explanation


def recommend_what_if_action(
    scenario: str,
    interpretation: dict,
    impact: dict,
) -> str:
    """
    Recommend a practical merchant action based on a
    What-If scenario and its projected risk impact.
    """

    if not scenario or not scenario.strip():
        raise ValueError(
            "scenario must not be empty"
        )

    if not interpretation:
        raise ValueError(
            "interpretation must not be empty"
        )

    if not impact:
        raise ValueError(
            "impact must not be empty"
        )

    required_impact_fields = [
        "current_risk_score",
        "projected_risk_score",
        "risk_change",
        "status",
    ]

    for field in required_impact_fields:
        if field not in impact:
            raise ValueError(
                f"impact is missing required field: {field}"
            )

    current_risk = float(
        impact["current_risk_score"]
    )

    projected_risk = float(
        impact["projected_risk_score"]
    )

    risk_change = float(
        impact["risk_change"]
    )

    status = impact["status"]

    refund_rate = interpretation.get(
        "refund_rate"
    )

    dispute_rate = interpretation.get(
        "dispute_rate"
    )

    transaction_volume_change = interpretation.get(
        "transaction_volume_change"
    )

    if status == "increased":

        if (
            refund_rate is not None
            and dispute_rate is not None
            and transaction_volume_change is not None
        ):
            action = (
                "Review refund and dispute activity immediately, "
                "strengthen transaction monitoring, and investigate "
                "the increase in transaction volume before allowing "
                "the higher-risk pattern to continue."
            )

        elif refund_rate is not None:
            action = (
                "Review recent refund activity, investigate the "
                "cause of the higher refund rate, and establish "
                "ongoing refund-rate monitoring."
            )

        elif dispute_rate is not None:
            action = (
                "Review recent disputes, investigate the causes "
                "of the higher dispute rate, and strengthen "
                "dispute monitoring."
            )

        elif transaction_volume_change is not None:
            action = (
                "Monitor transaction velocity closely and review "
                "the increased transaction volume for unusual "
                "patterns before the higher activity continues."
            )

        else:
            action = (
                "Review the scenario's affected risk signals and "
                "increase monitoring because the projected risk "
                "level has increased."
            )

    elif status == "decreased":

        action = (
            "Maintain the controls contributing to the lower "
            "projected risk and continue monitoring transaction "
            "activity to ensure the improvement is sustained."
        )

    else:

        action = (
            "Continue normal risk monitoring because the scenario "
            "does not materially change the projected risk level."
        )

    return (
        f"{action} "
        f"Projected risk changes from {current_risk:.2f} to "
        f"{projected_risk:.2f} ({risk_change:+.2f})."
    )

