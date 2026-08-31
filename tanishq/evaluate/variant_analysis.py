"""
variant_analysis.py — Per-Variant Detection Evaluation for HDC
================================================================

This module measures how effectively our HDC Fraud Detection Model catches
each specific post-compromise ATO variant (ATO-V1 to ATO-V5).

It proves/validates our Attack Intelligence hypothesis:
    ATO-V1 (Loud Takeover) -> Highest Detection Rate (Expected: Easy)
    ATO-V4 (The Ghost)     -> Lowest Detection Rate (Expected: Very Hard)
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline.variant_labeler import VARIANT_PROTOTYPES, VARIANT_NAMES

EXPECTED_DIFFICULTY = {
    "ATO-V1": "Easy (Expected high recall)",
    "ATO-V2": "Moderate",
    "ATO-V3": "Moderate",
    "ATO-V4": "Very Hard (The Ghost - subtle)",
    "ATO-V5": "Hard (Multi-Signal weak correlation)",
}


def evaluate_variants(y_true: np.ndarray, y_pred: np.ndarray, variant_labels: np.ndarray) -> pd.DataFrame:
    """
    Evaluates HDC detection performance broken down by each ATO variant.
    
    Args:
        y_true: True binary labels (1=Fraud, 0=Legit).
        y_pred: Predicted binary labels (1=Fraud, 0=Legit).
        variant_labels: Array of variant strings (ATO-V1 .. ATO-V5, LEGITIMATE).
        
    Returns:
        DataFrame with breakdown of detection rate per variant.
    """
    results = []
    
    for v_id in list(VARIANT_PROTOTYPES.keys()):
        # Select all samples belonging to this fraud variant
        mask = (variant_labels == v_id) & (y_true == 1)
        total_cases = int(np.sum(mask))
        
        if total_cases > 0:
            detected_cases = int(np.sum((y_pred == 1) & mask))
            missed_cases = total_cases - detected_cases
            recall = (detected_cases / total_cases) * 100
        else:
            detected_cases = 0
            missed_cases = 0
            recall = 0.0
            
        results.append({
            "Variant ID": v_id,
            "Variant Description": VARIANT_NAMES.get(v_id, ""),
            "Total Fraud Cases": total_cases,
            "Caught (TP)": detected_cases,
            "Missed (FN)": missed_cases,
            "Detection Rate": f"{recall:.1f}%",
            "Expected Difficulty": EXPECTED_DIFFICULTY.get(v_id, "")
        })
        
    return pd.DataFrame(results)


def print_variant_report(variant_df: pd.DataFrame):
    """
    Prints a formatted per-variant detection report.
    """
    print("\n" + "=" * 80)
    print("  🛡️  HDC PER-VARIANT FRAUD DETECTION BREAKDOWN")
    print("=" * 80)
    print(variant_df.to_string(index=False))
    print("=" * 80 + "\n")


if __name__ == '__main__':
    print("Testing variant analysis...")
    y_t = np.array([1, 1, 1, 1, 1, 0, 0])
    y_p = np.array([1, 1, 0, 0, 1, 0, 1])
    v_l = np.array(["ATO-V1", "ATO-V2", "ATO-V3", "ATO-V4", "ATO-V5", "LEGITIMATE", "LEGITIMATE"])
    
    res = evaluate_variants(y_t, y_p, v_l)
    print_variant_report(res)
