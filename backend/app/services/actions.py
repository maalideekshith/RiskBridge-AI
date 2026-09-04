def create_action(
    problem: str,
    action: str,
    priority: str,
) -> dict:
    """
    Create a remediation action from a Phase 3
    prioritized remediation recommendation.
    """

    if not problem or not problem.strip():
        raise ValueError(
            "problem cannot be empty"
        )

    if not action or not action.strip():
        raise ValueError(
            "action cannot be empty"
        )

    valid_priorities = {
        "HIGH",
        "MEDIUM",
        "LOW",
    }

    if priority not in valid_priorities:
        raise ValueError(
            "priority must be one of: HIGH, MEDIUM, LOW"
        )

    return {
        "problem": problem.strip(),
        "action": action.strip(),
        "priority": priority,
        "status": "pending",
    }
def mark_action_pending(
    action: dict,
) -> dict:
    """
    Mark an existing remediation action as pending.
    """

    if not action:
        raise ValueError(
            "action cannot be empty"
        )

    required_fields = [
        "problem",
        "action",
        "priority",
        "status",
    ]

    for field in required_fields:
        if field not in action:
            raise ValueError(
                f"action is missing required field: {field}"
            )

    valid_priorities = {
        "HIGH",
        "MEDIUM",
        "LOW",
    }

    if action["priority"] not in valid_priorities:
        raise ValueError(
            "action contains an invalid priority"
        )

    result = action.copy()

    result["status"] = "pending"

    return result
def mark_action_completed(
    action: dict,
) -> dict:
    """
    Mark an existing remediation action as completed.
    """

    if not action:
        raise ValueError(
            "action cannot be empty"
        )

    required_fields = [
        "problem",
        "action",
        "priority",
        "status",
    ]

    for field in required_fields:
        if field not in action:
            raise ValueError(
                f"action is missing required field: {field}"
            )

    valid_priorities = {
        "HIGH",
        "MEDIUM",
        "LOW",
    }

    if action["priority"] not in valid_priorities:
        raise ValueError(
            "action contains an invalid priority"
        )

    result = action.copy()

    result["status"] = "completed"

    return result
def calculate_updated_risk(
    remediation_result: dict,
    completed_actions: int,
) -> dict:
    """
    Calculate the updated risk after completed
    remediation actions.
    """

    if not remediation_result:
        raise ValueError(
            "remediation_result cannot be empty"
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
        if field not in remediation_result:
            raise ValueError(
                f"remediation_result is missing required field: {field}"
            )

    impact_score = float(
        remediation_result["impact_score"]
    )

    estimated_reduction = float(
        remediation_result["estimated_risk_reduction"]
    )

    total_actions = int(
        remediation_result["action_count"]
    )

    if not isinstance(
        remediation_result["actions"],
        list,
    ):
        raise ValueError(
            "remediation_result actions must be a list"
        )

    if total_actions <= 0:
        raise ValueError(
            "remediation_result must contain actions"
        )

    if completed_actions < 0:
        raise ValueError(
            "completed_actions cannot be negative"
        )

    if completed_actions > total_actions:
        raise ValueError(
            "completed_actions cannot exceed total actions"
        )

    completion_ratio = (
        completed_actions / total_actions
    )

    applied_reduction = round(
        estimated_reduction * completion_ratio,
        2,
    )

    updated_risk = round(
        max(
            0.0,
            impact_score - applied_reduction,
        ),
        2,
    )

    remaining_reduction = round(
        max(
            0.0,
            estimated_reduction - applied_reduction,
        ),
        2,
    )

    if completed_actions == 0:
        status = "pending"

    elif completed_actions < total_actions:
        status = "in_progress"

    else:
        status = "completed"

    return {
        "problem": remediation_result["problem"],
        "original_risk": impact_score,
        "estimated_total_reduction": estimated_reduction,
        "completed_actions": completed_actions,
        "total_actions": total_actions,
        "completion_percentage": round(
            completion_ratio * 100,
            2,
        ),
        "applied_risk_reduction": applied_reduction,
        "updated_risk": updated_risk,
        "remaining_potential_reduction": (
            remaining_reduction
        ),
        "status": status,
    }
def maintain_action_history(
    action: dict,
    history: list | None = None,
) -> dict:
    """
    Maintain the history of remediation action states.

    Each state transition is appended to the existing
    action history without modifying previous entries.
    """

    if not action:
        raise ValueError(
            "action cannot be empty"
        )

    required_fields = [
        "problem",
        "action",
        "priority",
        "status",
    ]

    for field in required_fields:
        if field not in action:
            raise ValueError(
                f"action is missing required field: {field}"
            )

    valid_statuses = {
        "pending",
        "in_progress",
        "completed",
    }

    if action["status"] not in valid_statuses:
        raise ValueError(
            "action contains an invalid status"
        )

    valid_priorities = {
        "HIGH",
        "MEDIUM",
        "LOW",
    }

    if action["priority"] not in valid_priorities:
        raise ValueError(
            "action contains an invalid priority"
        )

    if history is None:
        history = []

    if not isinstance(history, list):
        raise ValueError(
            "history must be a list"
        )

    updated_history = history.copy()

    updated_history.append(
        {
            "problem": action["problem"],
            "action": action["action"],
            "priority": action["priority"],
            "status": action["status"],
        }
    )

    return {
        "problem": action["problem"],
        "action": action["action"],
        "priority": action["priority"],
        "current_status": action["status"],
        "history": updated_history,
        "history_count": len(updated_history),
        "status": "history_updated",
    }