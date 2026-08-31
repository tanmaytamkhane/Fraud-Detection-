"""
simulate/validate.py — Validate synthetic samples against the official
signal catalog (identify/taxonomy.json: new_device, new_location,
new_beneficiary, amount_deviation, velocity_deviation, time_deviation)

Run from the project root:
    python -m simulate.validate
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd

from simulate.profile_builder import build_user_profile
from pipeline.loader import load_data

KNOWN_LIMITATION_NOTE = (
    "Normal-sample rows here are drawn from the SAME transactions used to "
    "build the account profiles (not held out). This means normal-sample "
    "deviation metrics are trivially near-zero by construction — that's "
    "expected, not a bug. A true held-out comparison happens in the Defend "
    "pillar's train/test split, not here. This validation step exists to "
    "confirm the synthetic generator is producing the INTENDED deviation "
    "direction and magnitude, not to simulate the classifier's real task."
)


def _rate(flags: list) -> float:
    return float(np.mean(flags)) if flags else float("nan")


def compute_signals(df: pd.DataFrame, profiles_by_card1: dict) -> dict:
    new_device, new_location, new_beneficiary = [], [], []
    amount_deviation, time_deviation = [], []

    for _, row in df.iterrows():
        profile = profiles_by_card1.get(row["card1"])
        if profile is None:
            continue

        # Device/location rates: only counted when the raw field is actually
        # present. ~69% of DeviceInfo and ~24% of addr1 are null (no matching
        # identity record / no address on file) — missing data is NOT
        # evidence of a "new" device or location, so it's excluded from the
        # denominator rather than silently counted as a positive.
        if pd.notna(row["DeviceInfo"]):
            new_device.append(row["DeviceInfo"] not in profile["known_devices"])
        if pd.notna(row["addr1"]):
            new_location.append(row["addr1"] not in profile["known_addr1"])

        # substitute signal — see ato_simulator.py docstring on beneficiary_change
        new_beneficiary.append(row["ProductCD"] not in profile["known_product_categories"])

        if profile["avg_amount"]:
            amount_deviation.append((row["TransactionAmt"] - profile["avg_amount"]) / profile["avg_amount"])

        if profile["usual_hours"]:
            txn_hour = (row["TransactionDT"] % 86400) // 3600
            dists = [min(abs(txn_hour - h), 24 - abs(txn_hour - h)) for h in profile["usual_hours"]]
            time_deviation.append(min(dists))

    return {
        "new_device_rate": _rate(new_device),
        "new_device_n_evaluated": len(new_device),
        "new_location_rate": _rate(new_location),
        "new_location_n_evaluated": len(new_location),
        "new_beneficiary_rate_SUBSTITUTE": _rate(new_beneficiary),
        "amount_deviation": pd.Series(amount_deviation).describe().to_dict() if amount_deviation else {},
        "time_deviation_hours": pd.Series(time_deviation).describe().to_dict() if time_deviation else {},
    }


def main():
    print("Loading real data and building profiles...")
    real_df = load_data()
    profiles_df = build_user_profile(real_df)
    profiles_by_card1 = profiles_df.set_index("card1").to_dict(orient="index")

    ato_df = pd.read_csv("simulate/ato_dataset.csv")

    legit = real_df[real_df.isFraud == 0]
    normal_sample = legit[legit.card1.isin(profiles_df.card1)].sample(
        n=min(2000, len(legit)), random_state=42
    )

    results = {"_note": KNOWN_LIMITATION_NOTE, "normal": compute_signals(normal_sample, profiles_by_card1)}

    for variant_id, group in ato_df.groupby("variant_id"):
        results[variant_id] = compute_signals(group, profiles_by_card1)

    print(json.dumps(results, indent=2, default=str))

    with open("simulate/validation_report.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("\nSaved: simulate/validation_report.json")


if __name__ == "__main__":
    main()
