"""simulate/tb_generator.py — Synthetic Data Generator for TB-001 (Transaction Behaviour)"""
import numpy as np
import pandas as pd

def generate_tb_dataset(n_samples=24998, fraud_ratio=0.20, seed=42):
    rng = np.random.RandomState(seed)
    n_fraud = int(n_samples * fraud_ratio)
    n_legit = n_samples - n_fraud

    # 1. Legit Samples
    legit_vel = rng.beta(1.5, 6.0, size=n_legit)
    legit_micro = rng.beta(1.2, 7.0, size=n_legit)
    legit_subnet = rng.beta(1.5, 6.5, size=n_legit)
    legit_amt = rng.beta(1.8, 5.0, size=n_legit)
    legit_chan = rng.beta(1.5, 5.5, size=n_legit)
    legit_dev = rng.beta(1.5, 6.0, size=n_legit)

    # Legit shopping rush & micro charges (App Store in-app purchases)
    app_idx = rng.choice(n_legit, size=int(n_legit * 0.08), replace=False)
    legit_vel[app_idx] = rng.uniform(0.55, 0.80, size=len(app_idx))
    legit_micro[app_idx] = rng.uniform(0.50, 0.78, size=len(app_idx))

    df_legit = pd.DataFrame({
        "inter_arrival_velocity": np.clip(legit_vel, 0, 1),
        "micro_amount_clustering": np.clip(legit_micro, 0, 1),
        "bot_subnet_entropy": np.clip(legit_subnet, 0, 1),
        "amount_deviation": np.clip(legit_amt, 0, 1),
        "channel_risk": np.clip(legit_chan, 0, 1),
        "device_risk": np.clip(legit_dev, 0, 1),
        "is_fraud": 0,
        "variant_id": "LEGIT"
    })

    # 2. Fraud Variants
    v1_count = int(n_fraud * 0.60)
    v2_count = n_fraud - v1_count

    # TB-V1: High-Frequency Carding Botnet
    v1_vel = rng.beta(6.5, 2.0, size=v1_count)
    v1_micro = rng.beta(6.5, 2.0, size=v1_count)
    v1_subnet = rng.beta(6.0, 2.5, size=v1_count)
    v1_amt = rng.beta(2.0, 5.0, size=v1_count)
    v1_chan = rng.beta(6.5, 2.0, size=v1_count)
    v1_dev = rng.beta(6.0, 2.5, size=v1_count)
    
    # Stealth low-velocity carding (slow drip)
    stealth_idx = rng.choice(v1_count, size=int(v1_count * 0.10), replace=False)
    v1_vel[stealth_idx] = rng.uniform(0.35, 0.55, size=len(stealth_idx))

    # TB-V2: Coordinated Multi-Account Burst
    v2_vel = rng.beta(6.0, 2.5, size=v2_count)
    v2_micro = rng.beta(3.0, 4.0, size=v2_count)
    v2_subnet = rng.beta(6.5, 2.0, size=v2_count)
    v2_amt = rng.beta(6.0, 2.5, size=v2_count)
    v2_chan = rng.beta(5.8, 2.5, size=v2_count)
    v2_dev = rng.beta(6.0, 2.5, size=v2_count)

    df_v1 = pd.DataFrame({
        "inter_arrival_velocity": np.clip(v1_vel, 0, 1),
        "micro_amount_clustering": np.clip(v1_micro, 0, 1),
        "bot_subnet_entropy": np.clip(v1_subnet, 0, 1),
        "amount_deviation": np.clip(v1_amt, 0, 1),
        "channel_risk": np.clip(v1_chan, 0, 1),
        "device_risk": np.clip(v1_dev, 0, 1),
        "is_fraud": 1,
        "variant_id": "TB-V1"
    })

    df_v2 = pd.DataFrame({
        "inter_arrival_velocity": np.clip(v2_vel, 0, 1),
        "micro_amount_clustering": np.clip(v2_micro, 0, 1),
        "bot_subnet_entropy": np.clip(v2_subnet, 0, 1),
        "amount_deviation": np.clip(v2_amt, 0, 1),
        "channel_risk": np.clip(v2_chan, 0, 1),
        "device_risk": np.clip(v2_dev, 0, 1),
        "is_fraud": 1,
        "variant_id": "TB-V2"
    })

    df = pd.concat([df_legit, df_v1, df_v2], ignore_index=True)
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df

if __name__ == "__main__":
    df = generate_tb_dataset()
    df.to_csv("simulate/tb_dataset.csv", index=False)
    print(f"[OK] Generated Realistic TB dataset: {df.shape}")
