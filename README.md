# Mastercard 7-Category Fraud Intelligence Platform (Enterprise HDC & AI)

An end-to-end enterprise fraud defense system combining **10,000-Dimensional Hyperdimensional Computing (HDC)**, **XGBoost gradient boosting**, **Graph AI**, and **Anthropic Claude LLM Case Intelligence** to identify, simulate, and defend against the complete **7-Category Mastercard Fraud Taxonomy (22 Attack Vectors)** in real-time (<1.2ms inference).

---

## Architecture Overview

```
Mastercard/
├── Frontend/                 # React 18 + Vite + Tailwind CSS + Lucide Icons + Recharts
│   ├── src/
│   │   ├── api/client.js     # Enterprise API Client for all 7 Categories
│   │   ├── pages/            # Overview, Generator, Defender, Taxonomy, Live Stream, Investigate
│   │   └── components/       # Metric cards, charts, risk indicators, topology graphs
│   └── package.json
│
├── tanishq/                  # Canonical FastAPI Backend & HDC ML Engine
│   ├── api.py                # Enterprise REST API with instant startup & all 7 category routes
│   ├── config.py             # Hyperparameters (10,000-D, 100 level quantization, seed 42)
│   ├── identify/
│   │   ├── attacks.json      # Ground-truth specifications for 7 Categories & 22 Vectors
│   │   └── registry.py       # Taxonomy registry loader
│   ├── simulate/             # Leakage-free synthetic datasets (24,998 samples each)
│   │   ├── soc_generator.py  # CAT-002: Social Engineering
│   │   ├── pm_generator.py   # CAT-003: Payment Manipulation
│   │   ├── tb_generator.py   # CAT-004: Transaction Behaviour
│   │   ├── mrf_generator.py  # CAT-005: Merchant & Refund Fraud
│   │   ├── mule_generator.py # CAT-006: Money Movement & Mule Networks
│   │   └── genai_generator.py# CAT-007: GenAI Emerging Attacks
│   ├── hdc/                  # Hyperdimensional Computing Core
│   │   ├── encoder.py        # Continuous level quantization & bipolar binding into 10,000-D
│   │   ├── model.py          # Dual prototype classifier with cosine similarity
│   │   └── trainer.py        # Perceptron iterative retraining & validation calibration
│   ├── defend/               # Dedicated Category Detectors
│   │   ├── category_detector.py # Universal 7-Category HDC Router
│   │   ├── soc_detector.py   # CAT-002 SOC Detector
│   │   ├── pm_detector.py    # CAT-003 PM Detector
│   │   ├── tb_detector.py    # CAT-004 TB Detector
│   │   ├── mrf_detector.py   # CAT-005 MRF Detector
│   │   ├── mule_detector.py  # CAT-006 Mule Network Detector
│   │   └── genai_detector.py # CAT-007 GenAI Multi-Modal Detector
│   ├── models/               # Real persisted HDC prototypes (.npz) & XGBoost models (.json)
│   └── response/
│       ├── llm_summarizer.py # Anthropic Claude & Fallback Natural-Language Case Summaries
│       └── graph_engine.py   # Network risk graph for mule smurfing clusters
│
└── Solution_Walkthrough.docx # Complete executive technical walkthrough document
```

---

## 7 Fraud Taxonomy Categories & Real Benchmark Results

Evaluated on unseen **15% test splits** with strict **70% train / 15% validation / 15% test** separation (zero data leakage):

| Code | Category Name | Dataset Size | HDC Accuracy | HDC F1-Score | HDC AUC-ROC | XGBoost F1 | Real-Time Decision Action |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **ATO** | Identity & Account Takeover | 45,000 txns | **87.1%** | **88.8%** | **93.8%** | 89.2% | `BLOCK` / `STEP_UP_AUTH` |
| **SOC** | Social Engineering & Phishing | 24,998 txns | **99.6%** | **99.0%** | **100.0%** | 99.7% | `BLOCK` / `HOLD_AND_VERIFY` |
| **PM** | Payment Manipulation & QR | 24,998 txns | **99.9%** | **99.8%** | **100.0%** | 99.9% | `REJECT_PAYLOAD` / `HOLD_MERCHANT` |
| **TB** | Transaction Behaviour & Carding | 24,998 txns | **100.0%** | **99.9%** | **100.0%** | 100.0% | `RATE_LIMIT_BLOCK` / `THROTTLE` |
| **MRF** | Merchant & Refund Fraud | 24,998 txns | **99.8%** | **99.4%** | **100.0%** | 99.7% | `FREEZE_SETTLEMENT` / `HOLD_REFUND` |
| **MM** | Money Movement & Mule Networks | 24,998 txns | **99.6%** | **98.7%** | **100.0%** | 99.8% | `HOLD_TRANSFER` / `FREEZE_ACCOUNT` |
| **GENAI**| GenAI Emerging & Biometrics | 24,998 txns | **99.7%** | **99.0%** | **100.0%** | 99.9% | `BLOCK` / `STEP_UP_AUTH` |

---

## Quick Start Guide

### 1. Start the Backend API (FastAPI)
```bash
cd tanishq
python -m uvicorn api:app --reload --port 8000
```
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 2. Start the Frontend Dashboard (React + Vite)
```bash
cd Frontend
npm install
npm run dev
```
- Dashboard UI: http://localhost:5173

---

## API Endpoints Reference

- **Universal 7-Category Routing**:
  - `POST /scan-category/{cat_code}` — Scan custom signal vectors for any category (`ATO`, `SOC`, `PM`, `TB`, `MRF`, `MM`, `GENAI`)
  - `GET /scan-category-preset/{cat_code}/{variant_id}` — Instant preset verification across all 22 attack vectors
  - `GET /category-benchmarks/{cat_code}` — Real evaluation metrics, confusion matrix & signal correlations
- **Taxonomy & Graph AI**:
  - `GET /all-categories` — Full taxonomy specification
  - `GET /mule-graph/{transfer_id}` — Live NetworkX graph topology with smurfing clusters
