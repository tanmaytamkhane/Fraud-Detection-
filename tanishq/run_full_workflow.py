"""
run_full_workflow.py — End-to-End Attack → Detect → Respond Demo
=================================================================
This single script ties together ALL 4 team members' work:

  Person 1 (Yash)   → identify/     : Attack Ground Truth & Contract
  Person 2 (Abdulla)→ simulate/      : Attack Simulation Engine
  Person 3 (Tanishq)→ defend/        : Real-time Detection (UnifiedScanner)
  Person 4 (Shreya) → response/      : Automated Bank Response Engine

HOW TO RUN:
    python -X utf8 run_full_workflow.py

    Or to run a specific attack variant:
    python -X utf8 run_full_workflow.py --variant ATO-V1

WHAT HAPPENS:
    1. Load Person 1's attack contract & variant definitions
    2. Show the simulated attack signals (Person 2 output)
    3. Run detection through Person 3's defend engine
    4. Get the final bank response from Person 4's engine
    5. Print a full end-to-end summary
"""

import sys
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime

# ── Ensure project root is in path ──────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))


# ============================================================================
#  STEP 0: Colour helpers (works on all terminals)
# ============================================================================

def _c(text, code):
    """Wrap text in ANSI colour code (safe fallback for Windows)."""
    try:
        return f"\033[{code}m{text}\033[0m"
    except Exception:
        return text

def red(t):    return _c(t, "91")
def yellow(t): return _c(t, "93")
def green(t):  return _c(t, "92")
def cyan(t):   return _c(t, "96")
def bold(t):   return _c(t, "1")
def dim(t):    return _c(t, "2")


# ============================================================================
#  Attack preset signals  (what Person 2's simulator produces)
# ============================================================================

# Each preset maps to the 6 normalized signals:
# [device_risk, address_mismatch, amount_deviation, velocity, time_anomaly, channel_risk]
ATTACK_PRESETS = {
    "ATO-V1": {
        "signals": [0.95, 0.85, 0.90, 0.40, 0.20, 0.90],
        "label": "High-Value New Device Takeover (Loud)",
        "difficulty": "Easy",
        "color": red,
    },
    "ATO-V2": {
        "signals": [0.20, 0.30, 0.40, 0.95, 0.20, 0.75],
        "label": "Velocity Burst from Known Device",
        "difficulty": "Moderate",
        "color": red,
    },
    "ATO-V3": {
        "signals": [0.20, 0.80, 0.10, 0.10, 0.90, 0.30],
        "label": "Off-Hours Location Shift",
        "difficulty": "Moderate",
        "color": yellow,
    },
    "ATO-V4": {
        "signals": [0.20, 0.10, 0.25, 0.10, 0.10, 0.20],
        "label": "Subtle Amount Deviation — The Ghost",
        "difficulty": "Very Hard",
        "color": yellow,
    },
    "ATO-V5": {
        "signals": [0.35, 0.45, 0.25, 0.40, 0.60, 0.40],
        "label": "Multi-Signal Low-Intensity — The Chameleon",
        "difficulty": "Hard",
        "color": yellow,
    },
    "LEGIT": {
        "signals": [0.15, 0.05, 0.10, 0.10, 0.15, 0.15],
        "label": "Legitimate Transaction (Control)",
        "difficulty": "N/A",
        "color": green,
    },
}

SIGNAL_NAMES = [
    "device_risk",
    "address_mismatch",
    "amount_deviation",
    "velocity",
    "time_anomaly",
    "channel_risk",
]

ACTION_COLORS = {
    "BLOCK":        red,
    "HOLD":         yellow,
    "STEP_UP_AUTH": yellow,
    "REVIEW":       cyan,
    "APPROVE":      green,
}

ACTION_ICONS = {
    "BLOCK":        "BLOCK",
    "HOLD":         "HOLD",
    "STEP_UP_AUTH": "STEP-UP AUTH",
    "REVIEW":       "REVIEW",
    "APPROVE":      "APPROVE",
}


# ============================================================================
#  STEP 1: Load Person 1 — Attack Ground Truth
# ============================================================================

def load_person1_contract(variant_id: str):
    print(bold("\n" + "=" * 68))
    print(bold("  STEP 1 — PERSON 1 (YASH): ATTACK INTELLIGENCE & GROUND TRUTH"))
    print(bold("=" * 68))

    from identify.registry import AttackRegistry

    registry = AttackRegistry().load()
    contract = registry.get_attack_contract("ATO-001")

    print(f"  Attack ID   : {contract['attack_id']}")
    print(f"  Attack Name : {contract.get('name', contract.get('attack_name', 'N/A'))}")
    print(f"  Signals     : {len(contract.get('signals', []))} defined signals")
    print(f"  Variants    : {len(registry.list_variants('ATO-001'))} behavioral variants")
    print(f"  Mitigations : {len(contract.get('mitigations', []))} mitigation actions")

    if variant_id != "LEGIT":
        variant = registry.get_variant("ATO-001", variant_id)
        if variant:
            print(f"\n  [Target Variant] {variant_id}: {variant.name}")
            print(f"   Risk Level   : {variant.risk_level}")
            print(f"   Difficulty   : {variant.detection_difficulty}")
            print(f"   Expected Resp: {variant.expected_mitigation}")
            print(f"   Sim Config   : {variant.simulation_config}")
    else:
        print("\n  [Target] LEGIT — Normal transaction (no attack)")

    print(f"\n  {green('Person 1 [OK] — Ground truth loaded successfully')}")
    return registry


# ============================================================================
#  STEP 2: Person 2 — Simulation (show what the attack looks like as signals)
# ============================================================================

def show_person2_simulation(variant_id: str, preset: dict):
    print(bold("\n" + "=" * 68))
    print(bold("  STEP 2 — PERSON 2 (ABDULLA): ATTACK SIMULATION"))
    print(bold("=" * 68))

    color_fn = preset["color"]
    signals = preset["signals"]

    print(f"  Simulating variant : {color_fn(variant_id)}")
    print(f"  Attack description : {preset['label']}")
    print(f"  Detection difficulty: {preset['difficulty']}")
    print()
    print(f"  {'Signal':<22}  {'Value':>6}  {'Bar'}")
    print(f"  {'-'*22}  {'-'*6}  {'-'*30}")

    for name, value in zip(SIGNAL_NAMES, signals):
        bar_len = int(value * 30)
        bar = "#" * bar_len + "." * (30 - bar_len)
        flag = red(" ◄ HIGH") if value >= 0.7 else (yellow(" ◄ MED") if value >= 0.4 else "")
        print(f"  {name:<22}  {value:>6.2f}  [{bar}]{flag}")

    print(f"\n  {green('Person 2 [OK] — Attack signal vector generated')}")
    return signals


# ============================================================================
#  STEP 3: Person 3 — Detection Engine (defend/)
# ============================================================================

def run_person3_detection(signals: list, transaction_id: str, quiet: bool = False):
    if not quiet:
        print(bold("\n" + "=" * 68))
        print(bold("  STEP 3 — PERSON 3 (TANISHQ): REAL-TIME DETECTION ENGINE"))
        print(bold("=" * 68))

    try:
        from defend.scanner import UnifiedScanner

        scanner = UnifiedScanner(auto_load_registry=True)
        print("  Running multi-engine detection:")
        print("    BehaviourEngine     → behavioural scoring")
        print("    XGBoostBaseline     → ML probability (fallback to behaviour if untrained)")
        print("    AnomalyDetector     → isolation forest (fallback if untrained)")
        print("    RiskEngine          → weighted fusion (40% XGB + 30% Behaviour + 30% Anomaly)")
        print()

        result = scanner.scan_signals(signals, transaction_id=transaction_id)

        sub = result.get("sub_scores", {})
        print(f"  Sub-scores:")
        print(f"    Behaviour Score  : {sub.get('behaviour_score', 'N/A'):.4f}")
        print(f"    XGB Probability  : {sub.get('xgb_probability', 'N/A'):.4f}")
        print(f"    Anomaly Score    : {sub.get('anomaly_score', 'N/A'):.4f}")
        print()

        risk_score = result["risk_score"]
        risk_level = result["risk_level"]
        matched_variant = result.get("matched_variant", "UNKNOWN")
        variant_name = result.get("variant_name", "")

        risk_color = red if risk_score >= 0.60 else (yellow if risk_score >= 0.30 else green)
        print(f"  {bold('Fused Risk Score')}    : {risk_color(f'{risk_score:.4f} ({risk_score * 100:.1f}%)')}")
        print(f"  {bold('Risk Level')}         : {risk_color(risk_level)}")
        print(f"  {bold('Matched ATO Variant')}: {matched_variant} — {variant_name}")

        if result.get("explanation"):
            print(f"\n  Explanation: {dim(result['explanation'][:200])}")

        print(f"\n  {green('Person 3 [OK] — Detection complete')}")
        return result

    except ImportError as e:
        print(f"  {yellow('[FALLBACK]')} defend/ module not found, using HDC engine directly.")
        print(f"  Import error: {e}")
        return _fallback_hdc_detection(signals, transaction_id)


def _fallback_hdc_detection(signals: list, transaction_id: str):
    """Fallback: use HDC engine (Person 1's hdc/) if defend/ isn't available."""
    from hdc.encoder import HDCEncoder
    from hdc.model import HDCClassifier
    from hdc.trainer import HDCTrainer
    from pipeline.variant_labeler import label_variants, VARIANT_NAMES

    from pipeline.variant_labeler import VARIANT_PROTOTYPES

    encoder = HDCEncoder(dim=10000)
    classifier = HDCClassifier(dim=10000)

    legit_samples = np.random.RandomState(42).uniform(0.05, 0.30, (200, 6)).astype(np.float32)
    fraud_samples = np.array([
        VARIANT_PROTOTYPES["ATO-V1"], VARIANT_PROTOTYPES["ATO-V2"],
        VARIANT_PROTOTYPES["ATO-V3"], VARIANT_PROTOTYPES["ATO-V4"],
        VARIANT_PROTOTYPES["ATO-V5"],
    ] * 40, dtype=np.float32)
    fraud_samples = np.clip(
        fraud_samples + np.random.RandomState(42).normal(0, 0.05, fraud_samples.shape).astype(np.float32), 0, 1
    )
    X_train = np.vstack([legit_samples, fraud_samples])
    y_train = np.array([0] * 200 + [1] * 200, dtype=np.int32)

    trainer = HDCTrainer(encoder=encoder, classifier=classifier)
    trainer.train(X_train, y_train, retrain_epochs=15)

    sig_arr = np.array(signals, dtype=np.float32).reshape(1, -1)
    hv = encoder.encode_batch(sig_arr)
    pred, _ = classifier.predict_batch(hv)
    risk_score = float(classifier.get_fraud_score(hv)[0])
    variant = str(label_variants(sig_arr)[0])

    import importlib.util, importlib
    # Import risk_engine directly to avoid defend/__init__.py triggering sklearn import
    spec = importlib.util.spec_from_file_location(
        "defend.risk_engine",
        str(Path(__file__).parent / "defend" / "risk_engine.py")
    )
    re_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(re_mod)
    RiskEngine = re_mod.RiskEngine
    re = RiskEngine()
    decision = re.decision(risk_score)
    risk_level = re.risk_level(risk_score)

    print(f"  {bold('HDC Risk Score')}   : {risk_score:.4f} ({risk_score * 100:.1f}%)")
    print(f"  {bold('HDC Risk Level')}   : {risk_level}")
    print(f"  {bold('Matched Variant')} : {variant} — {VARIANT_NAMES.get(variant, 'N/A')}")
    print(f"\n  {green('Person 3 [OK] — HDC detection complete (fallback mode)')}")

    return {
        "transaction_id": transaction_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "decision": decision,
        "action": decision,
        "matched_variant": variant,
        "variant": variant,
        "variant_name": VARIANT_NAMES.get(variant, ""),
        "sub_scores": {
            "behaviour_score": risk_score,
            "xgb_probability": risk_score,
            "anomaly_score": risk_score,
        },
    }


# ============================================================================
#  STEP 4: Person 4 — Response Engine (response/)
# ============================================================================

def run_person4_response(scan_result: dict, transaction_id: str):
    print(bold("\n" + "=" * 68))
    print(bold("  STEP 4 — PERSON 4 (SHREYA): AUTOMATED BANK RESPONSE ENGINE"))
    print(bold("=" * 68))

    risk_score = scan_result["risk_score"]
    variant_id = scan_result.get("matched_variant") or scan_result.get("variant")

    from response.engine import ResponseEngine

    engine = ResponseEngine()
    decision = engine.execute_action(
        transaction_id=transaction_id,
        risk_score=risk_score,
        variant_id=variant_id,
    )

    action = decision["action"]
    action_color = ACTION_COLORS.get(action, bold)
    action_label = ACTION_ICONS.get(action, action)

    print()
    print(f"  Risk Score   : {risk_score:.4f} ({risk_score * 100:.1f}%)")
    print(f"  Variant      : {variant_id}")
    print()
    print(f"  {bold('BANK DECISION')}  : {action_color(bold(f'[{action_label}]'))}")
    print(f"  Message      : {decision.get('message', decision.get('action_message', ''))}")
    print(f"  Notify       : {decision.get('notify', [])}")
    print(f"  Severity     : {decision.get('severity', 'N/A')} / 4")
    print(f"  Timestamp    : {decision.get('timestamp', datetime.now().isoformat())}")

    print(f"\n  {green('Person 4 [OK] — Bank response executed and logged')}")
    return decision


# ============================================================================
#  STEP 5: Final Summary
# ============================================================================

def print_final_summary(variant_id: str, preset: dict, signals: list,
                         scan_result: dict, decision: dict):
    action = decision["action"]
    risk_score = scan_result["risk_score"]
    action_color = ACTION_COLORS.get(action, bold)

    print(bold("\n" + "#" * 68))
    print(bold("  END-TO-END SUMMARY"))
    print(bold("#" * 68))
    print()
    print(f"  Transaction ID  : {scan_result['transaction_id']}")
    print(f"  Attack Variant  : {preset['color'](variant_id)} — {preset['label']}")
    print(f"  Input Signals   : {[round(s, 2) for s in signals]}")
    print()
    print(f"  Risk Score      : {risk_score:.4f}  ({risk_score * 100:.1f}%)")
    print(f"  Risk Level      : {scan_result.get('risk_level', 'N/A')}")
    print(f"  Matched Variant : {scan_result.get('matched_variant', 'N/A')}")
    print()
    print(f"  FINAL ACTION    : {action_color(bold(f'[ {ACTION_ICONS.get(action, action)} ]'))}")
    print(f"  Bank Message    : {decision.get('message', decision.get('action_message', ''))}")
    print()

    print("  Pipeline stages:")
    print(f"    [1] Person 1 (Yash)    → Ground truth & attack contract   [DONE]")
    print(f"    [2] Person 2 (Abdulla) → Attack simulation (6 signals)    [DONE]")
    print(f"    [3] Person 3 (Tanishq) → Multi-engine fraud detection     [DONE]")
    print(f"    [4] Person 4 (Shreya)  → Automated bank response          [DONE]")
    print(bold("#" * 68 + "\n"))


# ============================================================================
#  Run All Variants
# ============================================================================

def run_all_variants():
    print(bold("\n" + "=" * 68))
    print(bold("  BATCH RUN — All 6 Scenarios"))
    print(bold("=" * 68))

    from response.engine import ResponseEngine
    engine = ResponseEngine()

    print(f"\n  {'Variant':<10}  {'Description':<40}  {'Risk':>6}  {'Action'}")
    print(f"  {'-'*10}  {'-'*40}  {'-'*6}  {'-'*14}")

    for variant_id, preset in ATTACK_PRESETS.items():
        signals = preset["signals"]
        txn_id = f"TXN-{variant_id.replace('-', '')}"

        # Reuse the same detection logic (with graceful fallback), suppress verbose output
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            scan_result = run_person3_detection(signals, txn_id, quiet=True)
        decision = engine.decide_action(scan_result["risk_score"], variant_id)

        action = decision["action"]
        risk = scan_result["risk_score"]
        color_fn = preset["color"]
        action_color = ACTION_COLORS.get(action, lambda x: x)

        label = preset["label"][:38]
        print(f"  {color_fn(variant_id):<10}  {label:<40}  {risk:>6.2f}  {action_color(action)}")

    print()


# ============================================================================
#  Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Run the end-to-end fraud detection workflow"
    )
    parser.add_argument(
        "--variant",
        choices=list(ATTACK_PRESETS.keys()),
        default=None,
        help="Attack variant to simulate (default: run all)",
    )
    args = parser.parse_args()

    print(bold("\n" + "#" * 68))
    print(bold("  MASTERCARD HACKATHON — FULL WORKFLOW DEMO"))
    print(bold("  Person 1 → Person 2 → Person 3 → Person 4"))
    print(bold("#" * 68))

    if args.variant is None:
        # ── Run the complete batch (all variants) ──
        run_all_variants()
    else:
        # ── Single variant end-to-end ──
        variant_id = args.variant
        preset = ATTACK_PRESETS[variant_id]
        transaction_id = f"TXN-{variant_id.replace('-', '')}-{datetime.now().strftime('%H%M%S')}"

        # Step 1: Person 1
        registry = load_person1_contract(variant_id)

        # Step 2: Person 2
        signals = show_person2_simulation(variant_id, preset)

        # Step 3: Person 3
        scan_result = run_person3_detection(signals, transaction_id)

        # Step 4: Person 4
        decision = run_person4_response(scan_result, transaction_id)

        # Summary
        print_final_summary(variant_id, preset, signals, scan_result, decision)


if __name__ == "__main__":
    main()
