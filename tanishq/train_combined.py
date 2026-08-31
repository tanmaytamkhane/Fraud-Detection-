"""
train_combined.py — Train HDC + XGBoost binary fraud/legit classifiers on
REAL IEEE-CIS legit transactions + synthetic ATO-V1..V5 fraud, compare, plot.
=============================================================================
This is the fix for the core gap in the project: simulate/ato_dataset.csv is
100% fraud, so nothing trained on it alone can ever learn "is this fraud at
all" — only "which attack variant is this, given it's already fraud." This
script merges:
  - REAL legit transactions (isFraud == 0) from the IEEE-CIS Kaggle dataset
    (data/train_transaction.csv + data/train_identity.csv, loaded via
    pipeline/loader.py)
  - The 25,398 synthetic ATO fraud rows in simulate/ato_dataset.csv (all
    isFraud == 1, with ground-truth variant_id ATO-V1..V5)
into one binary fraud/legit dataset, engineers the 6 signals, and trains
BOTH an HDC prototype classifier and an XGBoost classifier to answer the
actual binary question.

MEMORY NOTE: this container has ~3.9GB RAM and 1 CPU, no swap. A raw
10,000-D HDC encoding of the full ~590K-row IEEE-CIS legit pool (let alone
590K+25K combined) needs tens of GB just for one encoded float32 matrix —
that's what got OOM-killed before. This script fixes that by:
  1. Filtering to legit rows and *sampling* them down to --legit-sample
     rows (default 20,000) before anything touches the HDC encoder.
  2. Disabling the config's 3x fraud-oversample duplication for this run
     specifically (see NOTE in main()) since our sampled combined set is
     already fraud-heavy — duplicating the fraud rows further would just
     double memory for no benefit.
  3. Explicitly deleting large intermediates and reporting peak RSS at each
     stage so a future run can be tuned to whatever machine it's on.

Usage:
    python train_combined.py                      # defaults: 20,000 legit rows
    python train_combined.py --legit-sample 40000  # bigger machine
    python train_combined.py --sample 0.5          # also subsample the final combined set
"""
import sys
import os
import gc
import json
import time
import resource
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    roc_curve, roc_auc_score, confusion_matrix,
    precision_score, recall_score, f1_score, accuracy_score
)
from sklearn.model_selection import train_test_split
import xgboost as xgb

sys.path.insert(0, str(Path(__file__).parent))

import config as cfg
from config import TRAIN_TEST_SPLIT, RANDOM_STATE, SIGNAL_NAMES, HDC_RETRAIN_EPOCHS
from pipeline.loader import load_data
from pipeline.feature_engineer import engineer_features
from pipeline.variant_labeler import VARIANT_NAMES
import hdc.trainer as hdc_trainer_module
from hdc.encoder import HDCEncoder
from hdc.model import HDCClassifier
from hdc.trainer import HDCTrainer
from evaluate.report import generate_report
from evaluate.variant_analysis import evaluate_variants, print_variant_report

ATO_PATH = Path(__file__).parent / "simulate" / "ato_dataset.csv"
OUT_DIR = Path(__file__).parent / "results"
MODELS_DIR = Path(__file__).parent / "models"
OUT_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

VARIANT_IDS = ["ATO-V1", "ATO-V2", "ATO-V3", "ATO-V4", "ATO-V5"]


def peak_rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def log_mem(label):
    print(f"  [mem] {label}: peak RSS so far = {peak_rss_mb():,.0f} MB")


def load_real_legit(legit_sample_n, seed=RANDOM_STATE):
    """Loads the full real IEEE-CIS train set, keeps ONLY legit (isFraud==0)
    rows, then samples down to legit_sample_n rows. Filtering happens before
    anything expensive so we never hold more than we need."""
    print(f"Loading real IEEE-CIS data (train_transaction.csv + train_identity.csv)...")
    df = load_data(sample_frac=None)
    legit = df[df["isFraud"] == 0].copy()
    del df
    gc.collect()
    print(f"  Real legit rows available: {len(legit):,}")
    if legit_sample_n is not None and legit_sample_n < len(legit):
        legit = legit.sample(n=legit_sample_n, random_state=seed).reset_index(drop=True)
    print(f"  Real legit rows sampled for training: {len(legit):,}")
    return legit


def load_synthetic_fraud():
    print(f"Loading synthetic ATO fraud rows from {ATO_PATH} ...")
    fraud = pd.read_csv(ATO_PATH)
    print(f"  Synthetic fraud rows: {len(fraud):,} (all isFraud==1)")
    print(fraud["variant_id"].value_counts().rename("count").to_string())
    return fraud


def build_combined_dataset(legit_sample_n, seed=RANDOM_STATE):
    """Merges real legit + synthetic fraud into one binary dataset.
    Returns (df_combined, variant_truth) where variant_truth[i] is the
    ground-truth ATO-V1..V5 label for fraud rows and 'LEGITIMATE' for
    real legit rows (NOT re-derived from prototype distance — we have the
    actual simulator labels for the fraud rows, so we use them directly)."""
    legit = load_real_legit(legit_sample_n, seed=seed)
    fraud = load_synthetic_fraud()

    legit["is_synthetic"] = False
    legit["attack_id"] = None
    legit["variant_id"] = "LEGITIMATE"

    combined = pd.concat([legit, fraud], ignore_index=True, sort=False)
    del legit, fraud
    gc.collect()

    variant_truth = combined["variant_id"].fillna("LEGITIMATE").values
    print(f"\nCombined dataset: {len(combined):,} rows "
          f"({int(combined['isFraud'].sum()):,} fraud / "
          f"{int((combined['isFraud']==0).sum()):,} legit, "
          f"{combined['isFraud'].mean()*100:.1f}% fraud rate)")
    print("  NOTE: this fraud rate is much higher than IEEE-CIS's real ~3.5%,")
    print("  because we can only afford a small legit sample on this machine's")
    print("  RAM budget. See the run summary at the end for what this means")
    print("  for how to read these metrics.")
    return combined, variant_truth


def train_xgb(X_train, y_train, X_val, y_val):
    print("\n  Training XGBoost classifier on the 6 engineered signals...")
    scale_pos_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1)
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        scale_pos_weight=scale_pos_weight,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    return model


def summarize_llm(hdc_metrics, xgb_metrics, variant_df):
    import os
    prompt_facts = (
        f"HDC — Acc {hdc_metrics['accuracy']:.3f}, Prec {hdc_metrics['precision']:.3f}, "
        f"Rec {hdc_metrics['recall']:.3f}, F1 {hdc_metrics['f1_score']:.3f}, AUC {hdc_metrics.get('auc_roc', 0):.3f}. "
        f"XGBoost — Acc {xgb_metrics['accuracy']:.3f}, Prec {xgb_metrics['precision']:.3f}, "
        f"Rec {xgb_metrics['recall']:.3f}, F1 {xgb_metrics['f1_score']:.3f}, AUC {xgb_metrics.get('auc_roc', 0):.3f}."
    )
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        best = "XGBoost" if xgb_metrics.get("auc_roc", 0) >= hdc_metrics.get("auc_roc", 0) else "HDC"
        return (
            f"[template fallback — set ANTHROPIC_API_KEY for an LLM-written version]\n"
            f"{prompt_facts}\n{best} has the higher AUC-ROC on this run."
        )
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key, timeout=15.0)
        resp = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=200,
            messages=[{"role": "user", "content":
                f"You are a fraud-ML analyst. In 3-4 sentences, compare these two fraud "
                f"detection models for a hackathon report: {prompt_facts} "
                f"Be concrete about which model wins on which metric and why that might be."}],
        )
        return resp.content[0].text.strip()
    except Exception as e:
        return f"[LLM call failed: {e}]\n{prompt_facts}"


def plot_results(y_val, hdc_scores, hdc_preds, xgb_scores, xgb_preds, variant_df):
    fig, ax = plt.subplots(figsize=(6, 5))
    for name, scores in [("HDC", hdc_scores), ("XGBoost", xgb_scores)]:
        fpr, tpr, _ = roc_curve(y_val, scores)
        auc = roc_auc_score(y_val, scores)
        ax.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve — HDC vs XGBoost (real legit + synthetic ATO fraud)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "roc_comparison.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for ax, name, preds in [(axes[0], "HDC", hdc_preds), (axes[1], "XGBoost", xgb_preds)]:
        cm = confusion_matrix(y_val, preds)
        ax.imshow(cm, cmap="Blues")
        ax.set_title(f"{name} Confusion Matrix")
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        ax.set_xticks([0, 1]); ax.set_xticklabels(["Legit", "Fraud"])
        ax.set_yticks([0, 1]); ax.set_yticklabels(["Legit", "Fraud"])
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center",
                         color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "confusion_matrices.png", dpi=150)
    plt.close(fig)

    variants = variant_df["Variant ID"].tolist()
    hdc_rates = [float(v.strip("%")) for v in variant_df["HDC Detection Rate"]]
    xgb_rates = [float(v.strip("%")) for v in variant_df["XGBoost Detection Rate"]]
    x = np.arange(len(variants))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width / 2, hdc_rates, width, label="HDC")
    ax.bar(x + width / 2, xgb_rates, width, label="XGBoost")
    ax.set_xticks(x)
    ax.set_xticklabels(variants)
    ax.set_ylabel("Detection Rate (%)")
    ax.set_title("Per-Variant Detection Rate — HDC vs XGBoost (ground-truth variant_id)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "variant_detection_comparison.png", dpi=150)
    plt.close(fig)


def plot_feature_importance(model, signal_names):
    fig, ax = plt.subplots(figsize=(6, 4))
    importances = model.feature_importances_
    order = np.argsort(importances)
    ax.barh(np.array(signal_names)[order], importances[order], color="#2b6cb0")
    ax.set_title("XGBoost Feature Importance (6 HDC signals) — binary fraud/legit")
    ax.set_xlabel("Importance")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "xgb_feature_importance.png", dpi=150)
    plt.close(fig)


def save_models(hdc_clf, encoder, xgb_model, run_meta):
    """Persists binary fraud/legit models to models/, kept separate from
    the variant-classifier artifacts in results_variant_clf/."""
    np.savez(
        MODELS_DIR / "hdc_binary_prototypes.npz",
        prototypes=hdc_clf.prototypes,
        threshold=np.array([hdc_clf.threshold], dtype=np.float32),
        dim=np.array([hdc_clf.dim]),
    )
    encoder_meta = {
        "dim": encoder.dim,
        "num_levels": encoder.num_levels,
        "num_signals": encoder.num_signals,
        "seed": cfg.HDC_SEED,
        "note": "HDCEncoder is deterministic given (dim, num_levels, num_signals, seed) "
                "via config.HDC_SEED — reconstruct with HDCEncoder(**these kwargs) rather "
                "than trying to serialize the random level/signal hypervectors.",
    }
    with open(MODELS_DIR / "hdc_binary_encoder_meta.json", "w") as f:
        json.dump(encoder_meta, f, indent=2)

    xgb_model.save_model(str(MODELS_DIR / "xgb_binary_model.json"))

    with open(MODELS_DIR / "binary_model_run_meta.json", "w") as f:
        json.dump(run_meta, f, indent=2, default=str)

    print(f"  Saved binary models to {MODELS_DIR}/:")
    print(f"    - hdc_binary_prototypes.npz + hdc_binary_encoder_meta.json")
    print(f"    - xgb_binary_model.json")
    print(f"    - binary_model_run_meta.json")


def main(legit_sample_n, sample_frac, hdc_epochs, disable_oversample):
    t0 = time.time()

    print("=" * 70)
    print("  STEP 1: LOAD & MERGE REAL LEGIT + SYNTHETIC FRAUD")
    print("=" * 70)
    df, variant_truth = build_combined_dataset(legit_sample_n)
    log_mem("after building combined dataset")

    if sample_frac is not None:
        idx = df.sample(frac=sample_frac, random_state=RANDOM_STATE).index
        df = df.loc[idx].reset_index(drop=True)
        variant_truth = variant_truth[idx]
        print(f"  --sample {sample_frac} applied -> {len(df):,} rows")

    print("\n" + "=" * 70)
    print("  STEP 2: ENGINEER 6 SIGNALS")
    print("=" * 70)
    df_features = engineer_features(df)
    signal_matrix = df_features[SIGNAL_NAMES].values.astype(np.float32)
    labels = df_features["isFraud"].values.astype(np.int32)
    del df, df_features
    gc.collect()
    log_mem("after feature engineering")

    print("\n" + "=" * 70)
    print("  STEP 3: TRAIN/VAL SPLIT (80/20, stratified by isFraud)")
    print("=" * 70)
    all_idx = np.arange(len(labels))
    train_idx, val_idx = train_test_split(
        all_idx, test_size=TRAIN_TEST_SPLIT, random_state=RANDOM_STATE, stratify=labels
    )
    X_train, y_train = signal_matrix[train_idx], labels[train_idx]
    X_val, y_val = signal_matrix[val_idx], labels[val_idx]
    val_variants = variant_truth[val_idx]
    print(f"  Train: {len(y_train):,} ({y_train.sum():,} fraud, {y_train.mean()*100:.1f}%)  |  "
          f"Val: {len(y_val):,} ({y_val.sum():,} fraud, {y_val.mean()*100:.1f}%)")

    # ---------------- HDC ----------------
    print("\n" + "=" * 70)
    print("  STEP 4: TRAIN HDC")
    print("=" * 70)
    if disable_oversample:
        # NOTE (judgment call — flagged to user): config.FRAUD_OVERSAMPLE_RATIO=3.0
        # assumes the real-world ~3.5% fraud rate and duplicates fraud rows to
        # get the model to pay attention to the minority class. Here fraud is
        # already the dominant class (see fraud rate printed above) because we
        # can only afford a small legit sample on this machine's RAM. Applying
        # 3x oversampling on top of that would both push the problem further
        # from realistic imbalance AND roughly double peak memory during HDC
        # training (the trainer duplicates the encoded fraud rows in-memory).
        # So for this run we disable it. If you retrain on a bigger legit
        # sample that restores realistic ~3.5% imbalance, re-enable it.
        hdc_trainer_module.FRAUD_OVERSAMPLE_RATIO = 1.0
        print("  [judgment call] Disabling fraud oversampling for this run — "
              "see comment in main() for why.")

    encoder = HDCEncoder()
    hdc_clf = HDCClassifier()
    trainer = HDCTrainer(encoder=encoder, classifier=hdc_clf)
    trainer.train(X_train, y_train, retrain_epochs=hdc_epochs)
    log_mem("after HDC training")

    X_val_enc = encoder.encode_batch(X_val)
    hdc_preds, _ = hdc_clf.predict_batch(X_val_enc)
    hdc_scores = hdc_clf.get_fraud_score(X_val_enc)
    hdc_metrics = generate_report(y_true=y_val, y_pred=hdc_preds, scores=hdc_scores,
                                   signal_matrix=X_val, labels=y_val)
    hdc_variant_df = evaluate_variants(y_true=y_val, y_pred=hdc_preds, variant_labels=val_variants)
    del X_val_enc
    gc.collect()
    log_mem("after HDC validation")

    # ---------------- XGBoost ----------------
    print("\n" + "=" * 70)
    print("  STEP 5: TRAIN XGBOOST")
    print("=" * 70)
    xgb_model = train_xgb(X_train, y_train, X_val, y_val)
    xgb_preds = xgb_model.predict(X_val)
    xgb_scores = xgb_model.predict_proba(X_val)[:, 1]
    xgb_metrics = {
        "accuracy": accuracy_score(y_val, xgb_preds),
        "precision": precision_score(y_val, xgb_preds, zero_division=0),
        "recall": recall_score(y_val, xgb_preds, zero_division=0),
        "f1_score": f1_score(y_val, xgb_preds, zero_division=0),
        "auc_roc": roc_auc_score(y_val, xgb_scores),
    }
    xgb_variant_df = evaluate_variants(y_true=y_val, y_pred=xgb_preds, variant_labels=val_variants)

    print(f"  XGBoost — Acc: {xgb_metrics['accuracy']:.4f}  Prec: {xgb_metrics['precision']:.4f}  "
          f"Rec: {xgb_metrics['recall']:.4f}  F1: {xgb_metrics['f1_score']:.4f}  AUC: {xgb_metrics['auc_roc']:.4f}")
    print_variant_report(xgb_variant_df)

    combined = hdc_variant_df[["Variant ID", "Variant Description", "Total Fraud Cases"]].copy()
    combined["HDC Detection Rate"] = hdc_variant_df["Detection Rate"]
    combined["XGBoost Detection Rate"] = xgb_variant_df["Detection Rate"]

    print("\n" + "=" * 70)
    print("  STEP 6: GENERATE GRAPHS")
    print("=" * 70)
    plot_results(y_val, hdc_scores, hdc_preds, xgb_scores, xgb_preds, combined)
    plot_feature_importance(xgb_model, SIGNAL_NAMES)
    print(f"  Saved graphs to {OUT_DIR}/")

    print("\n" + "=" * 70)
    print("  STEP 7: SAVE MODELS")
    print("=" * 70)
    run_meta = {
        "legit_sample_n": legit_sample_n,
        "sample_frac": sample_frac,
        "n_rows_total": int(len(train_idx) + len(val_idx)),
        "n_train": len(y_train),
        "n_val": len(y_val),
        "fraud_rate_pct": float(labels.mean() * 100),
        "oversample_disabled": disable_oversample,
        "hdc_epochs": hdc_epochs,
        "hdc_dimensions": cfg.HDC_DIMENSIONS,
    }
    save_models(hdc_clf, encoder, xgb_model, run_meta)

    print("\n" + "=" * 70)
    print("  STEP 8: LLM SUMMARY")
    print("=" * 70)
    summary_text = summarize_llm(hdc_metrics, xgb_metrics, combined)
    print(summary_text)

    results = {
        "n_rows_total": int(len(train_idx) + len(val_idx)),
        "n_train": len(y_train),
        "n_val": len(y_val),
        "legit_sample_n": legit_sample_n,
        "fraud_rate_pct": float(labels.mean() * 100),
        "oversample_disabled": disable_oversample,
        "hdc_metrics": {k: float(v) for k, v in hdc_metrics.items() if isinstance(v, (int, float, np.floating))},
        "xgb_metrics": xgb_metrics,
        "variant_comparison": combined.to_dict(orient="records"),
        "llm_summary": summary_text,
        "peak_rss_mb": peak_rss_mb(),
        "elapsed_seconds": time.time() - t0,
    }
    with open(OUT_DIR / "binary_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    combined.to_csv(OUT_DIR / "binary_variant_comparison.csv", index=False)

    print("\n" + "#" * 70)
    print("  FINAL COMPARISON — BINARY FRAUD/LEGIT (real legit + synthetic ATO fraud)")
    print("#" * 70)
    print(f"  {'Metric':<12}{'HDC':>10}{'XGBoost':>12}")
    for m in ["accuracy", "precision", "recall", "f1_score", "auc_roc"]:
        print(f"  {m:<12}{hdc_metrics.get(m, 0):>10.4f}{xgb_metrics.get(m, 0):>12.4f}")
    print(f"\n  Legit sample used: {legit_sample_n:,} rows (real IEEE-CIS)")
    print(f"  Fraud rows used:   25,398 (full simulate/ato_dataset.csv)")
    print(f"  Combined fraud rate: {labels.mean()*100:.1f}% (vs ~3.5% in real IEEE-CIS — see notes above)")
    print(f"  Peak RSS: {peak_rss_mb():,.0f} MB")
    print(f"  Total time: {time.time()-t0:.1f}s")
    print(f"  Results saved to: {OUT_DIR}/   Models saved to: {MODELS_DIR}/")
    print("#" * 70)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--legit-sample", type=int, default=20000,
                         help="Number of REAL legit rows to sample from IEEE-CIS "
                              "(default 20,000 — sized for a ~4GB RAM / 1-CPU box; "
                              "raise this on a bigger machine).")
    parser.add_argument("--sample", type=float, default=None,
                         help="Additionally subsample the final combined set by this fraction (for a quick smoke test).")
    parser.add_argument("--hdc-epochs", type=int, default=HDC_RETRAIN_EPOCHS,
                         help="HDC retrain epochs (default from config.py).")
    parser.add_argument("--no-disable-oversample", action="store_true",
                         help="Keep config's 3x fraud oversampling instead of disabling it for this run.")
    args = parser.parse_args()
    main(
        legit_sample_n=args.legit_sample,
        sample_frac=args.sample,
        hdc_epochs=args.hdc_epochs,
        disable_oversample=not args.no_disable_oversample,
    )
