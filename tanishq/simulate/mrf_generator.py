"""simulate/mrf_generator.py — Synthetic Data Generator for MRF-001 (Merchant & Refund Fraud)"""
import numpy as np
import pandas as pd

def generate_mrf_dataset(n_samples=24998, fraud_ratio=0.20, seed=42):
    rng = np.random.RandomState(seed)
    n_fraud = int(n_samples * fraud_ratio)
    n_legit = n_samples - n_fraud

    # 1. Legit Samples
    legit_prompt = rng.beta(1.2, 7.0, size=n_legit)
    legit_refund = rng.beta(1.5, 6.5, size=n_legit)
    legit_dispute = rng.beta(1.5, 6.0, size=n_legit)
    legit_amt = rng.beta(1.8, 5.0, size=n_legit)
    legit_chan = rng.beta(1.5, 5.5, size=n_legit)
    legit_dev = rng.beta(1.5, 6.0, size=n_legit)

    # Legit customer support disputes (legitimate returns on broken products)
    dispute_idx = rng.choice(n_legit, size=int(n_legit * 0.08), replace=False)
    legit_refund[dispute_idx] = rng.uniform(0.55, 0.80, size=len(dispute_idx))
    legit_dispute[dispute_idx] = rng.uniform(0.50, 0.75, size=len(dispute_idx))

    df_legit = pd.DataFrame({
        "prompt_injection_score": np.clip(legit_prompt, 0, 1),
        "unverified_refund_ratio": np.clip(legit_refund, 0, 1),
        "merchant_dispute_anomaly": np.clip(legit_dispute, 0, 1),
        "amount_deviation": np.clip(legit_amt, 0, 1),
        "channel_risk": np.clip(legit_chan, 0, 1),
        "device_risk": np.clip(legit_dev, 0, 1),
        "is_fraud": 0,
        "variant_id": "LEGIT"
    })

    # 2. Fraud Variants
    v1_count = int(n_fraud * 0.50)
    v2_count = n_fraud - v1_count

    # MRF-V1: Chatbot Refund Jailbreak
    v1_prompt = rng.beta(6.5, 2.0, size=v1_count)
    v1_refund = rng.beta(6.5, 2.0, size=v1_count)
    v1_dispute = rng.beta(4.5, 3.5, size=v1_count)
    v1_amt = rng.beta(5.0, 3.0, size=v1_count)
    v1_chan = rng.beta(6.0, 2.5, size=v1_count)
    v1_dev = rng.beta(5.5, 2.5, size=v1_count)
    
    # Subtle jailbreak phrasing evasion
    stealth_idx = rng.choice(v1_count, size=int(v1_count * 0.10), replace=False)
    v1_prompt[stealth_idx] = rng.uniform(0.35, 0.55, size=len(stealth_idx))

    # MRF-V2: Ghost Merchant Laundering
    v2_prompt = rng.beta(1.8, 5.5, size=v2_count)
    v2_refund = rng.beta(3.5, 3.5, size=v2_count)
    v2_dispute = rng.beta(6.8, 2.0, size=v2_count)
    v2_amt = rng.beta(6.2, 2.5, size=v2_count)
    v2_chan = rng.beta(5.8, 2.5, size=v2_count)
    v2_dev = rng.beta(5.5, 2.5, size=v2_count)

    df_v1 = pd.DataFrame({
        "prompt_injection_score": np.clip(v1_prompt, 0, 1),
        "unverified_refund_ratio": np.clip(v1_refund, 0, 1),
        "merchant_dispute_anomaly": np.clip(v1_dispute, 0, 1),
        "amount_deviation": np.clip(v1_amt, 0, 1),
        "channel_risk": np.clip(v1_chan, 0, 1),
        "device_risk": np.clip(v1_dev, 0, 1),
        "is_fraud": 1,
        "variant_id": "MRF-V1"
    })

    df_v2 = pd.DataFrame({
        "prompt_injection_score": np.clip(v2_prompt, 0, 1),
        "unverified_refund_ratio": np.clip(v2_refund, 0, 1),
        "merchant_dispute_anomaly": np.clip(v2_dispute, 0, 1),
        "amount_deviation": np.clip(v2_amt, 0, 1),
        "channel_risk": np.clip(v2_chan, 0, 1),
        "device_risk": np.clip(v2_dev, 0, 1),
        "is_fraud": 1,
        "variant_id": "MRF-V2"
    })

    df = pd.concat([df_legit, df_v1, df_v2], ignore_index=True)
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df

if __name__ == "__main__":
    df = generate_mrf_dataset()
    df.to_csv("simulate/mrf_dataset.csv", index=False)
    print(f"[OK] Generated Realistic MRF dataset: {df.shape}")
