from tests.test_features import transactions, user_profiles

from defend.pipeline import DetectionPipeline


print("\n========================================")
print("       ATO-HDC FULL PIPELINE")
print("========================================")


# ============================================================
# 1. CREATE PIPELINE
# ============================================================

print("\n[1] Initializing detection pipeline...")

pipeline = DetectionPipeline(
    user_profiles
)

print("Detection pipeline initialized.")


# ============================================================
# 2. TRAIN MODELS
# ============================================================

print("\n[2] Training XGBoost and anomaly detector...")

pipeline.train()

print("Models trained successfully.")


# ============================================================
# 3. PROCESS TRANSACTIONS
# ============================================================

print("\n[3] Processing transactions...")

risk_results = pipeline.process(
    transactions
)


# ============================================================
# 4. DISPLAY RISK RESULTS
# ============================================================

print("\n[4] Risk Results:")

for result in risk_results:
    print(result)


# ============================================================
# 5. GENERATE EXPLANATIONS
# ============================================================

print("\n[5] Generating explanations...")

explanations = pipeline.explain(
    transactions,
    risk_results
)

for explanation in explanations:

    print("\n----------------------------------------")

    print(explanation)


# ============================================================
# COMPLETE
# ============================================================

print("\n========================================")
print("       FULL PIPELINE COMPLETE")
print("========================================")