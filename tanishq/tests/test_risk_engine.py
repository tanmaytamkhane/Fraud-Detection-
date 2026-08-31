import pandas as pd

from defend.risk_engine import RiskEngine


engine = RiskEngine()


test_transactions = pd.DataFrame([
    {
        "transaction_id": "TX001",
        "xgb_probability": 0.02,
        "behaviour_score": 0.01,
        "anomaly_score": 0.05
    },
    {
        "transaction_id": "TX002",
        "xgb_probability": 0.96,
        "behaviour_score": 0.85,
        "anomaly_score": 1.00
    },
    {
        "transaction_id": "TX003",
        "xgb_probability": 0.55,
        "behaviour_score": 0.45,
        "anomaly_score": 0.60
    }
])


results = engine.evaluate_dataframe(
    test_transactions
)


print("\n========== RISK ENGINE RESULTS ==========\n")

print(
    results.to_string(index=False)
)