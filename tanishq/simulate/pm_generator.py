"""simulate/pm_generator.py — Synthetic Data Generator for PM-001 (Payment Manipulation)"""
import numpy as np
import pandas as pd

def generate_pm_dataset(n_samples=24998, fraud_ratio=0.20, seed=42):
    rng = np.random.RandomState(seed)
    n_fraud = int(n_samples * fraud_ratio)
    n_legit = n_samples - n_fraud

    # 1. Legit Samples
    legit_qr = rng.beta(1.5, 6.5, size=n_legit)
    legit_payload = rng.beta(1.2, 7.0, size=n_legit)
    legit_geo = rng.beta(1.8, 5.5, size=n_legit)
    legit_amt = rng.beta(1.8, 5.0, size=n_legit)
    legit_chan = rng.beta(1.5, 5.5, size=n_legit)
    legit_dev = rng.beta(1.5, 6.0, size=n_legit)

    # Legit travel & VPN edge cases
    vpn_idx = rng.choice(n_legit, size=int(n_legit * 0.08), replace=False)
    legit_geo[vpn_idx] = rng.uniform(0.65, 0.88, size=len(vpn_idx))

    df_legit = pd.DataFrame({
        "qr_signature_mismatch": np.clip(legit_qr, 0, 1),
        "payload_tampering_score": np.clip(legit_payload, 0, 1),
        "merchant_geo_mismatch": np.clip(legit_geo, 0, 1),
        "amount_deviation": np.clip(legit_amt, 0, 1),
        "channel_risk": np.clip(legit_chan, 0, 1),
        "device_risk": np.clip(legit_dev, 0, 1),
        "is_fraud": 0,
        "variant_id": "LEGIT"
    })

    # 2. Fraud Variants
    v1_count = int(n_fraud * 0.55)
    v2_count = n_fraud - v1_count

    # PM-V1: QR Redirection
    v1_qr = rng.beta(6.5, 2.0, size=v1_count)
    v1_payload = rng.beta(5.0, 3.0, size=v1_count)
    v1_geo = rng.beta(6.0, 2.5, size=v1_count)
    v1_amt = rng.beta(3.5, 3.5, size=v1_count)
    v1_chan = rng.beta(6.5, 2.2, size=v1_count)
    v1_dev = rng.beta(3.5, 3.5, size=v1_count)
    
    # Stealth QR evasion
    stealth_idx = rng.choice(v1_count, size=int(v1_count * 0.10), replace=False)
    v1_qr[stealth_idx] = rng.uniform(0.40, 0.60, size=len(stealth_idx))

    # PM-V2: API Amount Tampering
    v2_qr = rng.beta(1.8, 6.0, size=v2_count)
    v2_payload = rng.beta(7.0, 2.0, size=v2_count)
    v2_geo = rng.beta(3.5, 3.5, size=v2_count)
    v2_amt = rng.beta(6.5, 2.0, size=v2_count)
    v2_chan = rng.beta(6.0, 2.5, size=v2_count)
    v2_dev = rng.beta(5.0, 3.0, size=v2_count)

    df_v1 = pd.DataFrame({
        "qr_signature_mismatch": np.clip(v1_qr, 0, 1),
        "payload_tampering_score": np.clip(v1_payload, 0, 1),
        "merchant_geo_mismatch": np.clip(v1_geo, 0, 1),
        "amount_deviation": np.clip(v1_amt, 0, 1),
        "channel_risk": np.clip(v1_chan, 0, 1),
        "device_risk": np.clip(v1_dev, 0, 1),
        "is_fraud": 1,
        "variant_id": "PM-V1"
    })

    df_v2 = pd.DataFrame({
        "qr_signature_mismatch": np.clip(v2_qr, 0, 1),
        "payload_tampering_score": np.clip(v2_payload, 0, 1),
        "merchant_geo_mismatch": np.clip(v2_geo, 0, 1),
        "amount_deviation": np.clip(v2_amt, 0, 1),
        "channel_risk": np.clip(v2_chan, 0, 1),
        "device_risk": np.clip(v2_dev, 0, 1),
        "is_fraud": 1,
        "variant_id": "PM-V2"
    })

    df = pd.concat([df_legit, df_v1, df_v2], ignore_index=True)
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df

if __name__ == "__main__":
    df = generate_pm_dataset()
    df.to_csv("simulate/pm_dataset.csv", index=False)
    print(f"[OK] Generated Realistic PM dataset: {df.shape}")
