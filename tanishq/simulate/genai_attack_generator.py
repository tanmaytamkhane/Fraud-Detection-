"""
genai_attack_generator.py — Realistic Synthetic Multi-Modal Generator for Category 7 (GenAI-Native)
====================================================================================================
Generates multi-modal AI biometric signals with natural acoustic jitter variance and adversarial evasion.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

SIGNAL_NAMES = [
    "llm_semantic_intent_score",
    "voice_biometric_jitter",
    "synthetic_face_embedding_dist",
    "adversarial_perturbation_index",
    "device_risk",
    "amount_deviation"
]

def generate_genai_dataset(
    n_samples: int = 25000,
    fraud_ratio: float = 0.15,
    seed: int = 42,
    output_path: str = None
) -> pd.DataFrame:
    rng = np.random.RandomState(seed)
    n_fraud = int(n_samples * fraud_ratio)
    n_legit = n_samples - n_fraud

    records = []
    base_time = datetime(2026, 8, 1, 9, 0, 0)

    print(f"Generating {n_legit} legitimate transactions with natural microphone & sensor noise...")
    for i in range(n_legit):
        tx_time = base_time + timedelta(seconds=rng.randint(100, 2500000))
        # 6% of legit users have poor microphones, heavy accents, or VPNs
        is_noisy = rng.rand() < 0.06
        if is_noisy:
            llm_intent = float(np.clip(rng.normal(0.35, 0.10), 0.10, 0.60))
            voice_jitter = float(np.clip(rng.normal(0.40, 0.12), 0.10, 0.65))
            face_dist = float(np.clip(rng.normal(0.38, 0.10), 0.10, 0.60))
            adv_index = float(np.clip(rng.normal(0.30, 0.10), 0.05, 0.55))
            dev_risk = float(np.clip(rng.normal(0.45, 0.12), 0.15, 0.70))
            amt_dev = float(np.clip(rng.normal(0.35, 0.12), 0.05, 0.60))
        else:
            llm_intent = float(np.clip(rng.beta(1.5, 7.5), 0.01, 0.28))
            voice_jitter = float(np.clip(rng.beta(1.5, 7.5), 0.01, 0.28))
            face_dist = float(np.clip(rng.beta(1.5, 7.5), 0.01, 0.28))
            adv_index = float(np.clip(rng.beta(1.2, 7.0), 0.01, 0.25))
            dev_risk = float(np.clip(rng.beta(1.8, 6.5), 0.02, 0.35))
            amt_dev = float(np.clip(rng.beta(1.5, 6.5), 0.01, 0.35))

        amount = float(np.clip(np.exp(rng.normal(4.0, 1.1)), 10.0, 4000.0))

        records.append({
            "interaction_id": f"GENAI-{rng.randint(100000, 999999):06X}",
            "user_id": f"USR-{rng.randint(1000, 9999)}",
            "amount": round(amount, 2),
            "timestamp": tx_time.isoformat(),
            "llm_semantic_intent_score": round(llm_intent, 4),
            "voice_biometric_jitter": round(voice_jitter, 4),
            "synthetic_face_embedding_dist": round(face_dist, 4),
            "adversarial_perturbation_index": round(adv_index, 4),
            "device_risk": round(dev_risk, 4),
            "amount_deviation": round(amt_dev, 4),
            "is_fraud": 0,
            "attack_id": "LEGIT",
            "variant_id": "LEGIT",
            "variant_name": "Normal Verified Interaction"
        })

    print(f"Generating {n_fraud} GenAI-Native attacks with evasion noise...")
    variants = ["GENAI-V1", "GENAI-V2", "GENAI-V3", "GENAI-V4"]
    variant_names = {
        "GENAI-V1": "Conversational Autonomous Fraud Agent",
        "GENAI-V2": "Deepfake Video & Voice Authorization Bypass",
        "GENAI-V3": "Generative AI Synthetic Identity (KYC Diffusion Bypass)",
        "GENAI-V4": "Adaptive Adversarial Feature Evasion"
    }

    per_variant = n_fraud // len(variants)
    for vid in variants:
        count = per_variant
        for i in range(count):
            tx_time = base_time + timedelta(seconds=rng.randint(100, 2500000))
            evasion = rng.beta(1.5, 4.0)

            if vid == "GENAI-V1":
                amount = float(rng.uniform(2500.0, 12000.0))
                llm_intent = float(np.clip(rng.normal(0.88, 0.08) * (1 - 0.35 * evasion), 0.45, 0.99))
                voice_jitter = float(np.clip(rng.normal(0.25, 0.08), 0.08, 0.50))
                face_dist = float(np.clip(rng.normal(0.20, 0.06), 0.05, 0.40))
                adv_index = float(np.clip(rng.normal(0.60, 0.10) * (1 - 0.3 * evasion), 0.25, 0.85))
                dev_risk = float(np.clip(rng.normal(0.82, 0.08) * (1 - 0.3 * evasion), 0.40, 0.98))
                amt_dev = float(np.clip(rng.normal(0.70, 0.10), 0.35, 0.95))

            elif vid == "GENAI-V2":
                amount = float(rng.uniform(15000.0, 85000.0))
                llm_intent = float(np.clip(rng.normal(0.75, 0.10) * (1 - 0.3 * evasion), 0.40, 0.95))
                voice_jitter = float(np.clip(rng.normal(0.92, 0.06) * (1 - 0.35 * evasion), 0.50, 0.99))
                face_dist = float(np.clip(rng.normal(0.35, 0.08), 0.10, 0.60))
                adv_index = float(np.clip(rng.normal(0.45, 0.10), 0.15, 0.75))
                dev_risk = float(np.clip(rng.normal(0.88, 0.07) * (1 - 0.3 * evasion), 0.45, 0.99))
                amt_dev = float(np.clip(rng.normal(0.92, 0.06), 0.55, 0.99))

            elif vid == "GENAI-V3":
                amount = float(rng.uniform(8000.0, 35000.0))
                llm_intent = float(np.clip(rng.normal(0.25, 0.08), 0.08, 0.50))
                voice_jitter = float(np.clip(rng.normal(0.18, 0.06), 0.05, 0.40))
                face_dist = float(np.clip(rng.normal(0.90, 0.07) * (1 - 0.35 * evasion), 0.48, 0.99))
                adv_index = float(np.clip(rng.normal(0.55, 0.10), 0.20, 0.80))
                dev_risk = float(np.clip(rng.normal(0.75, 0.09) * (1 - 0.3 * evasion), 0.38, 0.95))
                amt_dev = float(np.clip(rng.normal(0.80, 0.09), 0.40, 0.98))

            else:  # GENAI-V4
                amount = float(rng.uniform(1200.0, 5500.0))
                llm_intent = float(np.clip(rng.normal(0.35, 0.09), 0.12, 0.60))
                voice_jitter = float(np.clip(rng.normal(0.22, 0.07), 0.08, 0.45))
                face_dist = float(np.clip(rng.normal(0.25, 0.08), 0.08, 0.50))
                adv_index = float(np.clip(rng.normal(0.92, 0.06) * (1 - 0.35 * evasion), 0.50, 0.99))
                dev_risk = float(np.clip(rng.normal(0.40, 0.10), 0.15, 0.65))
                amt_dev = float(np.clip(rng.normal(0.45, 0.10), 0.18, 0.70))

            records.append({
                "interaction_id": f"GENAI-{rng.randint(100000, 999999):06X}",
                "user_id": f"USR-{rng.randint(1000, 9999)}",
                "amount": round(amount, 2),
                "timestamp": tx_time.isoformat(),
                "llm_semantic_intent_score": round(llm_intent, 4),
                "voice_biometric_jitter": round(voice_jitter, 4),
                "synthetic_face_embedding_dist": round(face_dist, 4),
                "adversarial_perturbation_index": round(adv_index, 4),
                "device_risk": round(dev_risk, 4),
                "amount_deviation": round(amt_dev, 4),
                "is_fraud": 1,
                "attack_id": "GENAI-001",
                "variant_id": vid,
                "variant_name": variant_names[vid]
            })

    df = pd.DataFrame(records)
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    if output_path is None:
        output_path = Path(__file__).parent / "genai_dataset.csv"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[OK] Generated {len(df):,} realistic GenAI rows -> Saved to {output_path}")
    return df

if __name__ == "__main__":
    generate_genai_dataset(25000)
