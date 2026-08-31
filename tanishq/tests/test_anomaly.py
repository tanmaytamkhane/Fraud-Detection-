from tests.generate_training_data import generate_dataset
from defend.anomaly import AnomalyDetector


# Generate temporary dataset
data = generate_dataset()

print("\nDataset:")
print(data.shape)


# Create anomaly detector
detector = AnomalyDetector(
    contamination=0.05
)


# Train only on legitimate behaviour
detector.fit(data)

print("\nAnomaly detector trained.")


# Analyze transactions
results = detector.analyze(data)

print("\n========== ANOMALY RESULTS ==========")

print(
    results.head(20).to_string(index=False)
)


# Compare anomaly rates by actual label
combined = data.copy()

combined["anomaly_score"] = (
    results["anomaly_score"].values
)

combined["is_anomalous"] = (
    results["is_anomalous"].values
)


print("\n========== ANOMALY RATE BY CLASS ==========")

print(
    combined.groupby("label")["is_anomalous"]
    .mean()
)