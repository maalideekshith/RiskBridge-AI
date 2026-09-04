def collect_relevant_transactions(
    merchant_id: int,
    transactions: list,
) -> dict:
    """
    Collect transactions relevant to a risk-review case.
    """

    if merchant_id <= 0:
        raise ValueError(
            "merchant_id must be greater than zero"
        )

    if not isinstance(transactions, list):
        raise ValueError(
            "transactions must be a list"
        )

    relevant_transactions = []

    for transaction in transactions:
        if not isinstance(transaction, dict):
            raise ValueError(
                "each transaction must be a dictionary"
            )

        transaction_merchant_id = transaction.get(
            "merchant_id"
        )

        if transaction_merchant_id == merchant_id:
            relevant_transactions.append(
                transaction
            )

    return {
        "merchant_id": merchant_id,
        "transactions": relevant_transactions,
        "transaction_count": len(
            relevant_transactions
        ),
        "status": "transactions_collected",
    }
def collect_refund_information(
    merchant_id: int,
    refunds: list,
) -> dict:
    """
    Collect refund information relevant to a merchant.
    """

    if merchant_id <= 0:
        raise ValueError(
            "merchant_id must be greater than zero"
        )

    if not isinstance(refunds, list):
        raise ValueError(
            "refunds must be a list"
        )

    relevant_refunds = [
        refund
        for refund in refunds
        if isinstance(refund, dict)
        and refund.get("merchant_id") == merchant_id
    ]

    return {
        "merchant_id": merchant_id,
        "refunds": relevant_refunds,
        "refund_count": len(relevant_refunds),
        "status": "refunds_collected",
    }
def collect_dispute_information(
    merchant_id: int,
    disputes: list,
) -> dict:
    """
    Collect dispute information relevant to a merchant
    for risk-review evidence.
    """

    if merchant_id <= 0:
        raise ValueError(
            "merchant_id must be greater than zero"
        )

    if not isinstance(disputes, list):
        raise ValueError(
            "disputes must be a list"
        )

    relevant_disputes = []

    for dispute in disputes:
        if not isinstance(dispute, dict):
            raise ValueError(
                "Each dispute must be a dictionary"
            )

        if "merchant_id" not in dispute:
            raise ValueError(
                "dispute is missing merchant_id"
            )

        if dispute["merchant_id"] == merchant_id:
            relevant_disputes.append(dispute)

    return {
        "merchant_id": merchant_id,
        "disputes": relevant_disputes,
        "dispute_count": len(relevant_disputes),
        "status": "disputes_collected",
    }
def collect_merchant_policies(
    merchant_id: int,
    policies: list,
) -> dict:
    """
    Collect merchant policies relevant to a risk-review case.
    """

    if merchant_id <= 0:
        raise ValueError(
            "merchant_id must be greater than zero"
        )

    if not isinstance(policies, list):
        raise ValueError(
            "policies must be a list"
        )

    relevant_policies = []

    for policy in policies:
        if not isinstance(policy, dict):
            raise ValueError(
                "Each policy must be a dictionary"
            )

        if "merchant_id" not in policy:
            raise ValueError(
                "policy is missing merchant_id"
            )

        if policy["merchant_id"] == merchant_id:
            relevant_policies.append(policy)

    return {
        "merchant_id": merchant_id,
        "policies": relevant_policies,
        "policy_count": len(relevant_policies),
        "status": "policies_collected",
    }
def collect_risk_signals(
    merchant_id: int,
    risk_signals: list,
) -> dict:
    """
    Collect risk signals relevant to a risk-review case.
    """

    if merchant_id <= 0:
        raise ValueError(
            "merchant_id must be greater than zero"
        )

    if not isinstance(risk_signals, list):
        raise ValueError(
            "risk_signals must be a list"
        )

    relevant_signals = []

    for signal in risk_signals:
        if not isinstance(signal, dict):
            raise ValueError(
                "Each risk signal must be a dictionary"
            )

        if "merchant_id" not in signal:
            raise ValueError(
                "risk signal is missing merchant_id"
            )

        if signal["merchant_id"] == merchant_id:
            relevant_signals.append(signal)

    return {
        "merchant_id": merchant_id,
        "risk_signals": relevant_signals,
        "risk_signal_count": len(
            relevant_signals
        ),
        "status": "risk_signals_collected",
    }