# ============================================================
# RISK SIGNAL WEIGHTS
# ============================================================

RISK_SIGNAL_WEIGHTS = {
    "amount_anomaly": 15,
    "transaction_velocity": 10,
    "failed_payment": 10,
    "transaction_frequency": 10,
    "high_value_transaction": 10,

    "refund_rate": 10,
    "dispute_rate": 10,
    "refund_trend": 5,
    "dispute_trend": 5,
    "transaction_volume": 5,

    "device_ip_anomaly": 5,
    "geographic_anomaly": 5,
    "behavior_change": 10,
}


TOTAL_WEIGHT = sum(RISK_SIGNAL_WEIGHTS.values())