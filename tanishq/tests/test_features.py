import pandas as pd

from defend.features import FeatureEngine
from defend.behaviour import BehaviourEngine


# User's normal behavioural profile
user_profiles = {
    "U001": {
        "devices": ["D001", "D002"],
        "beneficiaries": ["B001", "B002", "B003"],
        "locations": ["Pune"],
        "mean_amount": 1500,
        "std_amount": 500,
        "normal_hours": [18, 22]
    }
}


# Two transactions:
# TX001 = normal
# TX002 = suspicious/ATO-like
transactions = pd.DataFrame([
    {
        "transaction_id": "TX001",
        "user_id": "U001",
        "timestamp": "2026-08-24 19:30:00",
        "amount": 1400,
        "device_id": "D001",
        "location": "Pune",
        "beneficiary_id": "B001"
    },
    {
        "transaction_id": "TX002",
        "user_id": "U001",
        "timestamp": "2026-08-24 03:15:00",
        "amount": 4000,
        "device_id": "D999",
        "location": "Mumbai",
        "beneficiary_id": "B999"
    }
])


# Create feature engine
engine = FeatureEngine(user_profiles)


# Generate behavioural features
features = engine.transform(transactions)


# Display results
print("\nGenerated Behavioural Features:\n")
print(features.to_string(index=False))


# -----------------------------
# Behaviour analysis
# -----------------------------

behaviour_engine = BehaviourEngine()

behaviour_results = behaviour_engine.analyze_dataframe(
    features
)

print("\nBehaviour Analysis:\n")
print(behaviour_results.to_string(index=False))