from tests.test_features import transactions, user_profiles

from defend.pipeline import DetectionPipeline


print("\n========================================")
print("       DETECTION PIPELINE TEST")
print("========================================")


# Create pipeline
pipeline = DetectionPipeline(
    user_profiles
)


# Train models
print("\n[1] Training models...")

pipeline.train()

print("Models trained successfully.")


# Process transactions
print("\n[2] Processing transactions...")

risk_results = pipeline.process(
    transactions
)


# Print results
print("\n[3] Risk Results...")

for result in risk_results:
    print(result)


# Generate explanations
print("\n[4] Generating explanations...")

explanations = pipeline.explain(
    transactions,
    risk_results
)


for explanation in explanations:

    print("\n----------------------------------------")
    print(explanation)


print("\n========================================")
print("       PIPELINE TEST COMPLETE")
print("========================================")