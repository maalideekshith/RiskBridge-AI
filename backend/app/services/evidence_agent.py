def analyze_case(
    case: dict,
    evidence: dict,
) -> dict:
    """
    Analyze a risk-review case using collected evidence.
    """

    if not case:
        raise ValueError(
            "case cannot be empty"
        )

    required_case_fields = [
        "merchant_id",
        "risk_reason",
        "status",
    ]

    for field in required_case_fields:
        if field not in case:
            raise ValueError(
                f"case is missing required field: {field}"
            )

    if not evidence:
        raise ValueError(
            "evidence cannot be empty"
        )

    if not isinstance(evidence, dict):
        raise ValueError(
            "evidence must be a dictionary"
        )

    transaction_count = len(
        evidence.get("transactions", [])
    )

    refund_count = len(
        evidence.get("refunds", [])
    )

    dispute_count = len(
        evidence.get("disputes", [])
    )

    policy_count = len(
        evidence.get("policies", [])
    )

    risk_signal_count = len(
        evidence.get("risk_signals", [])
    )

    total_evidence_items = (
        transaction_count
        + refund_count
        + dispute_count
        + policy_count
        + risk_signal_count
    )

    if risk_signal_count > 0:
        assessment = "high_risk"

    elif (
        refund_count > 0
        or dispute_count > 0
    ):
        assessment = "elevated_risk"

    else:
        assessment = "insufficient_risk_evidence"

    return {
        "merchant_id": case["merchant_id"],
        "risk_reason": case["risk_reason"],
        "assessment": assessment,
        "transaction_count": transaction_count,
        "refund_count": refund_count,
        "dispute_count": dispute_count,
        "policy_count": policy_count,
        "risk_signal_count": risk_signal_count,
        "total_evidence_items": total_evidence_items,
        "status": "case_analyzed",
    }
def identify_missing_evidence(
    evidence: dict,
) -> dict:
    """
    Identify evidence categories that are missing
    from a risk-review case.
    """

    if not evidence:
        raise ValueError(
            "evidence cannot be empty"
        )

    if not isinstance(evidence, dict):
        raise ValueError(
            "evidence must be a dictionary"
        )

    required_evidence = {
        "transactions": evidence.get(
            "transactions",
            []
        ),
        "refunds": evidence.get(
            "refunds",
            []
        ),
        "disputes": evidence.get(
            "disputes",
            []
        ),
        "policies": evidence.get(
            "policies",
            []
        ),
        "risk_signals": evidence.get(
            "risk_signals",
            []
        ),
    }

    missing_evidence = []

    for category, items in required_evidence.items():
        if not isinstance(items, list):
            raise ValueError(
                f"{category} must be a list"
            )

        if not items:
            missing_evidence.append(category)

    return {
        "missing_evidence": missing_evidence,
        "missing_count": len(
            missing_evidence
        ),
        "status": "missing_evidence_identified",
    }
def generate_evidence_checklist(
    missing_evidence: dict,
) -> dict:
    """
    Generate an evidence checklist based on
    missing evidence categories.
    """

    if not missing_evidence:
        raise ValueError(
            "missing_evidence cannot be empty"
        )

    if not isinstance(missing_evidence, dict):
        raise ValueError(
            "missing_evidence must be a dictionary"
        )

    if "missing_evidence" not in missing_evidence:
        raise ValueError(
            "missing_evidence is missing required field"
        )

    missing = missing_evidence["missing_evidence"]

    if not isinstance(missing, list):
        raise ValueError(
            "missing_evidence must be a list"
        )

    checklist = []

    descriptions = {
        "transactions": (
            "Collect relevant transaction records."
        ),
        "refunds": (
            "Collect relevant refund information."
        ),
        "disputes": (
            "Collect relevant dispute information."
        ),
        "policies": (
            "Collect applicable merchant policies."
        ),
        "risk_signals": (
            "Collect relevant risk signals."
        ),
    }

    for category in missing:
        if category in descriptions:
            checklist.append(
                {
                    "category": category,
                    "requirement": descriptions[
                        category
                    ],
                    "status": "missing",
                }
            )

    return {
        "checklist": checklist,
        "checklist_count": len(checklist),
        "status": "checklist_generated",
    }
def generate_case_summary(
    case_analysis: dict,
    evidence: dict,
) -> dict:
    """
    Generate a concise case summary from the
    risk analysis and collected evidence.
    """

    if not case_analysis:
        raise ValueError(
            "case_analysis cannot be empty"
        )

    if not isinstance(case_analysis, dict):
        raise ValueError(
            "case_analysis must be a dictionary"
        )

    required_fields = [
        "merchant_id",
        "risk_reason",
        "assessment",
        "total_evidence_items",
    ]

    for field in required_fields:
        if field not in case_analysis:
            raise ValueError(
                f"case_analysis is missing required field: {field}"
            )

    if not evidence:
        raise ValueError(
            "evidence cannot be empty"
        )

    if not isinstance(evidence, dict):
        raise ValueError(
            "evidence must be a dictionary"
        )

    summary = (
        f"Merchant {case_analysis['merchant_id']} "
        f"was flagged for {case_analysis['risk_reason']}. "
        f"The case assessment is "
        f"{case_analysis['assessment']}. "
        f"A total of "
        f"{case_analysis['total_evidence_items']} "
        f"evidence items were collected."
    )

    return {
        "merchant_id": case_analysis["merchant_id"],
        "risk_reason": case_analysis["risk_reason"],
        "assessment": case_analysis["assessment"],
        "summary": summary,
        "evidence_count": case_analysis[
            "total_evidence_items"
        ],
        "status": "case_summary_generated",
    }
def generate_recommended_response(
    case_analysis: dict,
    case_summary: dict,
    evidence_checklist: dict,
) -> dict:
    """
    Generate a recommended response for a risk-review case
    based on the case analysis, summary, and evidence checklist.
    """

    if not case_analysis:
        raise ValueError(
            "case_analysis cannot be empty"
        )

    if not isinstance(case_analysis, dict):
        raise ValueError(
            "case_analysis must be a dictionary"
        )

    required_analysis_fields = [
        "merchant_id",
        "risk_reason",
        "assessment",
    ]

    for field in required_analysis_fields:
        if field not in case_analysis:
            raise ValueError(
                f"case_analysis is missing required field: {field}"
            )

    if not case_summary:
        raise ValueError(
            "case_summary cannot be empty"
        )

    if not isinstance(case_summary, dict):
        raise ValueError(
            "case_summary must be a dictionary"
        )

    if "summary" not in case_summary:
        raise ValueError(
            "case_summary is missing required field: summary"
        )

    if not evidence_checklist:
        raise ValueError(
            "evidence_checklist cannot be empty"
        )

    if not isinstance(evidence_checklist, dict):
        raise ValueError(
            "evidence_checklist must be a dictionary"
        )

    if "checklist" not in evidence_checklist:
        raise ValueError(
            "evidence_checklist is missing required field: checklist"
        )

    checklist = evidence_checklist["checklist"]

    if not isinstance(checklist, list):
        raise ValueError(
            "evidence_checklist checklist must be a list"
        )

    missing_count = len(checklist)

    assessment = case_analysis["assessment"]

    if assessment == "high_risk":
        if missing_count > 0:
            recommendation = (
                "Prioritize the high-risk case, "
                "collect the missing evidence, "
                "and review the identified risk drivers "
                "before making a final risk decision."
            )
        else:
            recommendation = (
                "Prioritize the high-risk case, "
                "review the collected evidence, "
                "and proceed with a formal risk decision."
            )

    elif assessment == "elevated_risk":
        recommendation = (
            "Review the identified risk indicators, "
            "complete any missing evidence, "
            "and apply appropriate monitoring or remediation."
        )

    else:
        recommendation = (
            "Collect additional evidence and continue "
            "monitoring the case before making a final decision."
        )

    return {
        "merchant_id": case_analysis["merchant_id"],
        "risk_reason": case_analysis["risk_reason"],
        "assessment": assessment,
        "recommendation": recommendation,
        "missing_evidence_count": missing_count,
        "status": "recommended_response_generated",
    }