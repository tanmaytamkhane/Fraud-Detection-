"""
engine.py — Automated Response & Mitigation Engine
====================================================
Person 4's core module.

WHAT THIS FILE DOES:
    Receives a risk score (0.0 to 1.0) from Person 3's detection engine
    and decides what action the bank should take:

    Risk >= 80%  → 🛑 BLOCK           (Freeze account immediately)
    Risk 60-79%  → ⚠️  HOLD            (Hold transaction, notify cardholder)
    Risk 40-59%  → 🔐 STEP_UP_AUTH    (Request OTP / biometric)
    Risk 20-39%  → 📋 REVIEW          (Flag for human fraud analyst)
    Risk < 20%   → ✅ APPROVE         (Allow transaction)

HOW TO USE:
    from response.engine import ResponseEngine

    engine = ResponseEngine()

    # Single transaction decision
    decision = engine.execute_action(
        transaction_id="TXN-90001",
        risk_score=0.85,
        variant_id="ATO-V1"
    )
    print(decision["action"])   # "BLOCK"
    print(decision["message"])  # "CRITICAL: Account frozen..."

    # Get full audit trail
    log = engine.get_audit_log()

INTEGRATION WITH PERSON 3:
    from response.engine import ResponseEngine

    engine = ResponseEngine()
    scan_result = scanner.scan_signals([0.95, 0.85, 0.90, 0.40, 0.20, 0.90])
    engine.execute_action(
        transaction_id="TXN-90001",
        risk_score=scan_result["risk_score"],
        variant_id=scan_result.get("variant")
    )
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Any

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from identify import AttackRegistry
from response.graph_engine import NetworkRiskGraph
from response.llm_summarizer import generate_case_summary


# =============================================================================
# RESPONSE ACTION DEFINITIONS
# =============================================================================

# Action metadata aligned with Person 1's mitigation catalog (taxonomy.json)
ACTION_CATALOG = {
    "BLOCK": {
        "action_id": "block",
        "mitigation_id": "MIT-004",
        "name": "Account Block",
        "severity": 4,
        "severity_label": "critical",
        "icon": "🛑",
        "message": "CRITICAL: Account frozen. All transactions blocked immediately.",
        "notify": ["fraud_team", "cardholder", "compliance"],
        "customer_friction": "very_high",
        "response_time": "real-time",
    },
    "HOLD": {
        "action_id": "hold",
        "mitigation_id": "MIT-003",
        "name": "Transaction Hold",
        "severity": 3,
        "severity_label": "high",
        "icon": "⚠️",
        "message": "HIGH RISK: Transaction held. Cardholder notified via SMS/push.",
        "notify": ["cardholder", "fraud_team"],
        "customer_friction": "high",
        "response_time": "near-real-time",
    },
    "STEP_UP_AUTH": {
        "action_id": "step_up_authentication",
        "mitigation_id": "MIT-001",
        "name": "Step-Up Authentication",
        "severity": 2,
        "severity_label": "medium",
        "icon": "🔐",
        "message": "MEDIUM RISK: Additional verification required. OTP sent to registered device.",
        "notify": ["cardholder"],
        "customer_friction": "medium",
        "response_time": "within-minutes",
    },
    "REVIEW": {
        "action_id": "review",
        "mitigation_id": "MIT-002",
        "name": "Analyst Review",
        "severity": 1,
        "severity_label": "low",
        "icon": "📋",
        "message": "LOW RISK: Flagged for manual review by fraud analyst.",
        "notify": ["fraud_analyst"],
        "customer_friction": "low",
        "response_time": "within-hours",
    },
    "APPROVE": {
        "action_id": "approve",
        "mitigation_id": None,
        "name": "Approve",
        "severity": 0,
        "severity_label": "clear",
        "icon": "✅",
        "message": "CLEAR: Transaction approved. No anomalies detected.",
        "notify": [],
        "customer_friction": "none",
        "response_time": "instant",
    },
}


class ResponseEngine:
    """
    Automated bank response engine based on Person 1's mitigation rules.

    Takes a risk score (0.0-1.0) from Person 3's detection engine and
    maps it to one of 5 bank actions defined in the Ground Truth.

    Attributes:
        registry:    AttackRegistry loaded from Person 1's ground truth
        mitigations: Official mitigation catalog from taxonomy.json
        thresholds:  Risk score boundaries for each action tier
        action_log:  Audit trail of all decisions made
        stats:       Running statistics (counts per action, total processed)
    """

    def __init__(self, escalation_weight: float = 0.35):
        """Initialize the Response Engine with Person 1's ground truth rules and NetworkRiskGraph."""
        # Load the official mitigation catalog from Person 1
        self.registry = AttackRegistry().load()
        self.mitigations = self.registry.get_mitigation_catalog()

        # Audit trail — every decision is logged
        self.action_log: list[dict] = []

        # Graph-based network risk engine
        self.graph = NetworkRiskGraph()
        self.escalation_weight = escalation_weight

        # Running statistics
        self.stats = {
            "total_processed": 0,
            "action_counts": {
                "BLOCK": 0,
                "HOLD": 0,
                "STEP_UP_AUTH": 0,
                "REVIEW": 0,
                "APPROVE": 0,
            },
            "avg_risk_score": 0.0,
            "highest_risk_seen": 0.0,
        }

        # Thresholds from Person 1's ground truth
        # These map directly to the mitigation_catalog in taxonomy.json
        self.thresholds = {
            "block":    0.81,   # Risk > 80% → Block account (0.81 so ATO-V2 at 0.80 → HOLD per P1)
            "hold":     0.60,   # Risk 60-80% → Hold transaction
            "step_up":  0.40,   # Risk 40-59% → Request OTP / biometric
            "review":   0.20,   # Risk 20-39% → Flag for analyst
            "approve":  0.00,   # Risk < 20%  → Allow
        }

    # =========================================================================
    # CORE DECISION LOGIC
    # =========================================================================

    def decide_action(
        self,
        risk_score: float,
        variant_id: Optional[str] = None,
        network_risk: float = 0.0,
    ) -> dict:
        """
        Decide what action the bank should take based on the risk score and optional network risk.

        This is the core decision function. It maps a risk score to one of
        5 pre-defined actions using Person 1's threshold rules.

        If network_risk > 0, it escalates the effective risk score:
            effective_risk = min(1.0, max(risk_score, risk_score + network_risk * escalation_weight))

        Args:
            risk_score: Float between 0.0 and 1.0 from Person 3's detector.
            variant_id: Optional variant context (e.g., "ATO-V1") for logging.
            network_risk: Optional float between 0.0 and 1.0 from NetworkRiskGraph.

        Returns:
            Dictionary containing the full decision details.
        """
        # Clamp inputs to valid ranges
        risk_score = max(0.0, min(1.0, float(risk_score)))
        network_risk = max(0.0, min(1.0, float(network_risk)))

        # Blend network risk (escalate only, never de-escalate)
        if network_risk > 0.0:
            effective_risk = min(1.0, max(risk_score, risk_score + network_risk * self.escalation_weight))
        else:
            effective_risk = risk_score

        # Determine action based on thresholds applied to effective_risk
        if effective_risk >= self.thresholds["block"]:
            action_key = "BLOCK"
        elif effective_risk >= self.thresholds["hold"]:
            action_key = "HOLD"
        elif effective_risk >= self.thresholds["step_up"]:
            action_key = "STEP_UP_AUTH"
        elif effective_risk >= self.thresholds["review"]:
            action_key = "REVIEW"
        else:
            action_key = "APPROVE"

        # Build the full decision record
        action_meta = ACTION_CATALOG[action_key]
        result = {
            "action": action_key,
            "action_id": action_meta["action_id"],
            "mitigation_id": action_meta["mitigation_id"],
            "name": action_meta["name"],
            "severity": action_meta["severity"],
            "severity_label": action_meta["severity_label"],
            "risk_score": round(risk_score, 4),
            "risk_percent": f"{risk_score * 100:.1f}%",
            "network_risk": round(network_risk, 4),
            "effective_risk": round(effective_risk, 4),
            "message": action_meta["message"],
            "icon": action_meta["icon"],
            "notify": action_meta["notify"],
            "customer_friction": action_meta["customer_friction"],
            "response_time": action_meta["response_time"],
            "variant_context": variant_id,
            "timestamp": datetime.now().isoformat(),
        }

        # Log for audit trail
        self.action_log.append(result)

        # Update running stats
        self.stats["total_processed"] += 1
        self.stats["action_counts"][action_key] += 1
        self.stats["highest_risk_seen"] = max(self.stats["highest_risk_seen"], effective_risk)
        # Incremental average
        n = self.stats["total_processed"]
        self.stats["avg_risk_score"] = (
            self.stats["avg_risk_score"] * (n - 1) + effective_risk
        ) / n

        return result

    # =========================================================================
    # EXECUTION — Full pipeline: decide + log + print
    # =========================================================================

    def execute_action(
        self,
        transaction_id: str,
        risk_score: float,
        variant_id: Optional[str] = None,
        silent: bool = False,
        network_risk: Optional[float] = None,
        card1: Optional[Any] = None,
        device_id: Optional[Any] = None,
        addr1: Optional[Any] = None,
        explanation_text: Optional[str] = None,
    ) -> dict:
        """
        Full execution pipeline: decide action + log + print formatted output.

        This is the main method that Person 3 (or the API) calls.

        Args:
            transaction_id: Unique transaction identifier (e.g., "TXN-90001").
            risk_score:     Float 0.0 to 1.0 from the detection engine.
            variant_id:     Optional ATO variant context for logging.
            silent:         If True, suppress console output.
            network_risk:   Optional explicit network risk override (0.0 to 1.0).
            card1:          Optional account identifier for graph update/lookup.
            device_id:      Optional device identifier for graph update/lookup.
            addr1:          Optional location identifier for graph update/lookup.
            explanation_text: Optional human explanation for LLM analyst summary.

        Returns:
            The full decision dictionary (same as decide_action).
        """
        # 1. Compute network risk from graph if entity identifiers provided and network_risk not explicit
        if network_risk is None:
            if card1 is not None or device_id is not None or addr1 is not None:
                calc_net_risk = self.graph.get_network_risk(card1=card1, device_id=device_id, addr1=addr1)
            else:
                calc_net_risk = 0.0
        else:
            calc_net_risk = float(network_risk)

        decision = self.decide_action(risk_score, variant_id, network_risk=calc_net_risk)

        # Add the transaction ID to the decision record
        decision["transaction_id"] = transaction_id

        # 2. Update graph if entity identifiers provided
        if card1 is not None or device_id is not None or addr1 is not None:
            self.graph.add_transaction(
                transaction_id=transaction_id,
                card1=card1,
                device_id=device_id,
                addr1=addr1,
                decision_action=decision["action"],
            )

        # 3. Generate LLM case summary if explanation_text provided and action is actionable
        if explanation_text is not None and decision["action"] != "APPROVE":
            decision["analyst_summary"] = generate_case_summary(
                decision=decision,
                explanation_text=explanation_text,
                variant_name=variant_id,
            )

        if not silent:
            icon = decision["icon"]
            net_str = f" [NetRisk: {decision['network_risk']:.2f}]" if decision.get("network_risk", 0) > 0 else ""
            print(
                f"  TXN {transaction_id} | "
                f"Risk: {decision['risk_percent']:>6s}{net_str} | "
                f"{icon} {decision['action']:<13s} | "
                f"{decision['message']}"
            )

        return decision

    def process_batch(self, transactions: list[dict], silent: bool = False) -> list[dict]:
        """
        Process a batch of transactions.

        Args:
            transactions: List of dicts, each with keys:
                          "transaction_id", "risk_score", and optionally "variant_id",
                          "network_risk", "card1", "device_id", "addr1", "explanation_text"
            silent:       If True, suppress per-transaction console output.

        Returns:
            List of decision dictionaries.
        """
        if not silent:
            print(f"\n  Processing batch of {len(transactions)} transactions...")
            print(f"  {'─' * 70}")

        results = []
        for txn in transactions:
            result = self.execute_action(
                transaction_id=txn["transaction_id"],
                risk_score=txn["risk_score"],
                variant_id=txn.get("variant_id"),
                silent=silent,
                network_risk=txn.get("network_risk"),
                card1=txn.get("card1"),
                device_id=txn.get("device_id") or txn.get("DeviceInfo"),
                addr1=txn.get("addr1"),
                explanation_text=txn.get("explanation_text") or txn.get("explanation"),
            )
            results.append(result)

        if not silent:
            print(f"  {'─' * 70}")
            self.print_batch_summary()

        return results

    # =========================================================================
    # VALIDATION — Verify rules match Person 1's ground truth
    # =========================================================================

    def validate_against_ground_truth(self) -> bool:
        """
        Verify that our threshold rules produce the correct action for
        each of the 5 ATO variants defined by Person 1.

        Uses the risk_score from attacks.json for each variant and checks
        that our engine maps it to the expected_mitigation.

        Returns:
            True if all variants trigger the correct action, False otherwise.
        """
        print("\n  Validating response rules against Person 1's Ground Truth...")
        print(f"  {'─' * 60}")

        # Map our action names to Person 1's mitigation names
        action_to_mitigation = {
            "BLOCK": "block",
            "HOLD": "hold",
            "STEP_UP_AUTH": "step_up_authentication",
            "REVIEW": "review",
            "APPROVE": "approve",
        }

        all_pass = True
        variant_ids = ["ATO-V1", "ATO-V2", "ATO-V3", "ATO-V4", "ATO-V5"]

        for vid in variant_ids:
            variant = self.registry.get_variant("ATO-001", vid)
            if variant is None:
                print(f"  ❌ {vid}: variant not found in registry!")
                all_pass = False
                continue

            # Use the official risk_score from Person 1's ground truth
            risk_score = variant.risk_score
            expected = variant.expected_mitigation

            # Run our decision engine
            decision = self.decide_action(risk_score, vid)
            actual = action_to_mitigation.get(decision["action"], decision["action"].lower())

            # Check match
            match = (expected == actual)
            icon = "✅" if match else "❌"

            if not match:
                all_pass = False

            print(
                f"  {icon} {vid}: risk={risk_score:.2f} → "
                f"{decision['action']:<13s} "
                f"(expected: {expected}, got: {actual})"
            )

        print(f"  {'─' * 60}")
        if all_pass:
            print("  ✅ ALL VARIANTS PASS — Response engine matches Ground Truth!\n")
        else:
            print("  ❌ SOME VARIANTS FAILED — Check thresholds!\n")

        return all_pass

    # =========================================================================
    # AUDIT & REPORTING
    # =========================================================================

    def get_audit_log(self) -> list[dict]:
        """Return the full audit trail of all decisions made."""
        return self.action_log

    def get_stats(self) -> dict:
        """Return running statistics."""
        return self.stats

    def print_batch_summary(self):
        """Print a summary of actions taken so far."""
        stats = self.stats
        total = stats["total_processed"]

        if total == 0:
            print("  No transactions processed yet.")
            return

        print(f"\n  📊 BATCH SUMMARY ({total} transactions)")
        print(f"  {'─' * 40}")

        for action, count in stats["action_counts"].items():
            if count > 0:
                pct = (count / total) * 100
                icon = ACTION_CATALOG[action]["icon"]
                bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                print(f"  {icon} {action:<13s} {count:>4d}  ({pct:5.1f}%)  {bar}")

        print(f"  {'─' * 40}")
        print(f"  Avg risk score:     {stats['avg_risk_score']:.4f}")
        print(f"  Highest risk seen:  {stats['highest_risk_seen']:.4f}")

    def export_audit_log(self, filepath: Optional[str] = None) -> str:
        """
        Export the audit log to a JSON file for compliance/review.

        Args:
            filepath: Output path. Defaults to response/audit_log.json.

        Returns:
            The path the log was written to.
        """
        if filepath is None:
            filepath = str(Path(__file__).parent / "audit_log.json")

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "engine_version": "1.0.0",
            "total_decisions": len(self.action_log),
            "statistics": self.stats,
            "decisions": self.action_log,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"\n  📁 Audit log exported to: {filepath}")
        print(f"     Total decisions logged: {len(self.action_log)}")
        return filepath

    def clear_log(self):
        """Reset the audit log and statistics (for testing)."""
        self.action_log = []
        self.stats = {
            "total_processed": 0,
            "action_counts": {k: 0 for k in self.stats["action_counts"]},
            "avg_risk_score": 0.0,
            "highest_risk_seen": 0.0,
        }


# =============================================================================
# SELF-TEST — Run this file directly to verify everything works
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  🛑 RESPONSE & MITIGATION ENGINE — SELF-TEST")
    print("  Person 4 | Mastercard Hackathon")
    print("=" * 70)

    engine = ResponseEngine()

    # ─── Test 1: Individual transaction decisions ────────────────────────
    print("\n  📋 TEST 1: Processing individual transactions\n")

    test_transactions = [
        ("TXN-1001", 0.92, "ATO-V1"),   # Should → BLOCK
        ("TXN-1002", 0.71, "ATO-V2"),   # Should → HOLD
        ("TXN-1003", 0.48, "ATO-V3"),   # Should → STEP_UP_AUTH
        ("TXN-1004", 0.25, "ATO-V4"),   # Should → REVIEW
        ("TXN-1005", 0.52, "ATO-V5"),   # Should → STEP_UP_AUTH
        ("TXN-1006", 0.08, None),       # Should → APPROVE
    ]

    for txn_id, score, variant in test_transactions:
        engine.execute_action(txn_id, score, variant)

    # ─── Test 2: Batch processing ────────────────────────────────────────
    engine.clear_log()
    print("\n\n  📋 TEST 2: Batch processing")

    batch = [
        {"transaction_id": "BATCH-001", "risk_score": 0.95, "variant_id": "ATO-V1"},
        {"transaction_id": "BATCH-002", "risk_score": 0.65, "variant_id": "ATO-V2"},
        {"transaction_id": "BATCH-003", "risk_score": 0.55, "variant_id": "ATO-V3"},
        {"transaction_id": "BATCH-004", "risk_score": 0.30, "variant_id": "ATO-V4"},
        {"transaction_id": "BATCH-005", "risk_score": 0.45, "variant_id": "ATO-V5"},
        {"transaction_id": "BATCH-006", "risk_score": 0.12, "variant_id": None},
        {"transaction_id": "BATCH-007", "risk_score": 0.05, "variant_id": None},
        {"transaction_id": "BATCH-008", "risk_score": 0.88, "variant_id": "ATO-V1"},
    ]

    engine.process_batch(batch)

    # ─── Test 3: Ground truth validation ─────────────────────────────────
    engine.clear_log()
    print("\n  📋 TEST 3: Ground Truth Validation")
    all_pass = engine.validate_against_ground_truth()

    # ─── Test 4: Audit log export ────────────────────────────────────────
    print("  📋 TEST 4: Audit Log Export")
    engine.export_audit_log()

    # ─── Final result ────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    if all_pass:
        print("  ✅ ALL SELF-TESTS PASSED — Response Engine is ready!")
    else:
        print("  ❌ SOME TESTS FAILED — Review thresholds!")
    print("=" * 70 + "\n")
