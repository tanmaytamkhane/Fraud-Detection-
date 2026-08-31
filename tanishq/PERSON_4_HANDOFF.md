# 🛑 Person 4 Handoff — Response & Mitigation Engine

> **To:** Person 4 (Response & Mitigation Lead)
> **From:** Person 1 (Attack Intelligence & Ground Truth Owner)
> **Topic:** How to build the automated bank response engine

---

## 🎯 Your Job in One Sentence

> Receive a fraud risk score from Person 3 → Decide the bank's action → Execute it (Block, Hold, Step-Up Auth, or Approve) → Log the decision for audit

---

## 📦 What's Already Defined for You

Person 1 has established exactly **4 mitigation actions** in the Ground Truth (`identify/taxonomy.json`). You must implement these:

| Action ID | Action Name | When to Trigger | What It Does |
|---|---|---|---|
| `block` | **Account Block** | Risk ≥ 80% | Immediately freeze the account. Block ALL transactions. Alert fraud team. |
| `hold` | **Transaction Hold** | Risk 60–79% | Hold this specific transaction. Send SMS/push notification to cardholder. |
| `step_up_authentication` | **Step-Up Auth** | Risk 40–59% | Request additional verification (OTP, biometric, security question). |
| `review` | **Analyst Review** | Risk 20–39% | Flag for manual review by a human fraud analyst. |
| *(implicit)* | **Approve** | Risk < 20% | Allow the transaction to proceed normally. |

---

## 🧪 What Each Variant Should Trigger

Person 1 has defined the **expected mitigation** for each attack variant:

| Variant | Attack Type | Expected Action | Why |
|---|---|---|---|
| **ATO-V1** | Loud New Device Takeover | **BLOCK** | Multiple critical signals fired — obvious attack |
| **ATO-V2** | Velocity Burst Known Device | **HOLD** | High speed is suspicious but device is known |
| **ATO-V3** | Off-Hours Location Shift | **STEP-UP AUTH** | Could be legitimate travel — verify first |
| **ATO-V4** | Subtle Deviation (Ghost) | **REVIEW** | Almost invisible — needs human judgment |
| **ATO-V5** | Multi-Signal Chameleon | **STEP-UP AUTH** | Combined weak signals — verify identity |

---

## 🚀 How to Access the Ground Truth Rules in Code

```python
from identify import AttackRegistry

registry = AttackRegistry().load()

# Get the 4 official mitigation actions
mitigations = registry.get_mitigation_catalog()
for m in mitigations:
    print(f"{m['action_id']}: {m['name']} — {m['description']}")

# Get expected mitigation per variant
for vid in ["ATO-V1", "ATO-V2", "ATO-V3", "ATO-V4", "ATO-V5"]:
    v = registry.get_variant("ATO-001", vid)
    print(f"{vid}: expected action = {v.expected_mitigation}")
```

---

## 🛠️ How to Build Your Response Engine

### Step 1: Create Your Folder

```
response/
├── __init__.py
└── engine.py
```

### Step 2: Build the Response Engine

```python
# response/engine.py
"""
Automated Response & Mitigation Engine.
Receives risk scores from Person 3 and executes bank actions.
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from identify import AttackRegistry


class ResponseEngine:
    """Automated bank response engine based on Person 1's mitigation rules."""

    def __init__(self):
        # Load the official mitigation catalog from Person 1
        self.registry = AttackRegistry().load()
        self.mitigations = self.registry.get_mitigation_catalog()
        self.action_log = []  # Audit trail

        # Thresholds from Person 1's ground truth
        self.thresholds = {
            "block":    0.80,  # Risk >= 80% → Block account
            "hold":     0.60,  # Risk 60-79% → Hold transaction
            "step_up":  0.40,  # Risk 40-59% → Request OTP / biometric
            "review":   0.20,  # Risk 20-39% → Flag for analyst
            "approve":  0.00,  # Risk < 20%  → Allow
        }

    def decide_action(self, risk_score, variant_id=None):
        """
        Decide what action the bank should take.

        Args:
            risk_score: float between 0.0 and 1.0
            variant_id: optional string like "ATO-V1" for context

        Returns:
            dict with action details
        """
        if risk_score >= self.thresholds["block"]:
            action = "BLOCK"
            severity = 4
            message = "CRITICAL: Account frozen. All transactions blocked."
            notify = ["fraud_team", "cardholder", "compliance"]
        elif risk_score >= self.thresholds["hold"]:
            action = "HOLD"
            severity = 3
            message = "HIGH: Transaction held. Cardholder notification sent."
            notify = ["cardholder", "fraud_team"]
        elif risk_score >= self.thresholds["step_up"]:
            action = "STEP_UP_AUTH"
            severity = 2
            message = "MEDIUM: Additional verification required (OTP sent)."
            notify = ["cardholder"]
        elif risk_score >= self.thresholds["review"]:
            action = "REVIEW"
            severity = 1
            message = "LOW: Flagged for manual analyst review."
            notify = ["fraud_analyst"]
        else:
            action = "APPROVE"
            severity = 0
            message = "CLEAR: Transaction approved. No anomalies detected."
            notify = []

        result = {
            "action": action,
            "severity": severity,
            "risk_score": round(risk_score, 4),
            "risk_percent": f"{risk_score * 100:.1f}%",
            "message": message,
            "notify": notify,
            "variant_context": variant_id,
            "timestamp": datetime.now().isoformat(),
        }

        # Log for audit trail
        self.action_log.append(result)
        return result

    def execute_action(self, transaction_id, risk_score, variant_id=None):
        """
        Full execution: decide + log + print.

        Args:
            transaction_id: unique transaction identifier
            risk_score: float 0.0 to 1.0
            variant_id: optional ATO variant context
        """
        decision = self.decide_action(risk_score, variant_id)

        # Simulate execution
        action_icons = {
            "BLOCK": "🛑",
            "HOLD": "⚠️",
            "STEP_UP_AUTH": "🔐",
            "REVIEW": "📋",
            "APPROVE": "✅"
        }
        icon = action_icons.get(decision["action"], "❓")

        print(f"  TXN {transaction_id} | Risk: {decision['risk_percent']:>6s} | "
              f"{icon} {decision['action']} | {decision['message']}")

        return decision

    def validate_against_ground_truth(self):
        """
        Verify our thresholds match Person 1's expected mitigations.
        """
        print("\\nValidating response rules against Ground Truth...")

        test_cases = {
            "ATO-V1": 0.95,   # Expected: BLOCK
            "ATO-V2": 0.70,   # Expected: HOLD
            "ATO-V3": 0.50,   # Expected: STEP_UP_AUTH
            "ATO-V4": 0.30,   # Expected: REVIEW
            "ATO-V5": 0.50,   # Expected: STEP_UP_AUTH
        }

        expected_actions = {
            "ATO-V1": "block",
            "ATO-V2": "hold",
            "ATO-V3": "step_up_authentication",
            "ATO-V4": "review",
            "ATO-V5": "step_up_authentication",
        }

        all_pass = True
        for vid, score in test_cases.items():
            decision = self.decide_action(score, vid)
            expected = expected_actions[vid]
            actual = decision["action"].lower().replace("step_up_auth", "step_up_authentication")

            match = "✅" if expected in actual or actual in expected else "❌"
            if match == "❌":
                all_pass = False
            print(f"  {vid}: score={score:.2f} → {decision['action']} "
                  f"(expected: {expected}) {match}")

        return all_pass

    def get_audit_log(self):
        """Return the full audit trail of all decisions made."""
        return self.action_log


# Self-test
if __name__ == "__main__":
    print("=" * 60)
    print("  🛑 RESPONSE ENGINE SELF-TEST")
    print("=" * 60)

    engine = ResponseEngine()

    # Test with sample transactions
    test_transactions = [
        (1001, 0.92, "ATO-V1"),
        (1002, 0.71, "ATO-V2"),
        (1003, 0.48, "ATO-V3"),
        (1004, 0.25, "ATO-V4"),
        (1005, 0.52, "ATO-V5"),
        (1006, 0.08, None),
    ]

    print("\\nProcessing transactions:")
    for txn_id, score, variant in test_transactions:
        engine.execute_action(txn_id, score, variant)

    # Validate against Person 1's ground truth
    print()
    engine.validate_against_ground_truth()

    print(f"\\nAudit log entries: {len(engine.get_audit_log())}")
    print("=" * 60)
```

### Step 3: Connect with Person 3

Person 3 will call your engine like this:
```python
from response.engine import ResponseEngine

engine = ResponseEngine()

# Person 3's scanner produces results:
scan_result = scanner.scan_signals([0.95, 0.85, 0.90, 0.40, 0.20, 0.90])

# Pass to Person 4's response engine:
engine.execute_action(
    transaction_id="TXN-90001",
    risk_score=scan_result["risk_score"],
    variant_id=scan_result["variant"]
)
```

---

## ✅ Verification

Run your self-test:
```bash
python -m response.engine
```

You should see all 5 variants triggering the correct response actions.
