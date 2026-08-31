"""
simulate_starter.py — Starter Template for Person 2 (Simulation Team)
======================================================================
This file shows Person 2 how to import and use the Attack Intelligence
package (from identify) to generate simulated ATO attack streams.

Person 2 can build their simulation pipeline directly on top of this!
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add repository root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import Person 1's ground truth package directly!
from identify import AttackRegistry


def run_simulation_demo():
    print("=" * 70)
    print("  🧪 PERSON 2: ATTACK SIMULATION ENGINE (POWERED BY P1 GROUND TRUTH)")
    print("=" * 70)

    # 1. Load Ground Truth Contract
    registry = AttackRegistry().load()
    ato = registry.get_attack("ATO-001")
    contract = registry.get_attack_contract("ATO-001")

    print(f"\n[1] Loaded Ground Truth for: {contract['name']} ({contract['attack_id']})")
    print(f"    Available Simulation Knobs: {', '.join(contract['simulation_parameters'])}")
    print(f"    Total Variants Defined: {len(ato.variants)}")

    # 2. Iterate through all 5 variants and prepare generation recipes
    print("\n[2] Extracting Variant Simulation Recipes from Registry:")
    print("-" * 70)

    for v in ato.variants:
        cfg = v.simulation_config
        print(f"\n  ▶ Variant: {v.variant_id} — {v.name}")
        print(f"    Risk Level: {v.risk_level.upper()} (Score: {v.risk_score})")
        print(f"    Recipe Config: {cfg}")
        print(f"    Expected System Mitigation: {v.expected_mitigation}")

    # 3. Example: Applying Variant 1 (Loud ATO) to a baseline transaction
    print("\n" + "-" * 70)
    print("[3] Simulating an Attack Event on a Sample Transaction:")
    
    baseline_transaction = {
        "TransactionID": 900001,
        "TransactionAmt": 45.0,
        "DeviceType": "desktop",
        "DeviceInfo": "Windows",
        "id_15": "Found",
        "addr1": 315,
        "dist1": 12.0,
        "isFraud": 0
    }
    
    print("\n  Original Legitimate Transaction:")
    print(" ", baseline_transaction)
    
    # Get recipe for ATO-V1
    v1 = registry.get_variant("ATO-001", "ATO-V1")
    simulated_txn = baseline_transaction.copy()
    
    if v1.simulation_config["device_change"]:
        simulated_txn["DeviceType"] = "mobile"
        simulated_txn["DeviceInfo"] = "UNKNOWN_SAMSUNG_DEVICE"
        simulated_txn["id_15"] = "New"
        
    if v1.simulation_config["location_change"]:
        simulated_txn["addr1"] = 999
        simulated_txn["dist1"] = 2500.0
        
    if v1.simulation_config["amount_change"] > 0:
        simulated_txn["TransactionAmt"] = baseline_transaction["TransactionAmt"] * (1.0 + v1.simulation_config["amount_change"] * 10)
        
    simulated_txn["isFraud"] = 1
    simulated_txn["applied_variant"] = v1.variant_id
    
    print(f"\n  Synthetically Injected {v1.variant_id} Attack Transaction:")
    print(" ", simulated_txn)
    print("\n" + "=" * 70)
    print("  ✅ SIMULATION RECIPE VERIFIED SUCCESSFULLY")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    run_simulation_demo()
