from defend.explain import ExplanationEngine


engine = ExplanationEngine()


# TX002 represents our suspicious ATO transaction.

features = {
    "new_device": 1,
    "new_beneficiary": 1,
    "amount_deviation": 5.0,
    "velocity_deviation": 3.0,
    "location_change": 1,
    "time_deviation": 5.0
}


explanation = engine.generate_text(
    transaction_id="TX002",
    features=features,
    xgb_probability=0.96,
    behaviour_score=0.85,
    anomaly_score=1.00,
    risk_score=0.939,
    risk_level="CRITICAL",
    decision="BLOCK"
)


print("\n========== EXPLANATION ==========\n")

print(explanation)