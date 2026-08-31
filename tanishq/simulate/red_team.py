"""
red_team.py — Adversarial Red-Team Evasion Testing Campaign
===========================================================
Simulates adaptive attackers who tune attack parameters toward subtle /
legitimate-looking values to test evasion rates against the Defend + Response pipeline.
"""

import sys
import copy
import argparse
from pathlib import Path
from typing import Optional, List
import numpy as np
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from identify.registry import AttackRegistry
from pipeline.loader import load_data
from pipeline.feature_engineer import engineer_features
from simulate.ato_simulator import simulate_ato
from defend.scanner import UnifiedScanner
from response.engine import ResponseEngine


def nudge_simulation_config(base_config: dict, evasion_level: float, seed: int = 42) -> dict:
    """
    Nudges simulation parameters toward legitimate-looking values.

    Formula:
    - evasion_level in [0.0, 1.0]:
        0.0 = standard aggressive attack (unchanged)
        1.0 = maximally stealthy/evasive attack
    - Continuous knobs (amount_change, velocity_change):
        scaled down by (1.0 - 0.75 * evasion_level)
    - Boolean knobs (device_change, location_change, time_change, beneficiary_change):
        masked to False with probability min(0.8, evasion_level * 0.8)
    """
    rng = np.random.default_rng(seed)
    nudged = copy.deepcopy(base_config)
    evasion_level = float(np.clip(evasion_level, 0.0, 1.0))

    if evasion_level <= 0.0:
        return nudged

    # Nudge continuous knobs (reduce deviation magnitude)
    if "amount_change" in nudged:
        nudged["amount_change"] = float(nudged["amount_change"]) * max(0.0, 1.0 - 0.75 * evasion_level)

    if "velocity_change" in nudged:
        nudged["velocity_change"] = float(nudged["velocity_change"]) * max(0.0, 1.0 - 0.75 * evasion_level)

    # Nudge boolean knobs (attacker mimics known environment)
    prob_mask = min(0.8, evasion_level * 0.8)
    for b_knob in ["device_change", "location_change", "time_change", "beneficiary_change"]:
        if nudged.get(b_knob, False) and rng.random() < prob_mask:
            nudged[b_knob] = False

    return nudged


def run_red_team_campaign(
    registry: Optional[AttackRegistry] = None,
    transaction_history: Optional[pd.DataFrame] = None,
    scanner: Optional[UnifiedScanner] = None,
    response_engine: Optional[ResponseEngine] = None,
    variants: Optional[List[str]] = None,
    n_attempts_per_variant: int = 50,
    evasion_level: float = 0.5,
) -> pd.DataFrame:
    """
    Execute an adversarial evasion testing campaign across specified ATO variants.

    Args:
        registry: AttackRegistry instance.
        transaction_history: DataFrame of legitimate transactions for synthesis.
        scanner: UnifiedScanner instance from defend/.
        response_engine: ResponseEngine instance from response/.
        variants: List of variant IDs (e.g. ["ATO-V1", "ATO-V4"]). Default: all 5.
        n_attempts_per_variant: Number of attacks per variant.
        evasion_level: Float in [0.0, 1.0] indicating attack stealthiness.

    Returns:
        pd.DataFrame of all attack attempts and evasion outcomes.
    """
    if registry is None:
        registry = AttackRegistry().load()
    if transaction_history is None:
        transaction_history = load_data(sample_frac=0.1)
    if scanner is None:
        scanner = UnifiedScanner()
    if response_engine is None:
        response_engine = ResponseEngine()

    if variants is None:
        variant_objs = registry.list_variants("ATO-001")
        variants = [v["variant_id"] for v in variant_objs]

    print()
    print("=" * 75)
    print("  RED-TEAM ADVERSARIAL EVASION CAMPAIGN")
    print("=" * 75)
    print(f"  Target Variants : {', '.join(variants)}")
    print(f"  Attempts/Variant: {n_attempts_per_variant}")
    print(f"  Evasion Level   : {evasion_level:.2f} ({evasion_level*100:.0f}% stealth nudging)")
    print("=" * 75)

    records = []

    for v_idx, variant_id in enumerate(variants):
        variant_obj = registry.get_variant("ATO-001", variant_id)
        if not variant_obj:
            continue

        base_config = variant_obj.simulation_config
        nudged_config = nudge_simulation_config(
            base_config=base_config,
            evasion_level=evasion_level,
            seed=42 + v_idx,
        )

        # Generate evasive attack transactions
        synthetic_df = simulate_ato(
            transaction_history=transaction_history,
            variant_config=nudged_config,
            variant_id=variant_id,
            n_accounts=n_attempts_per_variant,
        )

        if len(synthetic_df) == 0:
            continue

        # Subsample or take exactly n_attempts_per_variant rows
        if len(synthetic_df) > n_attempts_per_variant:
            synthetic_df = synthetic_df.iloc[:n_attempts_per_variant].copy()

        # Engineer team features
        df_signals = engineer_features(synthetic_df)

        for i, (_, row) in enumerate(df_signals.iterrows()):
            txn_id = f"RED-{variant_id}-{i+1:04d}"
            sig_dict = {
                "device_risk": float(row.get("device_risk", 0.0)),
                "address_mismatch": float(row.get("address_mismatch", 0.0)),
                "amount_deviation": float(row.get("amount_deviation", 0.0)),
                "velocity": float(row.get("velocity", 0.0)),
                "time_anomaly": float(row.get("time_anomaly", 0.0)),
                "channel_risk": float(row.get("channel_risk", 0.0)),
            }

            # Scan via UnifiedScanner
            scan_res = scanner.scan_signals(sig_dict, transaction_id=txn_id)
            risk_score = scan_res["risk_score"]

            # Decide action via ResponseEngine
            decision = response_engine.execute_action(
                transaction_id=txn_id,
                risk_score=risk_score,
                variant_id=variant_id,
                silent=True,
                card1=row.get("card1"),
                addr1=row.get("addr1"),
            )

            action = decision["action"]
            # Attack is considered EVADED if bank decision is APPROVE or REVIEW (low-severity / missed block)
            evaded = bool(action in ["APPROVE", "REVIEW"])

            records.append({
                "transaction_id": txn_id,
                "variant_id": variant_id,
                "variant_name": variant_obj.name,
                "evasion_level": evasion_level,
                "risk_score": risk_score,
                "action": action,
                "evaded": evaded,
            })

    results_df = pd.DataFrame(records)

    # Print summary report
    print("\n" + "=" * 75)
    print("  🛡️  RED-TEAM EVASION RESULTS SUMMARY")
    print("=" * 75)

    summary_rows = []
    for vid in variants:
        v_df = results_df[results_df["variant_id"] == vid]
        total = len(v_df)
        if total == 0:
            continue
        evaded_cnt = int(v_df["evaded"].sum())
        evasion_rate = (evaded_cnt / total) * 100

        # Action tier distribution
        actions = v_df["action"].value_counts().to_dict()
        blocks = actions.get("BLOCK", 0)
        holds = actions.get("HOLD", 0)
        step_ups = actions.get("STEP_UP_AUTH", 0)
        reviews = actions.get("REVIEW", 0)
        approves = actions.get("APPROVE", 0)

        summary_rows.append({
            "Variant": vid,
            "Attempts": total,
            "Evaded (Approve/Review)": f"{evaded_cnt} ({evasion_rate:.1f}%)",
            "BLOCK": blocks,
            "HOLD": holds,
            "STEP_UP": step_ups,
            "REVIEW": reviews,
            "APPROVE": approves,
        })

    summary_table = pd.DataFrame(summary_rows)
    print(summary_table.to_string(index=False))

    total_attempts = len(results_df)
    total_evaded = int(results_df["evaded"].sum()) if total_attempts > 0 else 0
    overall_rate = (total_evaded / total_attempts) * 100 if total_attempts > 0 else 0.0

    print("-" * 75)
    print(f"  Overall Evasion Rate: {overall_rate:.2f}% ({total_evaded}/{total_attempts} evasions)")
    print("=" * 75 + "\n")

    return results_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Adversarial Red-Team Campaign")
    parser.add_argument("--variant", default=None, help="Target specific variant (e.g. ATO-V1). Default: all 5.")
    parser.add_argument("--attempts", type=int, default=20, help="Attempts per variant")
    parser.add_argument("--evasion", type=float, default=0.5, help="Evasion stealth level [0.0 to 1.0]")
    parser.add_argument("--sample-frac", type=float, default=0.05, help="Sample fraction of IEEE data")
    args = parser.parse_args()

    reg = AttackRegistry().load()
    hist = load_data(sample_frac=args.sample_frac)
    sc = UnifiedScanner()
    resp = ResponseEngine()

    target_variants = [args.variant] if args.variant else None
    run_red_team_campaign(
        registry=reg,
        transaction_history=hist,
        scanner=sc,
        response_engine=resp,
        variants=target_variants,
        n_attempts_per_variant=args.attempts,
        evasion_level=args.evasion,
    )
