"""
simulate/profile_builder.py — Behavioral baselines per account (card1 proxy)
================================================================================
Built for the official ATO-001 contract (identify/contract.json). Every
synthetic perturbation in ato_simulator.py deviates from a SPECIFIC
account's own real history here — never a global constant or invented
value, per CLAUDE.md's fidelity requirement.

Columns used come from config.TRANSACTION_COLUMNS / IDENTITY_COLUMNS —
this module assumes data was loaded via pipeline.loader.load_data(), so
it stays consistent with the rest of the team's pipeline.
"""

import pandas as pd

MIN_TRANSACTIONS_FOR_PROFILE = 2  # need a real baseline to deviate from


def _hour_of_day(transaction_dt: pd.Series) -> pd.Series:
    """TransactionDT is a seconds-based timedelta from an unspecified reference
    (documented Kaggle behavior). Modulo 86400 still recovers a consistent
    diurnal (hour-of-day) cycle even without a real wall-clock anchor."""
    return (transaction_dt % 86400) // 3600


def build_user_profile(transaction_history: pd.DataFrame) -> pd.DataFrame:
    """
    Returns one row per established account (card1, >=2 real transactions)
    with: avg/median amount, known devices, known addresses, known product
    categories, known email domains, typical dist1, usual hours, and the
    account's real inter-transaction gap (for velocity-burst calibration).
    """
    df = transaction_history.copy()
    df = df[df.isFraud == 0]
    df["hour_of_day"] = _hour_of_day(df["TransactionDT"])

    counts = df.groupby("card1").size()
    established = counts[counts >= MIN_TRANSACTIONS_FOR_PROFILE].index
    df = df[df.card1.isin(established)]

    profiles = []
    for card1, group in df.groupby("card1"):
        group = group.sort_values("TransactionDT")
        gaps = group["TransactionDT"].diff().dropna()

        profiles.append({
            "card1": card1,
            "n_transactions": len(group),
            "avg_amount": group.TransactionAmt.mean(),
            "median_amount": group.TransactionAmt.median(),
            "known_devices": set(group.DeviceInfo.dropna().unique()),
            "known_device_types": set(group.DeviceType.dropna().unique()),
            "known_addr1": set(group.addr1.dropna().unique()),
            "known_product_categories": set(group.ProductCD.dropna().unique()),
            "known_email_domains": set(group.P_emaildomain.dropna().unique()),
            "typical_dist1": group.dist1.median(),
            "usual_hours": set(group.hour_of_day.dropna().unique()),
            "median_gap_seconds": gaps.median() if len(gaps) else None,
            "last_transaction_dt": group.TransactionDT.max(),
        })

    return pd.DataFrame(profiles)
