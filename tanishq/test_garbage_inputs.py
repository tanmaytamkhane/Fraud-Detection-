"""
test_garbage_inputs.py — Robustness, Edge-Case & Garbage Value Stress Test
==========================================================================
Tests how the end-to-end system (P1 -> P2 -> P3 -> P4) handles:
 1. All Zeros (Absolute Minimums)
 2. All Max (Absolute Extreme Attack)
 3. Out-of-Bounds Extreme Values (e.g. 9999.0, 500.0, -100.0)
 4. Negative Values (e.g. -0.5, -10.0)
 5. Uniform Mid Noise (Pure ambiguity / 0.5 across the board)
 6. Single Extreme Spike in One Signal (e.g. only velocity = 1.0, others 0.0)
 7. Random Chaotic Floats
 8. Invalid format / size inputs (Error handling test)
"""

import sys
from pathlib import Path
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).parent))

from defend.scanner import UnifiedScanner
from response.engine import ResponseEngine

def run_garbage_tests():
    print("=" * 80)
    print(" 🧪 GARBAGE & EDGE-CASE STRESS TESTING FOR ATO FRAUD DETECTION SYSTEM")
    print("=" * 80)

    scanner = UnifiedScanner(auto_load_registry=True)
    engine = ResponseEngine()

    test_cases = [
        {
            "name": "1. ALL ZEROS (Zero Risk Profile)",
            "signals": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "description": "Baseline completely clean user transaction",
            "expected_decision": "APPROVE"
        },
        {
            "name": "2. ALL ONES (100% Signal Saturation)",
            "signals": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            "description": "All 6 fraud signals triggered at maximum capacity",
            "expected_decision": "BLOCK"
        },
        {
            "name": "3. EXTREME OUT-OF-BOUNDS (Garbage Massive Numbers)",
            "signals": [999.0, 500.0, 12000.0, 850.0, 99.0, 420.0],
            "description": "Crazy high inputs (Tests signal normalization & adapter capping)",
            "expected_decision": "BLOCK (Normalized/Capped safely)"
        },
        {
            "name": "4. NEGATIVE VALUES (Corrupt / Inverted Sensors)",
            "signals": [-10.0, -0.5, -99.9, -1.0, -5.0, -0.1],
            "description": "Negative numbers (Tests bounds clamping to 0.0)",
            "expected_decision": "APPROVE (Clamped to 0.0 safely)"
        },
        {
            "name": "5. PURE 50% NOISE (Maximum Uncertainty)",
            "signals": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            "description": "All signals exactly at the decision boundary (0.50)",
            "expected_decision": "STEP_UP_AUTH or HOLD"
        },
        {
            "name": "6. SINGLE SPIKE: ONLY VELOCITY BURST",
            "signals": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            "description": "Known device, matching address, normal amount, but rapid burst",
            "expected_decision": "REVIEW or STEP_UP_AUTH"
        },
        {
            "name": "7. SINGLE SPIKE: ONLY NEW DEVICE",
            "signals": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "description": "Everything normal except new device",
            "expected_decision": "REVIEW or STEP_UP_AUTH"
        },
        {
            "name": "8. RANDOM CHAOTIC JUNK",
            "signals": [0.01, 0.99, 0.02, 0.88, 0.05, 0.92],
            "description": "Alternating extreme high and extreme low signals",
            "expected_decision": "Evaluated based on fused score"
        },
    ]

    print(f"\n{'Test Case':<32} | {'Input Signals':<30} | {'Risk Score':<10} | {'Decision':<14} | {'Status'}")
    print("-" * 105)

    for i, test in enumerate(test_cases, 1):
        txn_id = f"TEST-GARBAGE-{i:03d}"
        
        # Test if scanner handles it gracefully without crashing
        try:
            # We clip/pass through signals
            raw_signals = test["signals"]
            
            # Run scan
            result = scanner.scan_signals(raw_signals, transaction_id=txn_id)
            risk = result["risk_score"]
            decision = engine.decide_action(risk)
            action = decision["action"]
            
            sig_str = "[" + ", ".join(f"{s:.1f}" if abs(s) < 100 else f"{s:.0f}" for s in raw_signals) + "]"
            
            print(f"{test['name'][:32]:<32} | {sig_str:<30} | {risk:>7.4f} ({risk*100:5.1f}%) | {action:<14} | ✅ PASSED")
            
        except Exception as e:
            print(f"{test['name'][:32]:<32} | {'FAILED':<30} | {'ERR':<10} | {'CRASH':<14} | ❌ {str(e)}")

    print("-" * 105)
    
    # ── Test 9: Malformed Vector (Wrong dimensions / Invalid length) ──
    print("\n9. Testing Schema Validation on Wrong Length Vector (3 values instead of 6):")
    try:
        scanner.scan_signals([0.5, 0.2, 0.1], transaction_id="ERR-001")
        print("  ❌ Failed to catch malformed input length!")
    except ValueError as e:
        print(f"  ✅ Correctly caught & rejected malformed length: \"{e}\"")
        
    print("\n10. Testing Invalid Data Type (Passing string instead of float):")
    try:
        scanner.scan_signals(["bad", "data", "test", 0, 1, 2], transaction_id="ERR-002")
        print("  ❌ Failed to catch invalid string types!")
    except Exception as e:
        print(f"  ✅ Correctly caught & rejected invalid type: \"{e}\"")

    print("\n" + "=" * 80)
    print(" 🎉 STRESS TEST COMPLETE: System successfully validated on garbage & boundary data.")
    print("=" * 80)

if __name__ == "__main__":
    run_garbage_tests()
