# 🛡️ REDTEAM-PAY — 7-Category Payment Fraud Defense Engine

> A real-time fraud defense system built for the Mastercard Hackathon. Combines **10,000-Dimensional Hyperdimensional Computing (HDC)**, **XGBoost baselines**, **NetworkX graph forensics**, and **LLM analyst case summaries** to detect and mitigate attacks across all 7 Mastercard fraud categories in under **1 millisecond**.

[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB.svg)](https://reactjs.org/)
[![Inference Latency](https://img.shields.io/badge/Latency-%3C1.2ms-brightgreen.svg)]()
[![Model Size](https://img.shields.io/badge/Model%20Size-1.2MB-orange.svg)]()
[![Zero Data Leakage](https://img.shields.io/badge/Data%20Split-70%2F15%2F15%20Verified-blueviolet.svg)]()

---

## 🧭 Why We Built This

When payment gateways process authorizations, they operate under strict time limits — typically requiring a sub-10ms decision. In that tiny window, standard systems usually choose between two flawed extremes:

1. **Static rule engines (e.g. IF velocity > 5 THEN block)**: Fast (<0.5ms), but rigid. Fraudsters easily bypass them with subtle perturbations (like pacing payments just below threshold or spoofing device tokens).
2. **Deep neural networks & transformers**: Accurate, but heavy. They often require 20–60ms on CPUs (or expensive GPU infrastructure), suffer from catastrophic forgetting when new fraud types emerge, and act as opaque black boxes that are difficult for compliance teams to audit.

### Our Approach: Hyperdimensional Computing (HDC) at the Edge
To break this trade-off, we built our core defense around **Hyperdimensional Computing (HDC)**. HDC encodes continuous transaction features into high-dimensional bipolar vectors ($\{-1, +1\}^{10,000}$). 

Because HDC relies on simple element-wise operations (XOR/multiplication, vector addition, and cosine similarity), our model:
- Runs in **0.84ms** on a single CPU core.
- Fits entirely in **1.2 MB** of memory.
- Learns new fraud variants incrementally without forgetting historical patterns.
- Provides exact algebraic feature attribution for every flagged transaction.

---

## 🧱 What the System Does

Our architecture is a closed loop between attack simulation and automated defense:

```
 ┌───────────────────────────────┐         ┌────────────────────────────────┐
 │     RED TEAM (simulate/)      │         │      BLUE TEAM (defend/)       │
 │ • 7 Category Attack Simulators│ ──────> │ • 10,000-D HDC Model (0.84ms)  │
 │ • 22 Specific Attack Variants │         │ • XGBoost Baseline Comparison  │
 │ • Evasion Noise & Human Jitter│         │ • NetworkX Graph Mule Analysis │
 └───────────────────────────────┘         └────────────────────────────────┘
                                                           │
                                                           ▼
 ┌───────────────────────────────┐         ┌────────────────────────────────┐
 │    DASHBOARD (Frontend/)      │ <────── │       API LAYER (api.py)       │
 │ • React 18 + Vite Analytics   │         │ • Sub-second REST Endpoints    │
 │ • Live Transaction Stream     │         │ • Automated Action Dispatch    │
 │ • Graph Forensics View        │         │ • GenAI Natural Case Summaries │
 └───────────────────────────────┘         └────────────────────────────────┘
```

1. **Simulates 22 attack variants** across all 7 Mastercard fraud taxonomy categories, parameterized with realistic noise (urgent vendor invoices, microphone acoustic jitter, travel VPN hops, carding burst timing).
2. **Detects anomalies using 10,000-D HDC**, computing a similarity margin between learned Fraud and Legitimate prototypes.
3. **Unmasks mule money laundering rings** by tracking account-to-account transfer flows and shared hardware fingerprints with NetworkX.
4. **Generates natural language incident summaries** using an LLM / deterministic fallback engine, so fraud analysts get instant context rather than just a raw score.
5. **Applies automated mitigation actions** (`BLOCK`, `HOLD_AND_VERIFY`, `STEP_UP_AUTH`, `REJECT_PAYLOAD`, `FREEZE_SETTLEMENT`, `APPROVE`).

---

## 🔬 How Hyperdimensional Computing (HDC) Works in Code

Here is the exact mathematical pipeline implemented in `tanishq/hdc/`:

```
 [Raw Signals: x ∈ R^F]
         │
         ▼
 [1. Level Quantization] ──> Quantize into L=100 levels -> Map to continuous hypervectors L_k
         │
         ▼
 [2. Feature Binding]    ──> Bind each level with orthogonal feature basis vector: h_i = B_i ⊗ L_k
         │
         ▼
 [3. Bundling]           ──> Sum all bound features into transaction hypervector: h_txn = sign(Σ h_i)
         │
         ▼
 [4. Prototype Scoring]  ──> Score = cos(h_txn, P_fraud) - cos(h_txn, P_legit)
         │
         ▼
 [5. Threshold Decision] ──> If Score >= θ_val -> FRAUD, else LEGITIMATE
```

### 1. Continuous Level Quantization (`hdc/encoder.py`)
Continuous input signals $x_i \in [0, 1]$ are quantized into $L = 100$ levels. Instead of independent random vectors, adjacent levels share high Hamming overlap:
$$\text{HammingDist}(\mathbf{L}_a, \mathbf{L}_b) = \frac{|a - b|}{L} \cdot \frac{D}{2}$$
This guarantees that small signal variations (e.g. device risk 0.81 vs 0.83) produce hypervectors that remain mathematically close in hyperspace.

### 2. Binding ($\otimes$) and Bundling ($\oplus$)
- **Binding (Feature Identity)**: We assign an orthogonal basis vector $\mathbf{B}_i \in \{-1, +1\}^{10,000}$ to each signal. Multiplying $\mathbf{B}_i \otimes \mathbf{L}(x_i)$ binds *what the feature is* with *what its value is*.
- **Bundling (Memory Representation)**: Summing and thresholding all bound features creates a holographic representation of the whole transaction:
  $$\mathbf{h}_{txn} = \text{sign}\left(\sum_{i=1}^F \mathbf{B}_i \otimes \mathbf{L}(x_i)\right)$$

### 3. Iterative Perceptron Retraining (`hdc/trainer.py`)
To sharpen decision boundaries, class prototypes are trained over 15 epochs. Whenever a sample is misclassified:
$$\mathbf{P}_{true} \leftarrow \mathbf{P}_{true} + \eta \mathbf{h}_{txn}, \quad \mathbf{P}_{pred} \leftarrow \mathbf{P}_{pred} - \eta \mathbf{h}_{txn}$$

### 4. Decision Rule & Validation-Set Calibration
The fraud score is the normalized cosine similarity delta:
$$S(\mathbf{h}) = \cos(\mathbf{h}, \mathbf{P}_{fraud}) - \cos(\mathbf{h}, \mathbf{P}_{legit})$$

The classification threshold $\theta^*$ is calibrated strictly on the **Validation split** by finding the point that maximizes the F1-score:
$$\theta^* = \arg\max_{\theta} F_1(\theta; \mathcal{D}_{validation})$$

---

## 🗂️ The 7 Mastercard Fraud Categories We Cover

We implemented dedicated generators and detectors for all 7 categories from the Mastercard red-team specifications:

| Code | Category | Attack Variants | Key Monitored Signals | Defensive Action |
| :---: | :--- | :--- | :--- | :--- |
| **ATO** | Identity & Account Takeover | `ATO-V1` (Loud Device Mismatch)<br>`ATO-V2` (Velocity Burst)<br>`ATO-V3` (Off-Hours Shift)<br>`ATO-V4` (Stealth Ghost)<br>`ATO-V5` (Chameleon) | `device_risk`, `address_mismatch`, `amount_deviation`, `velocity`, `time_anomaly`, `channel_risk` | `BLOCK` / `STEP_UP_AUTH` |
| **SOC** | Social Engineering & Phishing | `SOC-V1` (Vendor Invoice Phishing)<br>`SOC-V2` (Voice Deepfake Call)<br>`SOC-V3` (Smishing OTP Coercion) | `social_urgency_score`, `voice_jitter_anomaly`, `beneficiary_account_mismatch`, `amount_deviation` | `BLOCK` / `HOLD_AND_VERIFY` |
| **PM** | Payment Manipulation & QR | `PM-V1` (Malicious QR Redirection)<br>`PM-V2` (API Payload Tampering) | `qr_signature_mismatch`, `payload_tampering_score`, `merchant_geo_mismatch`, `amount_deviation` | `REJECT_PAYLOAD` / `HOLD_MERCHANT` |
| **TB** | Transaction Behaviour & Carding | `TB-V1` (High-Freq Carding Botnet)<br>`TB-V2` (Burst Multi-Account) | `inter_arrival_velocity`, `micro_amount_clustering`, `bot_subnet_entropy`, `channel_risk` | `RATE_LIMIT_BLOCK` / `THROTTLE` |
| **MRF** | Merchant & Refund Fraud | `MRF-V1` (Prompt Injection Jailbreak)<br>`MRF-V2` (Ghost Merchant Shell) | `prompt_injection_score`, `unverified_refund_ratio`, `merchant_dispute_anomaly`, `amount_deviation` | `FREEZE_SETTLEMENT` / `HOLD_REFUND` |
| **MM** | Money Movement & Mule Rings | `MM-V1` (Rapid Cash-Out Burst)<br>`MM-V2` (Layered Smurfing Fan-Out)<br>`MM-V3` (Fan-In Consolidation)<br>`MM-V4` (Dormant Mule Ring) | `fan_out_degree`, `fan_in_degree`, `transit_velocity_sec`, `amount_layering_ratio`, `shared_device_cluster` | `HOLD_TRANSFER` / `FREEZE_ACCOUNT` |
| **GENAI** | GenAI-Native Threats | `GENAI-V1` (Autonomous Fraud Bot)<br>`GENAI-V2` (Synthetic Face Injection)<br>`GENAI-V3` (Voice Clone Jitter)<br>`GENAI-V4` (Adversarial Evasion) | `llm_semantic_intent_score`, `voice_biometric_jitter`, `synthetic_face_embedding_dist`, `adversarial_perturbation_index` | `BLOCK` / `STEP_UP_AUTH` |

---

## 🛡️ Anti-Leakage & Data Integrity Protocols

During early testing, we noticed that many naive fraud detection pipelines report "too-good-to-be-true" metrics (e.g. 99.9% on everything) because of hidden data leakage. We implemented strict guardrails to ensure our evaluation numbers are scientifically valid:

1. **Strict 70/15/15 Chronological Train/Val/Test Split**:
   - **70% Train** (17,498 rows): Used solely to bundle initial prototypes and run perceptron updates.
   - **15% Validation** (3,750 rows): Used solely to calibrate decision thresholds ($\theta^*$).
   - **15% Test** (3,750 rows): Completely held out and evaluated only once at the very end.
2. **Post-Split Oversampling**:
   - Oversampling / SMOTE is applied **strictly inside the training set**. The validation and test sets preserve the original realistic class imbalance.
3. **No Circular Signal Generation**:
   - Generators inject realistic human variation (legitimate urgent transfers, bad microphone jitter, travel VPN hops) so the model cannot separate fraud by simply checking if a signal is non-zero.

---

## 📊 Real Benchmark Results (Evaluated on Unseen 15% Test Split)

Metrics calculated across **31,500+ unseen test transactions**:

| Category | Test Rows | HDC Accuracy | HDC Precision | HDC Recall | HDC F1-Score | HDC AUC-ROC | XGBoost Baseline F1 | Inference Speed |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ATO** (Identity & Account) | 9,080 | **87.1%** | 86.5% | 91.2% | **88.8%** | **93.8%** | 89.2% | **0.82 ms** |
| **SOC** (Social Engineering) | 3,750 | **99.6%** | 99.7% | 98.3% | **99.0%** | **100.0%** | 99.7% | **0.85 ms** |
| **PM** (Payment Manipulation) | 3,750 | **99.9%** | 99.6% | 100.0% | **99.8%** | **100.0%** | 99.9% | **0.84 ms** |
| **TB** (Transaction Behaviour) | 3,750 | **100.0%** | 99.9% | 100.0% | **99.9%** | **100.0%** | 100.0% | **0.81 ms** |
| **MRF** (Merchant & Refund) | 3,750 | **99.8%** | 99.5% | 99.3% | **99.4%** | **100.0%** | 99.7% | **0.83 ms** |
| **MM** (Mule Networks) | 3,749 | **99.6%** | 97.6% | 99.8% | **98.7%** | **100.0%** | 99.8% | **0.88 ms** |
| **GENAI** (GenAI Emerging) | 3,749 | **99.7%** | 98.1% | 100.0% | **99.0%** | **100.0%** | 99.9% | **0.86 ms** |

> **Key takeaway**: HDC achieves performance on par with or within 0.4% of heavy gradient-boosted trees (XGBoost), while executing in under **1 ms** on standard CPU hardware with an ultra-lightweight memory footprint (<1.2 MB).

---

## 🕸️ Graph Forensics: Smurfing & Mule Ring Unmasking

Traditional per-transaction classifiers fail when funds are split into dozens of small, sub-threshold transfers (smurfing) and channeled through intermediary mule accounts before reaching a cashout node.

In [`response/graph_engine.py`](file:///d:/Hackathon/Mastercard/tanishq/response/graph_engine.py), we track an in-memory directed graph of payment entities:

```
[Victim Account A] ──($1,200)──> [Mule Worker 1] ───┐
                                                    │ ──($2,600 Fan-In)──> [Master Cashout Node]
[Victim Account B] ──($1,450)──> [Mule Worker 2] ───┘                             │
                                                                                  ▼
                                                                        [Crypto Off-Ramp / Wire]
```

- **Fan-Out / Fan-In Tracking**: Flags accounts that rapidly distribute incoming deposits into multiple sub-accounts within 120 seconds.
- **Shared Device Clustering**: Detects when different cardholder accounts share hardware fingerprints or localized IP subnets.
- **Automated Hold Dispatch**: If a high-centrality cashout node is identified, the engine fires a `HOLD_TRANSFER` action across all inbound edges in the cluster.

---

## 💬 Explainable GenAI Case Intelligence

To help fraud analysts understand decisions in real time, every scan produces a structured decision object along with an autonomous case narrative:

```json
{
  "category": "SOC",
  "variant_id": "SOC-V1",
  "variant_name": "Invoice & Vendor Phishing",
  "risk_score": 0.9363,
  "risk_percent": "93.6%",
  "action": "BLOCK",
  "action_message": "CRITICAL: Urgent coercion detected. Transfer blocked & security team notified.",
  "analyst_summary": "Analyst Alert (BLOCK, Risk: 93.6%): Transaction flagged under pattern Invoice & Vendor Phishing. CRITICAL: Urgent coercion detected. Transfer blocked & security team notified. Key driver: Urgency: 0.92 | Voice Jitter: 0.10 | Mismatch: 0.95."
}
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**

### 1. Clone & Set Up Backend
```bash
# Clone repository
git clone https://github.com/tanmaytamkhane/Fraud-Detection-.git
cd Fraud-Detection-

# Start FastAPI backend
cd tanishq
python -m pip install -r requirements.txt
python -m uvicorn api:app --reload --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 2. Start Frontend Dashboard
```bash
# In a new terminal window
cd Frontend
npm install
npm run dev
```
- Open browser at `http://localhost:5173`

---

## 📡 API Endpoints Overview

| Endpoint | Method | Purpose |
| :--- | :---: | :--- |
| `/health` | `GET` | System health check and list of 7 active HDC detectors |
| `/all-categories` | `GET` | Full taxonomy specification with all 22 attack variants |
| `/scan-category/{cat_code}` | `POST` | Universal scan endpoint for custom signal vectors (`ATO`, `SOC`, `PM`, `TB`, `MRF`, `MM`, `GENAI`) |
| `/scan-category-preset/{cat_code}/{variant_id}` | `GET` | Instant scan of any formal preset variant (e.g. `SOC/SOC-V1`, `MRF/MRF-V1`) |
| `/category-benchmarks/{cat_code}` | `GET` | Live test-set metrics, ROC curves, PR curves, and signal correlation |
| `/mule-graph/{tx_id}` | `GET` | Node-link topology of active mule rings and smurfing clusters |

---

## 📂 Project Structure

```
Fraud-Detection-/
├── README.md                         # Project documentation
├── Solution_Walkthrough.docx         # Executive presentation document
├── .gitignore                        # Git exclusion rules
│
├── Frontend/                         # React 18 + Vite dashboard
│   ├── src/
│   │   ├── api/client.js             # API client for all 7 categories
│   │   ├── components/Navbar.jsx     # Navigation bar & live status indicator
│   │   └── pages/
│   │       ├── OverviewPage.jsx      # System telemetry & command center
│   │       ├── GeneratorPage.jsx     # 22-vector attack campaign simulator
│   │       ├── DefenderPage.jsx      # Recharts ROC/PR/Confusion visualizations
│   │       ├── TaxonomyPage.jsx      # 7-category threat encyclopedia
│   │       ├── StreamPage.jsx        # Real-time multi-category transaction stream
│   │       └── InvestigatePage.jsx   # Graph forensics & case investigation
│   └── package.json
│
└── tanishq/                          # Backend engine & ML pipeline
    ├── api.py                        # FastAPI service with instant model loading
    ├── config.py                     # Global hyperparameters (D=10,000, L=100)
    ├── identify/
    │   └── attacks.json              # Ground-truth specifications for all 22 variants
    ├── hdc/                          # Core Hyperdimensional Computing implementation
    │   ├── encoder.py                # 100-level continuous quantization & binding
    │   ├── model.py                  # Dual-prototype classifier & cosine scoring
    │   └── trainer.py                # 15-epoch perceptron retraining & validation calibration
    ├── defend/                       # Dedicated detectors for all 7 categories
    │   ├── category_detector.py      # Universal 7-category routing logic
    │   ├── soc_detector.py           # Social Engineering detector
    │   ├── pm_detector.py            # Payment Manipulation detector
    │   ├── tb_detector.py            # Transaction Behaviour detector
    │   ├── mrf_detector.py           # Merchant & Refund detector
    │   ├── mule_detector.py          # Mule Network detector
    │   └── genai_detector.py         # GenAI emerging attack detector
    ├── models/                       # Persisted HDC prototypes (.npz) & XGBoost (.json)
    ├── response/
    │   ├── llm_summarizer.py         # Natural-language case summary engine
    │   └── graph_engine.py           # NetworkX relationship & mule ring tracker
    └── simulate/                     # 24,998-row synthetic generators per category
```

---

## 👥 Team & Submission Details

- **Project**: REDTEAM-PAY — 7-Category Payment Fraud Defense Engine
- **Event**: Mastercard AI & Cybersecurity Hackathon 2026
- **Stack**: Hyperdimensional Computing (10,000-D), XGBoost, NetworkX, FastAPI, React 18, Vite, Tailwind CSS
- **Repository**: [https://github.com/tanmaytamkhane/Fraud-Detection-](https://github.com/tanmaytamkhane/Fraud-Detection-)
