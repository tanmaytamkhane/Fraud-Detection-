# 🛡️ Hyperdimensional Computing (HDC) Fraud Detection System

> **Mastercard Hackathon — AI Fraud Intelligence & Detection**  
> An end-to-end fraud detection architecture powered by **Hyperdimensional Computing (HDC)** and formal **Attack Intelligence Ground Truth** evaluated on real-world financial transaction data (IEEE-CIS 590,540 transactions).

---

## 🌟 Architecture Overview

```
Mastercard Hackathon Project Structure:
├── identify/           # Phase 1: Attack Intelligence & Ground Truth (Person 1)
│   ├── taxonomy.json   # 6 Signals, 4 Mitigations, Severity scale
│   ├── attacks.json    # Complete ATO-001 definitions & 5 behavioral variants
│   ├── contract.json   # Official Attack Contract exported for Person 2
│   ├── schemas.py      # Dataclass validation & integrity checks
│   └── registry.py     # AttackRegistry API
│
├── pipeline/           # Feature Engineering & Variant Classification
│   ├── loader.py       # High-efficiency loading & merging of transaction & identity data
│   ├── feature_engineer.py # 6 domain-specific ATO signals
│   └── variant_labeler.py  # Maps transactions to ATO-V1 through V5
│
├── hdc/                # Hyperdimensional Computing Engine (from scratch in NumPy)
│   ├── encoder.py      # 10,000-D hypervector level quantization & binding
│   ├── model.py        # Prototype classifier with calibrated decision threshold
│   └── trainer.py      # Iterative retraining with class-imbalance oversampling
│
├── evaluate/           # Diagnostics & Reporting
│   ├── metrics.py      # Accuracy, Precision, Recall, F1, AUC-ROC
│   ├── report.py       # Classification report & per-signal importance
│   └── variant_analysis.py # Per-variant detection breakdown
│
├── api.py              # Production FastAPI REST Backend (Bridge for Frontend)
├── config.py           # Master parameters & configuration
├── main.py             # End-to-end pipeline runner
├── simulate_starter.py # Person 2 integration starter template
├── TEAM_GUIDE.md       # Master coordination guide for all 4 team members
├── PERSON_2_HANDOFF.md # Complete Person 2 simulation specifications
├── PERSON_3_HANDOFF.md # Complete Person 3 detection integration guide
└── PERSON_4_HANDOFF.md # Complete Person 4 automated response guide
```

---

## 🔬 The 5 Behavioral ATO Variants (Phase 1 Ground Truth)

| Variant ID | Name | Post-Compromise Behavior | Expected Difficulty |
|---|---|---|---|
| **ATO-V1** | **High-Value New Device (Loud)** | New Device + High Amount Spike + New Beneficiary | Easy |
| **ATO-V2** | **Velocity Burst (Known Device)** | Compromised Known Device + Rapid Sequence of Transactions | Moderate |
| **ATO-V3** | **Off-Hours Location Shift** | New Geographic Location + Nighttime Transaction Window | Moderate |
| **ATO-V4** | **Subtle Deviation (The Ghost)** | Known Device + Known Beneficiary + Barely Noticeable Amount Bump | Very Hard |
| **ATO-V5** | **Multi-Signal (The Chameleon)** | Simultaneous subtle shifts across time, location, and velocity | Hard |

---

## 📊 Live HDC Benchmark Results (Validation Set)

Evaluated on **29,527 real transactions** from the IEEE-CIS fraud detection dataset:

```
================================================================================
  METRIC                        SCORE
================================================================================
  AUC-ROC                       0.7420
  Accuracy                      85.79%
  Recall (Overall Fraud Caught) 45.91%
  Precision                     12.30% (3.4x higher than natural fraud rate)
================================================================================

  PER-VARIANT DETECTION PROOF:
  ▶ ATO-V1 (Loud Takeover):          100.0% Detection Rate ✅
  ▶ ATO-V2 (Velocity Burst):          45.0% Detection Rate ⚠️
  ▶ ATO-V3 (Location Shift):         100.0% Detection Rate ✅
  ▶ ATO-V4 (The Ghost - Subtle):      17.2% Detection Rate 🚨 (Confirms stealth hypothesis)
  ▶ ATO-V5 (The Chameleon):           69.0% Detection Rate 💡 (HDC multi-signal correlation)
================================================================================
```

---

## 🚀 Quick Start & Execution

### 1. Start the FastAPI REST Backend (For Web Frontend)
```bash
python -m uvicorn api:app --reload --port 8000
```
Interactive API docs available at: **`http://localhost:8000/docs`**

#### Core API Endpoints:
- `POST /scan` → Scans 6 transaction signals and returns Risk Score, Verdict, and Bank Action.
- `GET /scan-preset/{variant_id}` → Instant scan for `ATO-V1`, `ATO-V2`, `ATO-V3`, `ATO-V4`, `ATO-V5`, or `LEGIT`.
- `GET /variants` → Full metadata of all 5 attack variants.
- `GET /benchmarks` → Real IEEE-CIS validation metrics.
- `GET /contract` → Attack contract JSON for Person 2.

---

### 2. Run the Full HDC Pipeline (Terminal)
```bash
# Fast test on 5% sample (~30k rows)
python -u -X utf8 main.py --sample 0.05

# Full dataset run (590k rows)
python -u -X utf8 main.py
```

### 3. Test Ground Truth & Contract (Person 1)
```bash
python -X utf8 -m identify.registry
```

### 4. Attack Simulation Starter (Person 2)
```bash
python simulate_starter.py
```

---

## 🤝 Team Integration Handoff Guides

Every team member has a dedicated, complete integration guide:
- 📖 **[`TEAM_GUIDE.md`](TEAM_GUIDE.md)** — Master overview of how all 4 members connect.
- 🟡 **[`PERSON_2_HANDOFF.md`](PERSON_2_HANDOFF.md)** — Simulation engine & attack generation recipes.
- 🟢 **[`PERSON_3_HANDOFF.md`](PERSON_3_HANDOFF.md)** — Real-time detection service integration.
- 🔵 **[`PERSON_4_HANDOFF.md`](PERSON_4_HANDOFF.md)** — Automated response & bank mitigation engine.
