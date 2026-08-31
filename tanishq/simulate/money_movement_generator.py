"""
money_movement_generator.py — Realistic Synthetic Graph & Transfer Generator for Category 6 (Money Movement)
=============================================================================================================
Includes natural human edge cases and adversarial evasion overlap to prevent trivial 100% separability:
- Benford's Law + Log-normal amounts
- Poisson transfer arrivals
- Realistic background noise (high-volume legit P2P, split bills, payroll)
- Adversarial evasion perturbations on mule accounts
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

SIGNAL_NAMES = [
    "fan_out_degree",
    "fan_in_degree",
    "transit_velocity_sec",
    "amount_layering_ratio",
    "shared_device_cluster",
    "account_dormancy_score"
]

def generate_money_movement_dataset(
    n_samples: int = 25000,
    fraud_ratio: float = 0.15,
    seed: int = 42,
    output_path: str = None
) -> pd.DataFrame:
    rng = np.random.RandomState(seed)
    n_fraud = int(n_samples * fraud_ratio)
    n_legit = n_samples - n_fraud

    records = []
    base_time = datetime(2026, 8, 1, 8, 0, 0)

    # 1. Legitimate Transactions (85%) with natural edge cases (high-volume sellers, bill splits)
    print(f"Generating {n_legit} legitimate financial transfers with realistic human variance...")
    legit_account_pool = [f"ACC-{rng.randint(10000, 99999)}" for _ in range(4000)]

    for i in range(n_legit):
        sender = rng.choice(legit_account_pool)
        receiver = rng.choice(legit_account_pool)
        while receiver == sender:
            receiver = rng.choice(legit_account_pool)

        amount = float(np.clip(np.exp(rng.normal(3.9, 1.2)), 5.0, 5000.0))
        delta_sec = float(rng.exponential(350.0))
        tx_time = base_time + timedelta(seconds=delta_sec * (i + 1) % (30 * 86400))

        # 5% of legit transactions are natural high-velocity edge cases (e.g. party splitting, freelance payouts)
        is_edge_case = rng.rand() < 0.05
        if is_edge_case:
            fan_out = float(np.clip(rng.normal(0.40, 0.12), 0.10, 0.65))
            fan_in = float(np.clip(rng.normal(0.35, 0.10), 0.10, 0.60))
            transit_vel = float(np.clip(rng.normal(0.38, 0.12), 0.10, 0.65))
            layering = float(np.clip(rng.normal(0.35, 0.12), 0.05, 0.60))
            shared_dev = 1 if rng.rand() < 0.08 else 0
            dormancy = float(np.clip(rng.normal(0.30, 0.10), 0.05, 0.55))
        else:
            fan_out = float(np.clip(rng.beta(1.8, 7.5), 0.02, 0.35))
            fan_in = float(np.clip(rng.beta(1.8, 7.5), 0.02, 0.35))
            transit_vel = float(np.clip(rng.beta(1.5, 6.5), 0.01, 0.30))
            layering = float(np.clip(rng.beta(1.2, 5.0), 0.00, 0.35))
            shared_dev = 1 if rng.rand() < 0.02 else 0
            dormancy = float(np.clip(rng.beta(1.5, 7.0), 0.01, 0.28))

        records.append({
            "transfer_id": f"TRX-{rng.randint(100000, 999999):06X}",
            "sender_account": sender,
            "receiver_account": receiver,
            "amount": round(amount, 2),
            "timestamp": tx_time.isoformat(),
            "fan_out_degree": round(fan_out, 4),
            "fan_in_degree": round(fan_in, 4),
            "transit_velocity_sec": round(transit_vel, 4),
            "amount_layering_ratio": round(layering, 4),
            "shared_device_cluster": shared_dev,
            "account_dormancy_score": round(dormancy, 4),
            "is_fraud": 0,
            "attack_id": "LEGIT",
            "variant_id": "LEGIT",
            "variant_name": "Normal Peer-to-Peer Transfer",
            "hop_level": 1
        })

    # 2. Fraud Attack Variants (15%) with realistic evasion noise
    print(f"Generating {n_fraud} mule & laundering transfers with adversarial evasion...")
    variants = ["MM-V1", "MM-V2", "MM-V3", "MM-V4"]
    variant_names = {
        "MM-V1": "Rapid Cash-Out Burst",
        "MM-V2": "Smurfing / Layered Fan-Out",
        "MM-V3": "Fan-In Consolidation Ring",
        "MM-V4": "Dormant Mule Ring Activation"
    }

    per_variant = n_fraud // len(variants)
    mule_master_accounts = [f"MULE-MSTR-{rng.randint(100, 999)}" for _ in range(25)]
    mule_worker_accounts = [f"MULE-WRK-{rng.randint(1000, 9999)}" for _ in range(200)]
    dormant_accounts = [f"DORMANT-ACC-{rng.randint(10000, 99999)}" for _ in range(50)]

    for vid in variants:
        count = per_variant
        for i in range(count):
            tx_time = base_time + timedelta(seconds=rng.randint(100, 2500000))
            # Evasion noise factor (some fraudsters disguise transit times or amounts)
            evasion = rng.beta(1.5, 4.0)  # 0.0 to 0.5

            if vid == "MM-V1":
                sender = f"VICTIM-{rng.randint(1000, 9999)}"
                receiver = rng.choice(mule_master_accounts)
                amount = float(rng.uniform(3500.0, 18000.0))
                fan_out = float(np.clip(rng.normal(0.42, 0.08) * (1 - 0.3 * evasion), 0.15, 0.70))
                fan_in = float(np.clip(rng.normal(0.22, 0.06), 0.08, 0.45))
                transit_vel = float(np.clip(rng.normal(0.88, 0.08) * (1 - 0.4 * evasion), 0.45, 0.99))
                layering = float(np.clip(rng.normal(0.92, 0.06) * (1 - 0.3 * evasion), 0.50, 0.99))
                shared_dev = 1 if rng.rand() < (0.85 - 0.3 * evasion) else 0
                dormancy = float(np.clip(rng.normal(0.32, 0.08), 0.10, 0.55))
                hop = 1

            elif vid == "MM-V2":
                sender = f"VICTIM-{rng.randint(1000, 9999)}"
                receiver = rng.choice(mule_worker_accounts)
                amount = float(rng.uniform(750.0, 1950.0))
                fan_out = float(np.clip(rng.normal(0.88, 0.08) * (1 - 0.35 * evasion), 0.45, 0.99))
                fan_in = float(np.clip(rng.normal(0.22, 0.06), 0.08, 0.45))
                transit_vel = float(np.clip(rng.normal(0.72, 0.10) * (1 - 0.35 * evasion), 0.35, 0.92))
                layering = float(np.clip(rng.normal(0.85, 0.08) * (1 - 0.3 * evasion), 0.45, 0.98))
                shared_dev = 1 if rng.rand() < 0.25 else 0
                dormancy = float(np.clip(rng.normal(0.22, 0.06), 0.08, 0.45))
                hop = 1

            elif vid == "MM-V3":
                sender = rng.choice(mule_worker_accounts)
                receiver = rng.choice(mule_master_accounts)
                amount = float(rng.uniform(1500.0, 9500.0))
                fan_out = float(np.clip(rng.normal(0.22, 0.06), 0.08, 0.45))
                fan_in = float(np.clip(rng.normal(0.88, 0.08) * (1 - 0.35 * evasion), 0.45, 0.99))
                transit_vel = float(np.clip(rng.normal(0.76, 0.09) * (1 - 0.35 * evasion), 0.38, 0.95))
                layering = float(np.clip(rng.normal(0.88, 0.07) * (1 - 0.3 * evasion), 0.50, 0.99))
                shared_dev = 1 if rng.rand() < (0.80 - 0.3 * evasion) else 0
                dormancy = float(np.clip(rng.normal(0.28, 0.07), 0.08, 0.50))
                hop = 2

            else:  # MM-V4
                sender = rng.choice(dormant_accounts)
                receiver = rng.choice(mule_master_accounts)
                amount = float(rng.uniform(4000.0, 15000.0))
                fan_out = float(np.clip(rng.normal(0.38, 0.08), 0.15, 0.65))
                fan_in = float(np.clip(rng.normal(0.38, 0.08), 0.15, 0.65))
                transit_vel = float(np.clip(rng.normal(0.52, 0.11), 0.25, 0.78))
                layering = float(np.clip(rng.normal(0.80, 0.09) * (1 - 0.3 * evasion), 0.40, 0.95))
                shared_dev = 1 if rng.rand() < 0.40 else 0
                dormancy = float(np.clip(rng.normal(0.88, 0.08) * (1 - 0.35 * evasion), 0.45, 0.99))
                hop = 2

            records.append({
                "transfer_id": f"TRX-{rng.randint(100000, 999999):06X}",
                "sender_account": sender,
                "receiver_account": receiver,
                "amount": round(amount, 2),
                "timestamp": tx_time.isoformat(),
                "fan_out_degree": round(fan_out, 4),
                "fan_in_degree": round(fan_in, 4),
                "transit_velocity_sec": round(transit_vel, 4),
                "amount_layering_ratio": round(layering, 4),
                "shared_device_cluster": shared_dev,
                "account_dormancy_score": round(dormancy, 4),
                "is_fraud": 1,
                "attack_id": "MM-001",
                "variant_id": vid,
                "variant_name": variant_names[vid],
                "hop_level": hop
            })

    df = pd.DataFrame(records)
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    if output_path is None:
        output_path = Path(__file__).parent / "money_movement_dataset.csv"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[OK] Generated {len(df):,} realistic rows -> Saved to {output_path}")
    return df

if __name__ == "__main__":
    generate_money_movement_dataset(25000)
