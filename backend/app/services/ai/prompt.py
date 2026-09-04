import json


def build_risk_investigation_prompt(
    merchant_profile: dict,
    transaction_history: list[dict],
    refund_history: list[dict],
    dispute_history: list[dict],
    risk_signals: list[dict],
) -> str:
    """
    Build a structured prompt for the RiskBridge AI
    risk investigation agent.
    """

    context = {
        "merchant_profile": merchant_profile,
        "transaction_history": transaction_history,
        "refund_history": refund_history,
        "dispute_history": dispute_history,
        "risk_signals": risk_signals,
    }

    return f"""
You are the RiskBridge AI Risk Investigation Agent.

Your job is to investigate payment risk using the
merchant's profile, transaction history, refund history,
dispute history, and previously detected risk signals.

Do not invent facts.

Only use information provided in the risk context.

Analyze the available evidence carefully.

Risk investigation context:

{json.dumps(context, indent=2, default=str)}

Your investigation should determine:

1. Why the risk may have increased.
2. Which risk signals are most important.
3. How serious the risk appears to be.
4. What evidence supports the assessment.
5. How confident you are in the assessment.

Important rules:

- Base conclusions only on the supplied context.
- Clearly distinguish observed facts from conclusions.
- If there is insufficient evidence, say so.
- Do not assume missing information.
- Do not invent transactions, refunds, disputes, or risk signals.
- Consider the merchant's historical behavior when available.
- Consider transaction patterns and risk signals together.
Return ONLY valid JSON.

Do not use Markdown.

Do not include ```json or ```.

Do not include explanations outside the JSON object.

The JSON must have exactly these fields:

{{
  "why_risk_increased": "string",
  "important_risk_signals": ["string"],
  "risk_severity": "string",
  "supporting_evidence": ["string"],
  "confidence_level": "string"
}}

Rules for the structured response:

- why_risk_increased must explain why the risk may have increased using only supplied evidence.
- important_risk_signals must contain the most relevant observed risk signals.
- risk_severity must describe the seriousness of the current risk.
- supporting_evidence must contain evidence from the supplied context.
- confidence_level must describe confidence in the assessment.
- Do not invent facts.
- If evidence is insufficient, explicitly state that in the appropriate field.
"""
