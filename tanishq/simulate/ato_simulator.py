"""
simulate/ato_simulator.py — Official ATO-001 contract implementation
========================================================================
Implements the 6 simulation knobs and 5 variants defined in
identify/contract.json (owned by Person 1 — "do not invent attack
parameters independently," per PERSON_2_HANDOFF.md).

What's different from Person 1's reference apply_ato_variant() in the
handoff doc: every perturbed value here is resampled from the REAL
dataset's own distribution, or scaled from the account's OWN profile —
never a hardcoded sentinel (their reference uses addr1=999, dist1=1500,
DeviceType="mobile_unrecognized", which aren't grounded in real data).
This keeps the generator compliant with CLAUDE.md's fidelity requirement
while producing identical semantic behavior to the 6 knobs.

Open item requiring Person 1 sign-off: `beneficiary_change`. IEEE-CIS
has no beneficiary/payee field (it's card-transaction data, not P2P
transfer data) — neither this implementation nor Person 1's own
reference code has a real field to flip for this knob. Implemented here
as a documented SUBSTITUTE (ProductCD + P_emaildomain shift to
unseen-by-account values) — flagged loudly at runtime, not silently
assumed correct.
"""

import hashlib

import numpy as np
import pandas as pd

from simulate.profile_builder import build_user_profile

RANDOM_STATE = 42
rng = np.random.default_rng(RANDOM_STATE)

# Fraction of established accounts sampled per variant when n_accounts
# isn't explicitly given. [ASSUMPTION: illustrative starting value, not
# sourced — tune once the Defend pillar's classifier is running.]
DEFAULT_INJECTION_RATIO = 0.15

_BENEFICIARY_WARNING_SHOWN = False


def _fit_global_distributions(transaction_history: pd.DataFrame) -> dict:
    """Real legit-transaction distributions used for resampling."""
    legit = transaction_history[transaction_history.isFraud == 0]
    gaps = (
        legit.sort_values("TransactionDT")
        .groupby("card1")["TransactionDT"]
        .diff()
        .dropna()
    )
    return {
        "dist1_all": legit.dist1.dropna(),
        "device_info_pool": legit.DeviceInfo.dropna().unique(),
        "device_type_pool": legit.DeviceType.dropna().unique(),
        "addr1_pool": legit.addr1.dropna().unique(),
        "product_cd_pool": legit.ProductCD.dropna().unique(),
        "email_domain_pool": legit.P_emaildomain.dropna().unique(),
        "fast_gap_p05": gaps.quantile(0.05) if len(gaps) else 60.0,
    }


def _resample_excluding(pool: np.ndarray, exclude: set):
    """Pick a real value from `pool` that ISN'T in the account's own known set."""
    candidates = pool[~pd.Series(pool).isin(exclude)]
    if len(candidates) == 0:
        return rng.choice(pool) if len(pool) else None
    return rng.choice(candidates)


def apply_ato_variant(
    base_row: pd.Series, variant_config: dict, profile: pd.Series, global_dists: dict
) -> pd.Series:
    """
    Applies the 6-knob variant_config to one account's baseline transaction.
    Every non-boolean magnitude is grounded in real data or the account's
    own profile — see module docstring.
    """
    global _BENEFICIARY_WARNING_SHOWN
    row = base_row.copy()

    if variant_config.get("device_change"):
        row["DeviceInfo"] = _resample_excluding(
            global_dists["device_info_pool"], profile["known_devices"]
        )
        row["DeviceType"] = _resample_excluding(
            global_dists["device_type_pool"], profile["known_device_types"]
        )

    if variant_config.get("location_change"):
        # boolean knob -> fixed high-percentile band (90th-99th), fitted from real data
        d = global_dists["dist1_all"]
        band = d[(d >= d.quantile(0.90)) & (d <= d.quantile(0.99))]
        row["dist1"] = rng.choice(band) if len(band) else profile["typical_dist1"]
        row["addr1"] = _resample_excluding(global_dists["addr1_pool"], profile["known_addr1"])

    if variant_config.get("beneficiary_change"):
        if not _BENEFICIARY_WARNING_SHOWN:
            print(
                "[NOTE] beneficiary_change has no literal IEEE-CIS field. "
                "Substituting ProductCD + P_emaildomain shift. Flag for "
                "Person 1 sign-off — see ato_simulator.py docstring."
            )
            _BENEFICIARY_WARNING_SHOWN = True
        row["ProductCD"] = _resample_excluding(
            global_dists["product_cd_pool"], profile["known_product_categories"]
        )
        row["P_emaildomain"] = _resample_excluding(
            global_dists["email_domain_pool"], profile["known_email_domains"]
        )

    amount_change = variant_config.get("amount_change", 0.0)
    if amount_change > 0:
        # matches Person 1's documented formula (1.0 + amount_change * 5.0),
        # applied to the ACCOUNT'S OWN avg amount rather than a copied raw value
        multiplier = 1.0 + amount_change * 5.0
        row["TransactionAmt"] = profile["avg_amount"] * multiplier

    if variant_config.get("time_change"):
        # Matches Person 1's documented night window (2-4 AM) for
        # cross-team consistency, rather than a personalized "unusual hour"
        # definition that would compute differently in each of our scripts.
        target_hour = int(rng.integers(2, 4))
        day_start = (row["TransactionDT"] // 86400) * 86400
        row["TransactionDT"] = day_start + target_hour * 3600

    return row


def generate_velocity_burst(
    base_row: pd.Series, variant_config: dict, profile: pd.Series, global_dists: dict
) -> pd.DataFrame:
    """
    velocity_change > 0 produces MULTIPLE closely-spaced transactions, not
    a single row — a burst is inherently a multi-transaction pattern
    (this is the piece our earlier difficulty-tier generator was
    structurally missing entirely).

    n_transactions and gap scale with velocity_change; the gap is
    calibrated from the real dataset's own fast inter-transaction gap
    (5th percentile among established accounts), not an invented number.
    """
    velocity_change = variant_config.get("velocity_change", 0.0)
    if velocity_change <= 0:
        return pd.DataFrame([base_row])

    n_transactions = max(1, round(velocity_change * 10))
    # higher velocity_change -> gap approaches the real "fast" baseline;
    # lower velocity_change -> gap stretches out
    gap_seconds = global_dists["fast_gap_p05"] / max(velocity_change, 0.1)

    rows = []
    for i in range(n_transactions):
        r = base_row.copy()
        r["TransactionDT"] = base_row["TransactionDT"] + int(i * gap_seconds)
        rows.append(r)
    return pd.DataFrame(rows)


def simulate_ato(
    transaction_history: pd.DataFrame,
    variant_config: dict,
    variant_id: str,
    n_accounts: int = None,
) -> pd.DataFrame:
    """
    Generate synthetic ATO transactions for one variant (e.g. ATO-V1).

    variant_config: the simulation_config dict from identify/contract.json
    (get it via identify.registry.AttackRegistry, see generate_dataset.py)
    """
    profiles = build_user_profile(transaction_history)
    global_dists = _fit_global_distributions(transaction_history)

    last_txn_per_account = (
        transaction_history[transaction_history.isFraud == 0]
        .sort_values("TransactionDT")
        .groupby("card1")
        .tail(1)
        .set_index("card1")
    )

    if n_accounts is None:
        n_accounts = int(len(profiles) * DEFAULT_INJECTION_RATIO)
    # Derive a per-variant seed from RANDOM_STATE + variant_id so each of the
    # 5 official variants samples a DIFFERENT (but still reproducible) set of
    # accounts, instead of all variants hitting the identical account pool.
        # hashlib (not Python's built-in hash()) because str hash() is randomized
    # per-process by default in Python 3 — would silently break reproducibility
    # across separate runs of generate_dataset.py.
    variant_hash = int(hashlib.md5(variant_id.encode()).hexdigest(), 16)
    variant_seed = RANDOM_STATE + (variant_hash % 10_000)
    sampled_profiles = profiles.sample(n=min(n_accounts, len(profiles)), random_state=variant_seed)

    all_rows = []
    for _, profile in sampled_profiles.iterrows():
        card1 = profile["card1"]
        template = last_txn_per_account.loc[card1].copy()
        template["card1"] = card1  # restore - it's the groupby index above

        perturbed = apply_ato_variant(template, variant_config, profile, global_dists)
        burst_df = generate_velocity_burst(perturbed, variant_config, profile, global_dists)

        burst_df["isFraud"] = 1
        burst_df["is_synthetic"] = True
        burst_df["attack_id"] = "ATO-001"
        burst_df["variant_id"] = variant_id
        all_rows.append(burst_df)

    return pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()


def generate_all_variants(
    transaction_history: pd.DataFrame, registry, n_accounts_per_variant: int = None
) -> pd.DataFrame:
    """Generate synthetic transactions for all 5 official ATO-001 variants."""
    variant_summaries = registry.list_variants("ATO-001")
    parts = []
    for v in variant_summaries:
        variant = registry.get_variant("ATO-001", v["variant_id"])
        synthetic = simulate_ato(
            transaction_history,
            variant.simulation_config,
            v["variant_id"],
            n_accounts=n_accounts_per_variant,
        )
        parts.append(synthetic)
    return pd.concat(parts, ignore_index=True)
