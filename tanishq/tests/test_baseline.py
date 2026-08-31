from tests.generate_training_data import generate_dataset
from defend.baseline import XGBoostBaseline


# Generate dataset
data = generate_dataset()

print("\nDataset:")
print(data.shape)

print("\nClass distribution:")
print(data["label"].value_counts())


# Create XGBoost model
model = XGBoostBaseline()


# Train
results = model.train(data)


# Metrics
print("\n========== XGBOOST RESULTS ==========")

for metric, value in results["metrics"].items():
    print(f"{metric:10s}: {value:.4f}")


# Feature importance
print("\n========== FEATURE IMPORTANCE ==========")

importance = model.feature_importance()

print(
    importance.to_string(index=False)
)


# Sample predictions
print("\n========== SAMPLE PREDICTIONS ==========")

sample = data.drop(
    columns=["label"]
).head(10)

predictions = model.predict(sample)

print(
    predictions.to_string(index=False)
)