"""
main.py — End-to-End HDC Fraud Detection Pipeline
===================================================
Run this file to execute the complete pipeline:
    python main.py --sample 0.05   (5% sample for fast benchmark)
    python main.py --sample 0.1    (10% sample for quick testing)
    python main.py                 (full dataset: 590K rows)
"""
import sys
import numpy as np
import time
import argparse
from pathlib import Path

# Ensure imports work
sys.path.insert(0, str(Path(__file__).parent))

from config import TRAIN_TEST_SPLIT, RANDOM_STATE, SIGNAL_NAMES
from pipeline.loader import load_data, load_simulated_data
from pipeline.feature_engineer import engineer_features
from pipeline.variant_labeler import label_variants, summarize_variants
from hdc.encoder import HDCEncoder
from hdc.model import HDCClassifier
from hdc.trainer import HDCTrainer
from evaluate.report import generate_report
from evaluate.variant_analysis import evaluate_variants, print_variant_report
from evaluate.model_comparison import compare_models, summarize_comparison


def run_pipeline(sample_frac=None, source="ieee"):
    """
    Run the full end-to-end fraud detection pipeline.

    Steps:
        1. Load and merge transaction + identity data
        2. Engineer 6 fraud signals from raw data
        3. Map fraud transactions to the 5 ATO behavioral variants
        4. Split into train/validation sets
        5. Train HDC model with iterative retraining
        6. Evaluate on validation set & per-variant analysis
        7. (simulated only) Compare HDC vs XGBoost on same validation split
    
    Args:
        sample_frac: Fraction of data to use (e.g. 0.05 for 5%). None = full dataset.
        source: "ieee" for raw IEEE-CIS data, "simulated" for Person 2's ATO dataset.

    Returns:
        dict with evaluation metrics
    """
    total_start = time.time()

    # ─── Step 1: Load Data ───
    print("=" * 60)
    print("  STEP 1: LOADING DATA")
    print("=" * 60)
    if source == "simulated":
        print("  Source: Person 2's simulated ATO dataset")
        df = load_simulated_data(sample_frac=sample_frac)
        # Stash real variant_id ground truth before feature engineering
        real_variant_ids = df["variant_id"].values.copy()
    else:
        df = load_data(sample_frac=sample_frac)

    # ─── Step 2: Engineer Features ───
    print("\n" + "=" * 60)
    print("  STEP 2: ENGINEERING FEATURES")
    print("=" * 60)
    df_features = engineer_features(df)

    # Extract signal matrix (numpy array) and labels
    signal_matrix = df_features[SIGNAL_NAMES].values.astype(np.float32)
    labels = df_features["isFraud"].values.astype(np.int32)

    print(f"\n  Signal matrix shape: {signal_matrix.shape}")
    print(f"  Labels: {len(labels):,} total, {labels.sum():,} fraud ({labels.mean()*100:.2f}%)")

    # ─── Step 3: ATO Variant Mapping ───
    print("\n" + "=" * 60)
    print("  STEP 3: MAPPING TO 5 BEHAVIORAL ATO VARIANTS")
    print("=" * 60)
    if source == "simulated":
        print("  Using real variant_id ground truth from Person 2's dataset")
        all_variant_labels = np.array(real_variant_ids, dtype=object)
    else:
        all_variant_labels = label_variants(signal_matrix, labels)
    variant_dist = summarize_variants(all_variant_labels)
    print(variant_dist.to_string(index=False))

    # ─── Step 4: Train/Validation Split ───
    print("\n" + "=" * 60)
    print("  STEP 4: SPLITTING DATA (80/20)")
    print("=" * 60)
    rng = np.random.RandomState(RANDOM_STATE)
    indices = rng.permutation(len(labels))
    split_idx = int(len(labels) * (1 - TRAIN_TEST_SPLIT))

    train_idx = indices[:split_idx]
    val_idx = indices[split_idx:]

    X_train, y_train = signal_matrix[train_idx], labels[train_idx]
    X_val, y_val = signal_matrix[val_idx], labels[val_idx]
    val_variants = all_variant_labels[val_idx]

    print(f"  Train: {len(y_train):,} samples ({y_train.sum():,} fraud)")
    print(f"  Val:   {len(y_val):,} samples ({y_val.sum():,} fraud)")

    # ─── Step 5: Train HDC Model ───
    print("\n" + "=" * 60)
    print("  STEP 5: TRAINING HDC MODEL")
    print("=" * 60)
    encoder = HDCEncoder()
    classifier = HDCClassifier()
    trainer = HDCTrainer(encoder=encoder, classifier=classifier)
    history = trainer.train(X_train, y_train)

    # ─── Step 6: Evaluate Model & Variants ───
    print("\n" + "=" * 60)
    print("  STEP 6: EVALUATING ON VALIDATION SET")
    print("=" * 60)

    # Encode validation set
    print(f"\n  Encoding {len(y_val):,} validation transactions into 10,000-D hypervectors...")
    X_val_encoded = encoder.encode_batch(X_val)

    # Predict
    predictions, similarity_scores = classifier.predict_batch(X_val_encoded)

    # Get fraud probability scores for AUC-ROC
    fraud_scores = classifier.get_fraud_score(X_val_encoded)

    # Generate overall classification report
    metrics = generate_report(
        y_true=y_val,
        y_pred=predictions,
        scores=fraud_scores,
        signal_matrix=X_val,
        labels=y_val,
    )

    # Evaluate per-variant detection rate
    variant_df = evaluate_variants(
        y_true=y_val,
        y_pred=predictions,
        variant_labels=val_variants
    )
    print_variant_report(variant_df)

    # ─── Step 7: HDC vs XGBoost Comparison (simulated only) ───
    if source == "simulated":
        print("\n" + "=" * 60)
        print("  STEP 7: HDC vs XGBoost COMPARISON")
        print("=" * 60)

        from defend.adapter import SignalAdapter
        from defend.baseline import XGBoostBaseline

        adapter = SignalAdapter()

        # Build defend-schema DataFrames for training and validation
        # using the SAME train/val split indices from Step 4
        import pandas as pd
        train_signals_df = pd.DataFrame(X_train, columns=SIGNAL_NAMES)
        val_signals_df = pd.DataFrame(X_val, columns=SIGNAL_NAMES)

        train_defend_df = adapter.team_to_defend_df(train_signals_df)
        train_defend_df["label"] = y_train

        val_defend_df = adapter.team_to_defend_df(val_signals_df)

        # Train XGBoost on the same training data
        xgb = XGBoostBaseline()
        xgb.train(train_defend_df)

        # Predict on the same validation data
        xgb_result = xgb.predict(val_defend_df)
        xgb_predictions = xgb_result["prediction"].values
        xgb_probabilities = xgb_result["ato_probability"].values

        # Compare HDC vs XGBoost
        comparison_df = compare_models(
            y_true=y_val,
            hdc_predictions=predictions,
            hdc_scores=fraud_scores,
            xgb_predictions=xgb_predictions,
            xgb_probabilities=xgb_probabilities,
        )
        summarize_comparison(comparison_df, y_val)

    elapsed = time.time() - total_start
    print(f"  Total pipeline time: {elapsed:.1f} seconds")

    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HDC Fraud Detection Pipeline")
    parser.add_argument(
        "--sample",
        type=float,
        default=None,
        help="Fraction of data to use (e.g. 0.05 for 5%%). None = full dataset.",
    )
    parser.add_argument(
        "--source",
        choices=["ieee", "simulated"],
        default="ieee",
        help="Data source: 'ieee' for raw IEEE-CIS data (default), "
             "'simulated' for Person 2's ATO dataset.",
    )
    args = parser.parse_args()

    print("\n" + "#" * 60)
    print("  HDC FRAUD DETECTION — MASTERCARD HACKATHON")
    print("#" * 60)
    print(f"  Sample fraction: {args.sample or 'FULL DATASET'}")
    print(f"  Data source:     {args.source}")
    print()

    metrics = run_pipeline(sample_frac=args.sample, source=args.source)

    print("\n" + "#" * 60)
    print("  FINAL RESULTS SUMMARY")
    print("#" * 60)
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  F1 Score:  {metrics['f1_score']:.4f}")
    if "auc_roc" in metrics:
        print(f"  AUC-ROC:   {metrics['auc_roc']:.4f}")
    print("#" * 60 + "\n")
