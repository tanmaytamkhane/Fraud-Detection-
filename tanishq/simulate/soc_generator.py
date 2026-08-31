"""simulate/soc_generator.py — Synthetic Data Generator for SOC-001 (Social Engineering)"""
import numpy as np
import pandas as pd

def generate_soc_dataset(n_samples=24998, fraud_ratio=0.20, seed=42):
    rng = np.random.RandomState(seed)
    n_fraud = int(n_samples * fraud_ratio)
    n_legit = n_samples - n_fraud

    # 1. Legit Samples
    legit_urgency = rng.beta(1.8, 6.5, size=n_legit)
    legit_voice = rng.beta(1.5, 7.0, size=n_legit)
    legit_payee_mismatch = rng.beta(1.5, 6.0, size=n_legit)
    legit_amt_dev = rng.beta(1.8, 5.0, size=n_legit)
    legit_channel = rng.beta(1.5, 5.5, size=n_legit)
    legit_device = rng.beta(1.5, 6.0, size=n_legit)
    
    # Legit human edge cases (urgent vendor payments, phone channel noise, new procurement device)
    edge_idx = rng.choice(n_legit, size=int(n_legit * 0.08), replace=False)
    legit_urgency[edge_idx] = rng.uniform(0.60, 0.85, size=len(edge_idx))
    legit_channel[edge_idx] = rng.uniform(0.55, 0.80, size=len(edge_idx))
    
    noise_idx = rng.choice(n_legit, size=int(n_legit * 0.05), replace=False)
    legit_voice[noise_idx] = rng.uniform(0.50, 0.78, size=len(noise_idx)) # Bad phone mic jitter

    df_legit = pd.DataFrame({
        "social_urgency_score": np.clip(legit_urgency, 0, 1),
        "voice_jitter_anomaly": np.clip(legit_voice, 0, 1),
        "beneficiary_account_mismatch": np.clip(legit_payee_mismatch, 0, 1),
        "amount_deviation": np.clip(legit_amt_dev, 0, 1),
        "channel_risk": np.clip(legit_channel, 0, 1),
        "device_risk": np.clip(legit_device, 0, 1),
        "is_fraud": 0,
        "variant_id": "LEGIT"
    })

    # 2. Fraud Variants
    v1_count = int(n_fraud * 0.40)
    v2_count = int(n_fraud * 0.35)
    v3_count = n_fraud - v1_count - v2_count

    # SOC-V1: Invoice Phishing
    v1_urgency = rng.beta(6.0, 2.5, size=v1_count)
    v1_voice = rng.beta(2.0, 5.0, size=v1_count)
    v1_mismatch = rng.beta(6.5, 2.0, size=v1_count)
    v1_amt = rng.beta(5.0, 3.0, size=v1_count)
    v1_chan = rng.beta(5.5, 2.5, size=v1_count)
    v1_dev = rng.beta(4.5, 3.0, size=v1_count)
    
    # SOC-V2: Deepfake Voice Vishing
    v2_urgency = rng.beta(5.5, 2.8, size=v2_count)
    v2_voice = rng.beta(7.0, 2.0, size=v2_count)
    v2_mismatch = rng.beta(6.0, 2.5, size=v2_count)
    v2_amt = rng.beta(6.5, 2.5, size=v2_count)
    v2_chan = rng.beta(6.0, 2.5, size=v2_count)
    v2_dev = rng.beta(4.8, 3.0, size=v2_count)

    # SOC-V3: Smishing OTP Interception
    v3_urgency = rng.beta(6.0, 2.5, size=v3_count)
    v3_voice = rng.beta(1.8, 6.0, size=v3_count)
    v3_mismatch = rng.beta(4.5, 3.5, size=v3_count)
    v3_amt = rng.beta(4.5, 3.5, size=v3_count)
    v3_chan = rng.beta(6.5, 2.0, size=v3_count)
    v3_dev = rng.beta(6.5, 2.0, size=v3_count)

    # Stealth Evasion Injection (Fraudsters deliberately softening urgency words to bypass filters)
    stealth_idx = rng.choice(v1_count, size=int(v1_count * 0.10), replace=False)
    v1_urgency[stealth_idx] = rng.uniform(0.35, 0.55, size=len(stealth_idx))

    df_v1 = pd.DataFrame({
        "social_urgency_score": np.clip(v1_urgency, 0, 1),
        "voice_jitter_anomaly": np.clip(v1_voice, 0, 1),
        "beneficiary_account_mismatch": np.clip(v1_mismatch, 0, 1),
        "amount_deviation": np.clip(v1_amt, 0, 1),
        "channel_risk": np.clip(v1_chan, 0, 1),
        "device_risk": np.clip(v1_dev, 0, 1),
        "is_fraud": 1,
        "variant_id": "SOC-V1"
    })

    df_v2 = pd.DataFrame({
        "social_urgency_score": np.clip(v2_urgency, 0, 1),
        "voice_jitter_anomaly": np.clip(v2_voice, 0, 1),
        "beneficiary_account_mismatch": np.clip(v2_mismatch, 0, 1),
        "amount_deviation": np.clip(v2_amt, 0, 1),
        "channel_risk": np.clip(v2_chan, 0, 1),
        "device_risk": np.clip(v2_dev, 0, 1),
        "is_fraud": 1,
        "variant_id": "SOC-V2"
    })

    df_v3 = pd.DataFrame({
        "social_urgency_score": np.clip(v3_urgency, 0, 1),
        "voice_jitter_anomaly": np.clip(v3_voice, 0, 1),
        "beneficiary_account_mismatch": np.clip(v3_mismatch, 0, 1),
        "amount_deviation": np.clip(v3_amt, 0, 1),
        "channel_risk": np.clip(v3_chan, 0, 1),
        "device_risk": np.clip(v3_dev, 0, 1),
        "is_fraud": 1,
        "variant_id": "SOC-V3"
    })

    df = pd.concat([df_legit, df_v1, df_v2, df_v3], ignore_index=True)
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df

if __name__ == "__main__":
    df = generate_soc_dataset()
    df.to_csv("simulate/soc_dataset.csv", index=False)
    print(f"[OK] Generated Realistic SOC dataset: {df.shape}")
