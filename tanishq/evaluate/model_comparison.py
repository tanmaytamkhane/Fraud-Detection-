"""
model_comparison.py - HDC vs XGBoost Side-by-Side Comparison
=============================================================

Compares predictions from the HDC classifier and XGBoost baseline
on the same validation set, and produces a combined ensemble prediction.
"""

import numpy as np
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluate.metrics import accuracy, precision, recall, f1_score, auc_roc


def compare_models(y_true, hdc_predictions, hdc_scores,
                   xgb_predictions, xgb_probabilities):
    """
    Build a per-row comparison DataFrame for HDC and XGBoost predictions.

    All five inputs must be aligned by row (same validation set, same order).

    Args:
        y_true: Ground truth labels (1=fraud, 0=legit).
        hdc_predictions: HDC binary predictions.
        hdc_scores: HDC continuous fraud scores (0-1).
        xgb_predictions: XGBoost binary predictions.
        xgb_probabilities: XGBoost fraud probabilities (0-1).

    Returns:
        pd.DataFrame with per-row comparison columns.
    """
    y_true = np.asarray(y_true)
    hdc_predictions = np.asarray(hdc_predictions)
    hdc_scores = np.asarray(hdc_scores)
    xgb_predictions = np.asarray(xgb_predictions)
    xgb_probabilities = np.asarray(xgb_probabilities)

    final_score = (hdc_scores + xgb_probabilities) / 2.0
    final_prediction = (final_score >= 0.5).astype(int)

    return pd.DataFrame({
        "y_true": y_true,
        "hdc_prediction": hdc_predictions,
        "hdc_score": hdc_scores,
        "xgb_prediction": xgb_predictions,
        "xgb_probability": xgb_probabilities,
        "agree": hdc_predictions == xgb_predictions,
        "final_score": final_score,
        "final_prediction": final_prediction,
    })


def summarize_comparison(comparison_df, y_true):
    """
    Print and return summary metrics comparing HDC, XGBoost, and the ensemble.

    Args:
        comparison_df: DataFrame from compare_models().
        y_true: Ground truth labels.

    Returns:
        dict with agreement_rate and per-model metrics dicts.
    """
    y_true = np.asarray(y_true)

    agreement_rate = comparison_df["agree"].mean()

    def _metrics(y_pred, scores=None):
        y_pred = np.asarray(y_pred)
        m = {
            "accuracy": accuracy(y_true, y_pred),
            "precision": precision(y_true, y_pred),
            "recall": recall(y_true, y_pred),
            "f1_score": f1_score(y_true, y_pred),
        }
        if scores is not None:
            m["auc_roc"] = auc_roc(y_true, np.asarray(scores))
        return m

    hdc_metrics = _metrics(comparison_df["hdc_prediction"], comparison_df["hdc_score"])
    xgb_metrics = _metrics(comparison_df["xgb_prediction"], comparison_df["xgb_probability"])
    ensemble_metrics = _metrics(comparison_df["final_prediction"], comparison_df["final_score"])

    # Print report
    print()
    print("=" * 70)
    print("  HDC vs XGBoost - MODEL COMPARISON REPORT")
    print("=" * 70)
    print(f"  Agreement Rate: {agreement_rate:.2%}")
    print(f"  (Both models predicted the same class on {agreement_rate:.2%} of rows)")
    print()

    header_parts = ["  ", "Metric".ljust(14), " | ", "HDC".rjust(10), " | ",
                     "XGBoost".rjust(10), " | ", "Ensemble".rjust(10)]
    header = "".join(header_parts)
    print(header)
    print("  " + "-" * (len(header) - 2))

    for metric_name in ["accuracy", "precision", "recall", "f1_score", "auc_roc"]:
        h = hdc_metrics.get(metric_name, float("nan"))
        x = xgb_metrics.get(metric_name, float("nan"))
        e = ensemble_metrics.get(metric_name, float("nan"))
        label = metric_name.replace("_", " ").title()
        if metric_name == "auc_roc":
            label = "AUC-ROC"
        row = "  " + label.ljust(14) + " | " + f"{h:10.4f}" + " | " + f"{x:10.4f}" + " | " + f"{e:10.4f}"
        print(row)

    # Determine winner
    candidates = [
        ("HDC", hdc_metrics["f1_score"]),
        ("XGBoost", xgb_metrics["f1_score"]),
        ("Ensemble", ensemble_metrics["f1_score"]),
    ]
    best_f1 = max(candidates, key=lambda t: t[1])
    print(f"  Best F1 Score: {best_f1[0]} ({best_f1[1]:.4f})")
    print("=" * 70)
    print()

    return {
        "agreement_rate": agreement_rate,
        "hdc": hdc_metrics,
        "xgb": xgb_metrics,
        "ensemble": ensemble_metrics,
    }
