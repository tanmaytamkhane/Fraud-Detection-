"""
variant_labeler.py — Categorizes Fraud Transactions into the 5 ATO Variants
=============================================================================

This module maps raw fraud transactions to the 5 post-compromise behavioral variants
established in Phase 1 (identify/attacks.json):

    ATO-V1: High-Value New Device Takeover (Loud / Multi-high anomalies)
    ATO-V2: Velocity Burst from Known Device (High speed / frequency)
    ATO-V3: Off-Hours Location Shift (Time anomaly + address mismatch)
    ATO-V4: Subtle Amount Deviation — The Ghost (Low intensity, sneaky)
    ATO-V5: Multi-Signal Low-Intensity — The Chameleon (Combined subtle deviations)
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import SIGNAL_NAMES

# 6-D Prototype Vectors for each ATO Variant:
# Order of signals: ['device_risk', 'address_mismatch', 'amount_deviation', 'velocity', 'time_anomaly', 'channel_risk']
VARIANT_PROTOTYPES = {
    "ATO-V1": np.array([0.85, 0.80, 0.90, 0.30, 0.20, 0.85], dtype=np.float32),
    "ATO-V2": np.array([0.20, 0.30, 0.40, 0.90, 0.20, 0.70], dtype=np.float32),
    "ATO-V3": np.array([0.20, 0.70, 0.10, 0.10, 0.85, 0.30], dtype=np.float32),
    "ATO-V4": np.array([0.20, 0.10, 0.30, 0.10, 0.10, 0.20], dtype=np.float32),
    "ATO-V5": np.array([0.35, 0.45, 0.25, 0.40, 0.60, 0.40], dtype=np.float32),
}

VARIANT_NAMES = {
    "ATO-V1": "High-Value New Device (Loud)",
    "ATO-V2": "Velocity Burst (Known Device)",
    "ATO-V3": "Off-Hours Location Shift",
    "ATO-V4": "Subtle Deviation (The Ghost)",
    "ATO-V5": "Multi-Signal (The Chameleon)",
}


def label_variants(signal_matrix: np.ndarray, labels: np.ndarray = None) -> np.ndarray:
    """
    Labels each fraud sample with the closest ATO variant ID (ATO-V1 to ATO-V5).
    Legitimate samples (label == 0) are labeled as 'LEGITIMATE'.
    
    Args:
        signal_matrix: np.ndarray of shape (N, 6) containing values in [0, 1].
        labels: Optional 1D array of shape (N,) with 1 for fraud and 0 for legit.
        
    Returns:
        np.ndarray of strings of length N with variant IDs or 'LEGITIMATE'.
    """
    n_samples = signal_matrix.shape[0]
    variant_labels = np.empty(n_samples, dtype=object)
    
    proto_keys = list(VARIANT_PROTOTYPES.keys())
    proto_matrix = np.array([VARIANT_PROTOTYPES[k] for k in proto_keys]) # Shape (5, 6)
    
    # Compute Euclidean distance from each sample to each of the 5 prototypes
    # (N, 1, 6) - (1, 5, 6) -> (N, 5, 6) -> sum over axis 2 -> (N, 5)
    diff = signal_matrix[:, np.newaxis, :] - proto_matrix[np.newaxis, :, :]
    distances = np.linalg.norm(diff, axis=2) # Shape (N, 5)
    
    closest_proto_idx = np.argmin(distances, axis=1) # Shape (N,)
    
    for i in range(n_samples):
        if labels is not None and labels[i] == 0:
            variant_labels[i] = "LEGITIMATE"
        else:
            variant_labels[i] = proto_keys[closest_proto_idx[i]]
            
    return variant_labels


def summarize_variants(variant_labels: np.ndarray) -> pd.DataFrame:
    """
    Returns a summary breakdown of assigned variants.
    """
    counts = pd.Series(variant_labels).value_counts()
    summary = []
    for k in list(VARIANT_PROTOTYPES.keys()) + ["LEGITIMATE"]:
        cnt = counts.get(k, 0)
        pct = (cnt / len(variant_labels)) * 100 if len(variant_labels) > 0 else 0
        summary.append({
            "Variant ID": k,
            "Variant Name": VARIANT_NAMES.get(k, "Normal Activity"),
            "Count": cnt,
            "Percentage": f"{pct:.2f}%"
        })
    return pd.DataFrame(summary)


if __name__ == '__main__':
    print("Testing variant labeler...")
    test_signals = np.array([
        [0.9, 0.8, 0.85, 0.3, 0.2, 0.9],   # V1
        [0.2, 0.2, 0.4, 0.95, 0.1, 0.7],   # V2
        [0.2, 0.75, 0.1, 0.1, 0.9, 0.3],   # V3
        [0.2, 0.1, 0.3, 0.1, 0.1, 0.2],    # V4 (Ghost)
        [0.35, 0.45, 0.25, 0.4, 0.6, 0.4], # V5 (Chameleon)
    ])
    test_labels = np.array([1, 1, 1, 1, 1])
    
    assigned = label_variants(test_signals, test_labels)
    print("Assigned Variants:", assigned)
    print("\nVariant Summary:")
    print(summarize_variants(assigned).to_string(index=False))
