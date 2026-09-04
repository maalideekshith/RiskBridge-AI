def identify_highest_impact_problem(
    impact: dict,
) -> dict:
    """
    Identify the highest-impact risk problem from
    a What-If or risk simulation result.
    """

    if not impact:
        raise ValueError(
            "impact cannot be empty"
        )

    required_fields = [
        "projected_refund_rate",
        "projected_dispute_rate",
        "projected_transaction_volume",
    ]

    for field in required_fields:
        if field not in impact:
            raise ValueError(
                f"impact is missing required field: {field}"
            )

    refund_rate = float(
        impact["projected_refund_rate"]
    )

    dispute_rate = float(
        impact["projected_dispute_rate"]
    )

    transaction_volume = int(
        impact["projected_transaction_volume"]
    )

    refund_impact = refund_rate * 2.0
    dispute_impact = dispute_rate * 3.0

    if transaction_volume >= 100:
        volume_impact = 10.0
    elif transaction_volume >= 50:
        volume_impact = 5.0
    else:
        volume_impact = 0.0

    problems = {
        "refund_rate": round(
            refund_impact,
            2,
        ),
        "dispute_rate": round(
            dispute_impact,
            2,
        ),
        "transaction_volume": round(
            volume_impact,
            2,
        ),
    }

    highest_problem = max(
        problems,
        key=problems.get,
    )

    highest_impact = problems[
        highest_problem
    ]

    if highest_impact == 0:
        problem = "none"
        impact_score = 0.0
        description = (
            "No material risk driver was identified "
            "from the projected scenario."
        )

    elif highest_problem == "refund_rate":
        problem = "refund_rate"
        impact_score = highest_impact
        description = (
            "The projected refund rate is the "
            "highest-impact risk driver."
        )

    elif highest_problem == "dispute_rate":
        problem = "dispute_rate"
        impact_score = highest_impact
        description = (
            "The projected dispute rate is the "
            "highest-impact risk driver."
        )

    else:
        problem = "transaction_volume"
        impact_score = highest_impact
        description = (
            "The projected transaction volume is the "
            "highest-impact risk driver."
        )

    return {
        "problem": problem,
        "impact_score": impact_score,
        "description": description,
        "risk_contributions": problems,
    }
def generate_remediation_plan(
    highest_impact: dict,
) -> dict:
    """
    Generate a practical remediation plan for the
    highest-impact risk problem identified by Step 1.
    """

    if not highest_impact:
        raise ValueError(
            "highest_impact cannot be empty"
        )

    required_fields = [
        "problem",
        "impact_score",
        "description",
        "risk_contributions",
    ]

    for field in required_fields:
        if field not in highest_impact:
            raise ValueError(
                f"highest_impact is missing required field: {field}"
            )

    problem = highest_impact["problem"]
    impact_score = float(
        highest_impact["impact_score"]
    )

    if problem == "refund_rate":
        actions = [
            "Review recent refund activity.",
            "Investigate the main causes of refunds.",
            "Identify unusual or repeated refund patterns.",
            "Establish ongoing refund-rate monitoring.",
        ]

    elif problem == "dispute_rate":
        actions = [
            "Review recent dispute activity.",
            "Investigate the main causes of disputes.",
            "Identify repeated or unusual dispute patterns.",
            "Strengthen dispute monitoring and prevention controls.",
        ]

    elif problem == "transaction_volume":
        actions = [
            "Review the increase in transaction volume.",
            "Monitor transaction velocity for unusual patterns.",
            "Investigate unexpected spikes in transaction activity.",
            "Establish ongoing transaction-volume monitoring.",
        ]

    else:
        actions = [
            "Continue monitoring merchant risk activity.",
            "Review emerging risk signals.",
            "Investigate any new material risk drivers.",
        ]

    return {
        "problem": problem,
        "impact_score": impact_score,
        "description": highest_impact["description"],
        "actions": actions,
        "action_count": len(actions),
        "status": "plan_generated",
    }
def prioritize_remediation_actions(
    remediation_plan: dict,
) -> dict:
    """
    Prioritize remediation actions based on the
    highest-impact risk problem.

    Phase 3 Step 3 assigns deterministic priorities
    so later remediation steps can use the ordered
    action list.
    """

    if not remediation_plan:
        raise ValueError(
            "remediation_plan cannot be empty"
        )

    required_fields = [
        "problem",
        "impact_score",
        "actions",
    ]

    for field in required_fields:
        if field not in remediation_plan:
            raise ValueError(
                f"remediation_plan is missing required field: {field}"
            )

    problem = remediation_plan["problem"]
    impact_score = float(
        remediation_plan["impact_score"]
    )
    actions = remediation_plan["actions"]

    if not isinstance(actions, list):
        raise ValueError(
            "remediation_plan actions must be a list"
        )

    if not actions:
        raise ValueError(
            "remediation_plan must contain at least one action"
        )

    if problem == "none":
        prioritized_actions = [
            {
                "action": action,
                "priority": "LOW",
                "priority_score": 1,
            }
            for action in actions
        ]

    elif problem == "dispute_rate":
        prioritized_actions = []

        for index, action in enumerate(actions):
            if index < 2:
                priority = "HIGH"
                priority_score = 3
            else:
                priority = "MEDIUM"
                priority_score = 2

            prioritized_actions.append(
                {
                    "action": action,
                    "priority": priority,
                    "priority_score": priority_score,
                }
            )

    elif problem == "refund_rate":
        prioritized_actions = []

        for index, action in enumerate(actions):
            if index < 2:
                priority = "HIGH"
                priority_score = 3
            else:
                priority = "MEDIUM"
                priority_score = 2

            prioritized_actions.append(
                {
                    "action": action,
                    "priority": priority,
                    "priority_score": priority_score,
                }
            )

    elif problem == "transaction_volume":
        prioritized_actions = []

        for index, action in enumerate(actions):
            if index < 2:
                priority = "HIGH"
                priority_score = 3
            else:
                priority = "MEDIUM"
                priority_score = 2

            prioritized_actions.append(
                {
                    "action": action,
                    "priority": priority,
                    "priority_score": priority_score,
                }
            )

    else:
        prioritized_actions = [
            {
                "action": action,
                "priority": "MEDIUM",
                "priority_score": 2,
            }
            for action in actions
        ]

    prioritized_actions.sort(
        key=lambda item: item["priority_score"],
        reverse=True,
    )

    return {
        "problem": problem,
        "impact_score": impact_score,
        "prioritized_actions": prioritized_actions,
        "action_count": len(prioritized_actions),
        "status": "actions_prioritized",
    }
def estimate_risk_reduction(
    prioritized_plan: dict,
) -> dict:
    """
    Estimate the potential risk reduction from
    prioritized remediation actions.

    The estimate is deterministic and represents
    potential reduction if the recommended actions
    are successfully implemented.
    """

    if not prioritized_plan:
        raise ValueError(
            "prioritized_plan cannot be empty"
        )

    required_fields = [
        "problem",
        "impact_score",
        "prioritized_actions",
    ]

    for field in required_fields:
        if field not in prioritized_plan:
            raise ValueError(
                f"prioritized_plan is missing required field: {field}"
            )

    problem = prioritized_plan["problem"]

    impact_score = float(
        prioritized_plan["impact_score"]
    )

    prioritized_actions = prioritized_plan[
        "prioritized_actions"
    ]

    if not isinstance(prioritized_actions, list):
        raise ValueError(
            "prioritized_actions must be a list"
        )

    if not prioritized_actions:
        raise ValueError(
            "prioritized_actions cannot be empty"
        )

    for item in prioritized_actions:
        if not isinstance(item, dict):
            raise ValueError(
                "Each prioritized action must be a dictionary"
            )

        if "action" not in item:
            raise ValueError(
                "Prioritized action is missing action field"
            )

        if "priority" not in item:
            raise ValueError(
                "Prioritized action is missing priority field"
            )

        if "priority_score" not in item:
            raise ValueError(
                "Prioritized action is missing priority_score field"
            )

    if problem == "none":
        reduction_factor = 0.0

    elif problem == "dispute_rate":
        reduction_factor = 0.50

    elif problem == "refund_rate":
        reduction_factor = 0.50

    elif problem == "transaction_volume":
        reduction_factor = 0.30

    else:
        reduction_factor = 0.25

    estimated_total_reduction = round(
        impact_score * reduction_factor,
        2,
    )

    remaining_risk = round(
        max(
            0.0,
            impact_score - estimated_total_reduction,
        ),
        2,
    )

    action_count = len(
        prioritized_actions
    )

    if action_count > 0:
        base_reduction_per_action = (
            estimated_total_reduction
            / action_count
        )
    else:
        base_reduction_per_action = 0.0

    actions_with_reduction = []

    for item in prioritized_actions:
        priority = item["priority"]

        if priority == "HIGH":
            priority_multiplier = 1.25
        elif priority == "MEDIUM":
            priority_multiplier = 1.0
        else:
            priority_multiplier = 0.75

        estimated_action_reduction = round(
            base_reduction_per_action
            * priority_multiplier,
            2,
        )

        actions_with_reduction.append(
            {
                "action": item["action"],
                "priority": priority,
                "priority_score": item[
                    "priority_score"
                ],
                "estimated_risk_reduction": (
                    estimated_action_reduction
                ),
            }
        )

    return {
        "problem": problem,
        "impact_score": impact_score,
        "estimated_risk_reduction": (
            estimated_total_reduction
        ),
        "remaining_risk": remaining_risk,
        "actions": actions_with_reduction,
        "action_count": action_count,
        "status": "risk_reduction_estimated",
    }
def track_remediation_status(
    risk_reduction_plan: dict,
    completed_actions: int = 0,
    status: str = "pending",
) -> dict:
    """
    Track the current remediation progress.

    Phase 3 Step 5 tracks remediation status,
    completed actions, and completion percentage.
    """

    if not risk_reduction_plan:
        raise ValueError(
            "risk_reduction_plan cannot be empty"
        )

    required_fields = [
        "problem",
        "impact_score",
        "estimated_risk_reduction",
        "remaining_risk",
        "actions",
        "action_count",
    ]

    for field in required_fields:
        if field not in risk_reduction_plan:
            raise ValueError(
                f"risk_reduction_plan is missing required field: {field}"
            )

    valid_statuses = {
        "pending",
        "in_progress",
        "completed",
    }

    if status not in valid_statuses:
        raise ValueError(
            "status must be one of: pending, in_progress, completed"
        )

    action_count = int(
        risk_reduction_plan["action_count"]
    )

    if action_count <= 0:
        raise ValueError(
            "risk_reduction_plan must contain at least one action"
        )

    if not isinstance(completed_actions, int):
        raise ValueError(
            "completed_actions must be an integer"
        )

    if completed_actions < 0:
        raise ValueError(
            "completed_actions cannot be negative"
        )

    if completed_actions > action_count:
        raise ValueError(
            "completed_actions cannot exceed action_count"
        )

    if status == "completed":
        if completed_actions != action_count:
            raise ValueError(
                "completed status requires all actions to be completed"
            )

    if status == "pending" and completed_actions != 0:
        raise ValueError(
            "pending status requires zero completed actions"
        )

    if (
        status == "in_progress"
        and (
            completed_actions == 0
            or completed_actions == action_count
        )
    ):
        raise ValueError(
            "in_progress status requires partial action completion"
        )

    completion_percentage = round(
        (
            completed_actions
            / action_count
        )
        * 100,
        2,
    )

    return {
        "problem": risk_reduction_plan["problem"],
        "impact_score": float(
            risk_reduction_plan["impact_score"]
        ),
        "estimated_risk_reduction": float(
            risk_reduction_plan[
                "estimated_risk_reduction"
            ]
        ),
        "remaining_risk": float(
            risk_reduction_plan[
                "remaining_risk"
            ]
        ),
        "completed_actions": completed_actions,
        "total_actions": action_count,
        "completion_percentage": completion_percentage,
        "status": status,
    }

