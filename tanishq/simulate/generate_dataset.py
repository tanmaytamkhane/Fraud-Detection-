"""
simulate/generate_dataset.py — Main entry point
==================================================
Loads real data via the team's own pipeline.loader (for consistency with
Person 1 / Person 3's code), pulls the official ATO-001 contract from
identify.registry, generates all 5 variants, and packages ato_dataset.csv.

Run from the project root:
    python -m simulate.generate_dataset
    python -m simulate.generate_dataset --variant ATO-V4   # single variant
    python -m simulate.generate_dataset --sample-frac 0.1  # faster iteration
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

from identify.registry import AttackRegistry
from pipeline.loader import load_data
from simulate.ato_simulator import simulate_ato, generate_all_variants


def main():
    parser = argparse.ArgumentParser(description="Generate the AV-03 / ATO-001 synthetic dataset")
    parser.add_argument("--variant", default=None,
                         help="Generate a single variant (e.g. ATO-V4). Default: all 5.")
    parser.add_argument("--sample-frac", type=float, default=None,
                         help="Load a fraction of real data for faster iteration")
    parser.add_argument("--n-accounts", type=int, default=None,
                         help="Accounts per variant. Default: 15%% of established accounts.")
    parser.add_argument("--output-path", default="simulate/ato_dataset.csv")
    args = parser.parse_args()

    print("Loading official ATO-001 contract from identify/registry...")
    registry = AttackRegistry().load()
    validation = registry.validate()
    if not validation["is_valid"]:
        print(f"WARNING: registry validation found {validation['total_errors']} errors — proceeding anyway.")

    print("\nLoading real transaction data via pipeline.loader...")
    transaction_history = load_data(sample_frac=args.sample_frac)

    if args.variant:
        variant = registry.get_variant("ATO-001", args.variant)
        if variant is None:
            print(f"ERROR: variant {args.variant} not found in contract.")
            return
        synthetic_df = simulate_ato(
            transaction_history, variant.simulation_config, args.variant, n_accounts=args.n_accounts
        )
        print(f"\nGenerated {len(synthetic_df)} synthetic rows for {args.variant} ({variant.name})")
    else:
        synthetic_df = generate_all_variants(transaction_history, registry, n_accounts_per_variant=args.n_accounts)
        print(f"\nGenerated {len(synthetic_df)} synthetic rows across all 5 official variants")

    synthetic_df.to_csv(args.output_path, index=False)
    print(f"Saved: {args.output_path}")

    print("\n=== Summary by variant ===")
    print(synthetic_df.groupby("variant_id").agg(
        n_rows=("TransactionAmt", "count"),
        n_accounts=("card1", "nunique"),
        avg_amount=("TransactionAmt", "mean"),
    ))


if __name__ == "__main__":
    main()
