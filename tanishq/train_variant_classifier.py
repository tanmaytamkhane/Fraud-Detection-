"""
train_variant_classifier.py — HDC + XGBoost 5-class ATO variant classifier
=============================================================================
Trains on the FULL simulate/ato_dataset.csv (25,398 rows, ground-truth
`variant_id` column ATO-V1..V5). This is a multiclass task: "given the
6 signals, which ATO variant is this attack?" — no legit-transaction
data required (unlike the binary fraud/legit pipeline in main.py, which
needs the IEEE-CIS raw files that aren't bundled here).

Usage:
    python train_variant_classifier.py
    python train_variant_classifier.py --sample 0.5
"""
import sys
import json
import time
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report
)
from sklearn.model_selection import train_test_split
import xgboost as xgb

sys.path.insert(0, str(Path(__file__).parent))

from config import SIGNAL_NAMES, RANDOM_STATE, HDC_RETRAIN_EPOCHS
from pipeline.feature_engineer import engineer_features
from pipeline.variant_labeler import VARIANT_NAMES
from hdc.encoder import HDCEncoder

DATA_PATH = Path(__file__).parent / "simulate" / "ato_dataset.csv"
OUT_DIR = Path(__file__).parent / "results_variant_clf"
OUT_DIR.mkdir(exist_ok=True)

CLASSES = ["ATO-V1", "ATO-V2", "ATO-V3", "ATO-V4", "ATO-V5"]
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}


class MulticlassHDCClassifier:
    """Prototype-based HDC classifier generalized to N classes.
    Argmax cosine similarity + perceptron-style retraining."""

    def __init__(self, dim, num_classes, learning_rate=1.0, seed=RANDOM_STATE):
        self.dim = dim
        self.num_classes = num_classes
        self.learning_rate = learning_rate
        self.prototypes = np.zeros((num_classes, dim), dtype=np.float32)

    def initial_train(self, encoded_hvs, labels):
        for c in range(self.num_classes):
            mask = labels == c
            if mask.sum() > 0:
                self.prototypes[c] = np.sum(encoded_hvs[mask], axis=0)

    def _cosine_sims(self, encoded_hvs):
        proto_norms = np.maximum(np.linalg.norm(self.prototypes, axis=1, keepdims=True), 1e-10)
        norm_protos = self.prototypes / proto_norms
        hv_norms = np.maximum(np.linalg.norm(encoded_hvs, axis=1, keepdims=True), 1e-10)
        norm_hvs = encoded_hvs / hv_norms
        return norm_hvs @ norm_protos.T  # (n, num_classes)

    def predict(self, encoded_hvs):
        sims = self._cosine_sims(encoded_hvs)
        return np.argmax(sims, axis=1), sims

    def retrain_step(self, encoded_hvs, labels):
        preds, _ = self.predict(encoded_hvs)
        wrong = preds != labels
        n_errors = wrong.sum()
        for i in np.where(wrong)[0]:
            self.prototypes[labels[i]] += self.learning_rate * encoded_hvs[i]
            self.prototypes[preds[i]] -= self.learning_rate * encoded_hvs[i]
        return n_errors

    def train(self, X_signals, y, encoder, epochs=HDC_RETRAIN_EPOCHS):
        print(f"  Encoding {len(y):,} transactions into {self.dim}-D hypervectors...")
        encoded = encoder.encode_batch(X_signals)
        self.initial_train(encoded, y)
        preds, _ = self.predict(encoded)
        acc = (preds == y).mean()
        print(f"  Initial train accuracy: {acc:.4f}")
        for epoch in range(epochs):
            errors = self.retrain_step(encoded, y)
            if (epoch + 1) % 5 == 0 or epoch == 0:
                preds, _ = self.predict(encoded)
                acc = (preds == y).mean()
                print(f"  Epoch {epoch+1:3d}/{epochs} — errors: {errors:,}, acc: {acc:.4f}")
        return encoded


def load_dataset(sample_frac=None):
    print(f"Loading dataset from {DATA_PATH} ...")
    df = pd.read_csv(DATA_PATH)
    if sample_frac is not None:
        df = df.sample(frac=sample_frac, random_state=RANDOM_STATE)
    print(f"Total rows: {len(df):,}")
    print(df["variant_id"].value_counts().rename("count").to_string())
    return df


def summarize_llm(hdc_report, xgb_report):
    import os
    hdc_acc = hdc_report["accuracy"]
    xgb_acc = xgb_report["accuracy"]
    facts = f"HDC overall accuracy {hdc_acc:.3f}. XGBoost overall accuracy {xgb_acc:.3f}. "
    facts += "Per-class F1 — HDC: " + ", ".join(
        f"{c}={hdc_report[c]['f1-score']:.2f}" for c in CLASSES) + ". "
    facts += "XGBoost: " + ", ".join(
        f"{c}={xgb_report[c]['f1-score']:.2f}" for c in CLASSES) + "."
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        winner = "XGBoost" if xgb_acc >= hdc_acc else "HDC"
        return (
            "[template fallback — set ANTHROPIC_API_KEY for an LLM-written version]\n"
            f"{facts}\n{winner} wins on overall accuracy. Expect both models to struggle most on "
            "ATO-V4 (Subtle Deviation) since it's designed to be the hardest, low-signal variant, "
            "and to do best on ATO-V1/V3 since those are the 'loud' variants with strong signal "
            "separation from the others."
        )
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key, timeout=15.0)
        resp = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=220,
            messages=[{"role": "user", "content":
                f"You are a fraud-ML analyst writing for a hackathon report. In 3-4 sentences, "
                f"compare these two 5-class ATO-variant classifiers: {facts} "
                f"Note which variant each model confuses most and why that might be."}],
        )
        return resp.content[0].text.strip()
    except Exception as e:
        return f"[LLM call failed: {e}]\n{facts}"


def plot_confusion(cm, title, path):
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(CLASSES))); ax.set_xticklabels(CLASSES, rotation=45)
    ax.set_yticks(range(len(CLASSES))); ax.set_yticklabels(CLASSES)
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
    ax.set_title(title)
    for i in range(len(CLASSES)):
        for j in range(len(CLASSES)):
            ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center",
                     color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=8)
    fig.colorbar(im)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_f1_comparison(hdc_report, xgb_report):
    hdc_f1 = [hdc_report[c]["f1-score"] for c in CLASSES]
    xgb_f1 = [xgb_report[c]["f1-score"] for c in CLASSES]
    x = np.arange(len(CLASSES))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width / 2, hdc_f1, width, label="HDC")
    ax.bar(x + width / 2, xgb_f1, width, label="XGBoost")
    ax.set_xticks(x); ax.set_xticklabels(CLASSES)
    ax.set_ylabel("F1 Score")
    ax.set_ylim(0, 1.05)
    ax.set_title("Per-Variant F1 Score — HDC vs XGBoost")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "f1_comparison.png", dpi=150)
    plt.close(fig)


def plot_feature_importance(model):
    fig, ax = plt.subplots(figsize=(6, 4))
    importances = model.feature_importances_
    order = np.argsort(importances)
    ax.barh(np.array(SIGNAL_NAMES)[order], importances[order], color="#2b6cb0")
    ax.set_title("XGBoost Feature Importance (variant classifier)")
    ax.set_xlabel("Importance")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "xgb_feature_importance.png", dpi=150)
    plt.close(fig)


def report_to_dict(y_true, y_pred):
    d = classification_report(y_true, y_pred, target_names=CLASSES,
                               output_dict=True, zero_division=0)
    d["accuracy"] = accuracy_score(y_true, y_pred)
    return d


def main(sample_frac):
    t0 = time.time()

    print("=" * 70); print("  STEP 1: LOAD DATASET"); print("=" * 70)
    df = load_dataset(sample_frac)

    print("\n" + "=" * 70); print("  STEP 2: ENGINEER 6 SIGNALS"); print("=" * 70)
    df_features = engineer_features(df)
    X = df_features[SIGNAL_NAMES].values.astype(np.float32)
    y = df["variant_id"].map(CLASS_TO_IDX).values.astype(np.int32)

    print("\n" + "=" * 70); print("  STEP 3: TRAIN/VAL SPLIT (80/20, stratified)"); print("=" * 70)
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    print(f"  Train: {len(y_train):,}  Val: {len(y_val):,}")

    # ---------------- HDC ----------------
    print("\n" + "=" * 70); print("  STEP 4: TRAIN HDC (multiclass)"); print("=" * 70)
    encoder = HDCEncoder()
    hdc_clf = MulticlassHDCClassifier(dim=encoder.dim, num_classes=len(CLASSES))
    hdc_clf.train(X_train, y_train, encoder, epochs=HDC_RETRAIN_EPOCHS)

    X_val_enc = encoder.encode_batch(X_val)
    hdc_preds, _ = hdc_clf.predict(X_val_enc)
    hdc_report = report_to_dict(y_val, hdc_preds)
    print(f"  HDC val accuracy: {hdc_report['accuracy']:.4f}")

    # ---------------- XGBoost ----------------
    print("\n" + "=" * 70); print("  STEP 5: TRAIN XGBOOST (multiclass)"); print("=" * 70)
    xgb_model = xgb.XGBClassifier(
        objective="multi:softprob", num_class=len(CLASSES),
        n_estimators=300, max_depth=5, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9,
        eval_metric="mlogloss", random_state=RANDOM_STATE, n_jobs=-1,
    )
    xgb_model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    xgb_preds = xgb_model.predict(X_val)
    xgb_report = report_to_dict(y_val, xgb_preds)
    print(f"  XGBoost val accuracy: {xgb_report['accuracy']:.4f}")

    print("\n  HDC classification report:")
    print(classification_report(y_val, hdc_preds, target_names=CLASSES, zero_division=0))
    print("  XGBoost classification report:")
    print(classification_report(y_val, xgb_preds, target_names=CLASSES, zero_division=0))

    # ---------------- Graphs ----------------
    print("\n" + "=" * 70); print("  STEP 6: GRAPHS"); print("=" * 70)
    plot_confusion(confusion_matrix(y_val, hdc_preds), "HDC Confusion Matrix", OUT_DIR / "hdc_confusion.png")
    plot_confusion(confusion_matrix(y_val, xgb_preds), "XGBoost Confusion Matrix", OUT_DIR / "xgb_confusion.png")
    plot_f1_comparison(hdc_report, xgb_report)
    plot_feature_importance(xgb_model)
    print(f"  Saved graphs to {OUT_DIR}/")

    # ---------------- LLM summary ----------------
    print("\n" + "=" * 70); print("  STEP 7: LLM SUMMARY"); print("=" * 70)
    summary_text = summarize_llm(hdc_report, xgb_report)
    print(summary_text)

    # ---------------- Save ----------------
    results = {
        "n_rows": len(df),
        "n_train": len(y_train),
        "n_val": len(y_val),
        "hdc_accuracy": hdc_report["accuracy"],
        "xgb_accuracy": xgb_report["accuracy"],
        "hdc_report": hdc_report,
        "xgb_report": xgb_report,
        "llm_summary": summary_text,
        "elapsed_seconds": time.time() - t0,
    }
    with open(OUT_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    xgb_model.save_model(str(OUT_DIR / "xgb_variant_model.json"))

    print("\n" + "#" * 70)
    print("  FINAL COMPARISON")
    print("#" * 70)
    print(f"  {'Class':<10}{'HDC F1':>10}{'XGB F1':>10}")
    for c in CLASSES:
        print(f"  {c:<10}{hdc_report[c]['f1-score']:>10.3f}{xgb_report[c]['f1-score']:>10.3f}")
    print(f"  {'OVERALL':<10}{hdc_report['accuracy']:>10.3f}{xgb_report['accuracy']:>10.3f}")
    print(f"\n  Total time: {time.time()-t0:.1f}s")
    print(f"  Results saved to: {OUT_DIR}/")
    print("#" * 70)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=float, default=None)
    args = parser.parse_args()
    main(sample_frac=args.sample)
