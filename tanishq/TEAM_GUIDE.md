# 🛡️ TEAM MASTER GUIDE — How All 4 Members Connect
## Mastercard Hackathon: HDC Fraud Detection System

---

## 🏗️ The Big Picture (How Our System Works)

Think of it like a **real bank's fraud detection pipeline**:

```
A customer makes a payment
        │
        ▼
┌───────────────────────────────────────────────────────────────────┐
│  PERSON 1 (You) — Attack Intelligence (GROUND TRUTH)             │
│  "What does fraud look like?"                                     │
│  Output: 6 signals, 5 variants, simulation rules                  │
│  Files: identify/                                                 │
│  Status: ✅ COMPLETE                                              │
└───────────┬───────────────────────────────────┬───────────────────┘
            │                                   │
            ▼                                   ▼
┌───────────────────────────┐   ┌───────────────────────────────────┐
│  PERSON 2 — Simulation    │   │  PERSON 3 — Detection Engine      │
│  "Generate fake attacks"  │   │  "Catch the fraud in real time"   │
│                           │   │                                   │
│  Reads: contract.json     │   │  Reads: 6 signals from pipeline/  │
│  Creates: Synthetic fraud │   │  Uses: HDC engine from hdc/       │
│  transactions for testing │   │  Output: FRAUD or LEGITIMATE      │
│                           │   │  + Risk Score (0-100%)            │
│  Files: simulate/         │   │  Files: Uses hdc/ and pipeline/   │
└───────────┬───────────────┘   └───────────────┬───────────────────┘
            │                                   │
            │    (Test data to validate)        │  (Risk score + verdict)
            │                                   │
            └───────────────┬───────────────────┘
                            │
                            ▼
            ┌───────────────────────────────────┐
            │  PERSON 4 — Response & Mitigation │
            │  "What action does the bank take?" │
            │                                   │
            │  Input: Risk score from Person 3  │
            │  Rules: 4 actions from Person 1   │
            │  Output: BLOCK / HOLD / REVIEW /  │
            │          STEP-UP AUTH              │
            │                                   │
            │  Files: response/                 │
            └───────────────────────────────────┘
```

---

## 📋 Step-by-Step for EVERY Team Member

---

### Step 0 (EVERYONE): Clone the Repository

Every team member runs this ONE command first:

```bash
git clone https://github.com/tanmaytamkhane/Fraud-Detection-.git
cd Fraud-Detection-
```

Then install dependencies:
```bash
pip install numpy pandas streamlit plotly
```

Verify it works:
```bash
python -X utf8 -m identify.registry
```
You should see `✅ ALL DATA IS VALID` and the 5 variant definitions.

---

### 🔴 PERSON 1 (You) — Attack Intelligence
**Status: ✅ COMPLETE**

Your job was to define the ground truth. It's done. Your ongoing responsibilities:
- If any team member needs a **new signal or parameter**, you add it to `identify/attacks.json`
- You are the **final authority** on what counts as fraud behavior
- Review Person 2's simulated data to make sure it follows your contract
- Review Person 4's response rules to make sure they match your mitigations

---

### 🟡 PERSON 2 — Simulation & Attack Generation
**Status: Awaiting their work**

**Their job**: Generate synthetic fraud transaction streams that follow YOUR ground truth recipes.

**What they already have from you:**
- `identify/contract.json` — The official rules
- `PERSON_2_HANDOFF.md` — Complete guide with code examples
- `simulate_starter.py` — Ready-to-run template

**What Person 2 should do:**

1. **Read** `PERSON_2_HANDOFF.md` first
2. **Run** `python simulate_starter.py` to see how the contract works
3. **Create** a folder called `simulate/` and build their generator:

```python
# simulate/generator.py — Person 2 writes this
from identify import AttackRegistry

registry = AttackRegistry().load()

# Get recipe for each variant
for variant_id in ["ATO-V1", "ATO-V2", "ATO-V3", "ATO-V4", "ATO-V5"]:
    v = registry.get_variant("ATO-001", variant_id)
    recipe = v.simulation_config
    # Generate 100 synthetic transactions per variant using the recipe
    # Save to simulate/synthetic_data.csv
```

4. **Output**: A CSV file (`simulate/synthetic_data.csv`) with fake fraud transactions tagged by variant
5. **Push** their code to the same GitHub repo

---

### 🟢 PERSON 3 — Detection Engine
**Status: Awaiting their work**

**Their job**: Take a transaction, run it through the HDC detection pipeline, and output a verdict.

**What they already have from you:**
- `PERSON_3_HANDOFF.md` (created below)
- The complete `pipeline/` and `hdc/` packages
- A working `main.py` that runs end-to-end

**What Person 3 should do:**

1. **Read** `PERSON_3_HANDOFF.md` first
2. **Understand** the 2 key functions they will use:
   - `engineer_features(df)` → Extracts 6 signals from raw transaction data
   - HDC Encoder + Classifier → Converts signals to verdict
3. **Create** a folder called `detect/` and build their detection service:

```python
# detect/scanner.py — Person 3 writes this
from pipeline.feature_engineer import engineer_features
from hdc.encoder import HDCEncoder
from hdc.model import HDCClassifier
from hdc.trainer import HDCTrainer

# Load and train model (or load a saved model)
# Accept a transaction → extract 6 signals → encode → predict → return verdict
```

4. **Connect with Person 2**: Run Person 2's synthetic data through the detector
5. **Connect with Person 4**: Send risk scores to Person 4's response engine
6. **Push** their code to the same GitHub repo

---

### 🔵 PERSON 4 — Response & Mitigation
**Status: Awaiting their work**

**Their job**: Based on Person 3's risk score, decide what action the bank takes.

**What they already have from you:**
- `PERSON_4_HANDOFF.md` (created below)
- The 4 official mitigation actions defined in `identify/taxonomy.json`
- The expected mitigation per variant in `identify/attacks.json`

**What Person 4 should do:**

1. **Read** `PERSON_4_HANDOFF.md` first
2. **Create** a folder called `response/` and build the response engine:

```python
# response/engine.py — Person 4 writes this
def decide_action(risk_score, variant_id=None):
    if risk_score >= 0.80:
        return "BLOCK"       # Freeze account immediately
    elif risk_score >= 0.60:
        return "HOLD"        # Hold transaction, notify cardholder
    elif risk_score >= 0.40:
        return "STEP_UP"     # Request OTP / additional verification
    else:
        return "APPROVE"     # Allow transaction
```

3. **Connect with Person 3**: Receive risk scores and apply response rules
4. **Add logging**: Track what action was taken for every transaction (for audit)
5. **Push** their code to the same GitHub repo

---

## 🔄 How Changes Flow Between Members

```
Person 1 pushes changes → git push origin main
Person 2 pulls changes  → git pull origin main
Person 3 pulls changes  → git pull origin main
Person 4 pulls changes  → git pull origin main
```

When any member finishes their work:
```bash
git add .
git commit -m "describe what you did"
git push origin main
```

Before starting work each day:
```bash
git pull origin main
```

---

## 📱 What to Message Each Person

### Message to Person 2:
> "Clone the repo: `git clone https://github.com/tanmaytamkhane/Fraud-Detection-.git`. Read `PERSON_2_HANDOFF.md` and run `python simulate_starter.py`. Your job is to create a `simulate/` folder and generate synthetic attack transaction streams following the 5 variant recipes in `identify/contract.json`."

### Message to Person 3:
> "Clone the repo: `git clone https://github.com/tanmaytamkhane/Fraud-Detection-.git`. Read `PERSON_3_HANDOFF.md`. Your job is to create a `detect/` folder and build a detection service using the existing `pipeline/` and `hdc/` packages. The HDC engine is already built — you just need to wire it up."

### Message to Person 4:
> "Clone the repo: `git clone https://github.com/tanmaytamkhane/Fraud-Detection-.git`. Read `PERSON_4_HANDOFF.md`. Your job is to create a `response/` folder and build the automated response engine. Based on the risk score from Person 3, you decide: BLOCK, HOLD, STEP-UP AUTH, or APPROVE."
