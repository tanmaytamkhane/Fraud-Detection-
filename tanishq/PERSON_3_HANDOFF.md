# 🔍 Person 3 Handoff — Detection Engine Integration Guide

> **To:** Person 3 (Detection Engine Lead)
> **From:** Person 1 (Attack Intelligence & Ground Truth Owner)
> **Topic:** How to build the real-time fraud detection service using the existing HDC engine

---

## 🎯 Your Job in One Sentence

> Take a raw transaction → Extract 6 fraud signals → Encode into a 10,000-D hypervector → Output FRAUD or LEGITIMATE + Risk Score

---

## 📦 What's Already Built for You

You do NOT need to build the machine learning model from scratch. It's done.

| Package | What it does | Key function you'll use |
|---|---|---|
| `pipeline/loader.py` | Loads raw CSV transaction data | `load_data(sample_frac)` |
| `pipeline/feature_engineer.py` | Extracts 6 fraud signals from raw data | `engineer_features(df)` |
| `pipeline/variant_labeler.py` | Labels fraud as ATO-V1 to V5 | `label_variants(signals, labels)` |
| `hdc/encoder.py` | Encodes 6 signals → 10,000-D hypervector | `encoder.encode_batch(signal_matrix)` |
| `hdc/model.py` | Classifies hypervector → Fraud/Legit | `classifier.predict_batch(encoded_hvs)` |
| `hdc/trainer.py` | Trains the HDC model | `trainer.train(X, y)` |
| `config.py` | All configuration & hyperparameters | Import constants from here |

---

## 🚀 Quick Start: Run the Full Pipeline Instantly

Before writing any code, verify the system works:

```bash
python -u -X utf8 main.py --sample 0.05
```

You'll see:
- Data loading → Feature extraction → HDC training → Evaluation report
- AUC-ROC: ~0.74, with per-variant detection breakdown

---

## 🛠️ How to Build Your Detection Service

### Step 1: Create Your Folder

```
detect/
├── __init__.py
└── scanner.py
```

### Step 2: Build the Scanner

```python
# detect/scanner.py
"""
Real-time fraud detection scanner.
Uses Person 1's feature engineering + HDC engine.
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import SIGNAL_NAMES
from pipeline.feature_engineer import engineer_features
from pipeline.loader import load_data
from pipeline.variant_labeler import label_variants
from hdc.encoder import HDCEncoder
from hdc.model import HDCClassifier
from hdc.trainer import HDCTrainer


class FraudScanner:
    """Real-time fraud detection scanner powered by HDC."""

    def __init__(self):
        self.encoder = HDCEncoder()
        self.classifier = HDCClassifier()
        self.trainer = HDCTrainer(encoder=self.encoder, classifier=self.classifier)
        self.is_trained = False

    def train_on_data(self, sample_frac=0.05):
        """Train the HDC model on real transaction data."""
        print("Loading training data...")
        df = load_data(sample_frac=sample_frac)
        df_features = engineer_features(df)

        X = df_features[SIGNAL_NAMES].values.astype(np.float32)
        y = df_features["isFraud"].values.astype(np.int32)

        print("Training HDC model...")
        self.trainer.train(X, y)
        self.is_trained = True
        print("Scanner ready!")

    def scan_signals(self, signal_values):
        """
        Scan a single transaction given its 6 signal values.

        Args:
            signal_values: list or array of 6 floats [0-1]
                [device_risk, address_mismatch, amount_deviation,
                 velocity, time_anomaly, channel_risk]

        Returns:
            dict with 'is_fraud', 'risk_score', 'variant', 'action'
        """
        signals = np.array(signal_values, dtype=np.float32).reshape(1, -1)
        encoded = self.encoder.encode_batch(signals)
        pred, _ = self.classifier.predict_batch(encoded)
        risk_score = float(self.classifier.get_fraud_score(encoded)[0])
        variant = label_variants(signals)[0]

        # Determine bank action based on risk score
        if risk_score >= 0.80:
            action = "BLOCK"
        elif risk_score >= 0.60:
            action = "HOLD"
        elif risk_score >= 0.40:
            action = "STEP_UP_AUTH"
        else:
            action = "APPROVE"

        return {
            "is_fraud": bool(pred[0] == 1),
            "risk_score": round(risk_score, 4),
            "risk_percent": f"{risk_score * 100:.1f}%",
            "variant": variant,
            "action": action,
        }

    def scan_batch(self, signal_matrix):
        """
        Scan a batch of transactions.

        Args:
            signal_matrix: numpy array of shape (N, 6)

        Returns:
            list of result dicts
        """
        return [self.scan_signals(row) for row in signal_matrix]


# Quick test
if __name__ == "__main__":
    scanner = FraudScanner()
    scanner.train_on_data(sample_frac=0.01)

    # Test the 5 attack variants
    test_cases = [
        ("ATO-V1 (Loud)",      [0.95, 0.85, 0.90, 0.40, 0.20, 0.90]),
        ("ATO-V4 (Ghost)",     [0.20, 0.10, 0.25, 0.10, 0.10, 0.20]),
        ("Legitimate User",    [0.15, 0.05, 0.10, 0.10, 0.15, 0.15]),
    ]

    for name, signals in test_cases:
        result = scanner.scan_signals(signals)
        print(f"  {name}: {result['action']} (Risk: {result['risk_percent']})")
```

### Step 3: Use with Person 2's Simulated Data

```python
# After Person 2 creates simulate/synthetic_data.csv:
import pandas as pd

scanner = FraudScanner()
scanner.train_on_data(sample_frac=0.05)

# Load Person 2's synthetic test data
synthetic = pd.read_csv("simulate/synthetic_data.csv")
features = engineer_features(synthetic)
X = features[SIGNAL_NAMES].values

results = scanner.scan_batch(X)
for r in results:
    print(f"Fraud: {r['is_fraud']}, Risk: {r['risk_percent']}, Action: {r['action']}")
```

### Step 4: Send Results to Person 4

```python
# Person 3 passes results to Person 4's response engine:
from response.engine import ResponseEngine  # Person 4's code

response_engine = ResponseEngine()
for result in results:
    response_engine.execute_action(
        transaction_id=...,
        risk_score=result["risk_score"],
        action=result["action"],
        variant=result["variant"]
    )
```

---

## 📊 The 6 Signals You're Working With

| # | Signal Name | What It Measures | Range |
|---|---|---|---|
| 1 | `device_risk` | Is the device new/unrecognized? | 0.0 (known) → 1.0 (new) |
| 2 | `address_mismatch` | Does billing address match card location? | 0.0 (match) → 1.0 (mismatch) |
| 3 | `amount_deviation` | How far is amount from user's normal? | 0.0 (normal) → 1.0 (extreme) |
| 4 | `velocity` | How fast are transactions happening? | 0.0 (normal) → 1.0 (rapid burst) |
| 5 | `time_anomaly` | Is it an unusual time (e.g. 3 AM)? | 0.0 (normal hours) → 1.0 (night) |
| 6 | `channel_risk` | Is the product/channel high-risk? | 0.0 (safe) → 1.0 (risky) |

---

## ✅ Verification

Run your scanner self-test:
```bash
python -m detect.scanner
```

Run the full pipeline benchmark:
```bash
python -u -X utf8 main.py --sample 0.05
```
