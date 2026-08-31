import unittest
from defend.scanner import UnifiedScanner
from response.engine import ResponseEngine


class TestUnifiedScanner(unittest.TestCase):

    def setUp(self):
        self.scanner = UnifiedScanner()
        self.response_engine = ResponseEngine()

    def test_untrained_fallback_scan(self):
        # ATO-V1 (High-risk attack)
        signals = [0.95, 0.85, 0.90, 0.40, 0.20, 0.90]
        result = self.scanner.scan_signals(signals, transaction_id="TXN-001")

        self.assertIn("risk_score", result)
        self.assertIn("decision", result)
        self.assertIn("action", result)
        self.assertIn("matched_variant", result)
        self.assertIn("sub_scores", result)

        # High risk should trigger BLOCK or HOLD
        self.assertGreater(result["risk_score"], 0.70)
        self.assertEqual(result["decision"], "BLOCK")
        self.assertEqual(result["matched_variant"], "ATO-V1")

        # Response engine integration
        action = self.response_engine.execute_action(
            transaction_id="TXN-001",
            risk_score=result["risk_score"],
            variant_id=result.get("matched_variant")
        )
        self.assertEqual(action["action"], "BLOCK")

    def test_low_risk_legitimate_scan(self):
        # Legitimate transaction
        legit_signals = [0.10, 0.05, 0.10, 0.10, 0.15, 0.10]
        result = self.scanner.scan_signals(legit_signals, transaction_id="TXN-LEGIT")

        self.assertLess(result["risk_score"], 0.20)
        self.assertEqual(result["decision"], "APPROVE")
        self.assertEqual(result["risk_level"], "LOW")

        action = self.response_engine.execute_action(
            transaction_id="TXN-LEGIT",
            risk_score=result["risk_score"],
            variant_id=result.get("matched_variant")
        )
        self.assertEqual(action["action"], "APPROVE")

    def test_all_five_variants(self):
        variant_signals = {
            "ATO-V1": [0.95, 0.85, 0.90, 0.40, 0.20, 0.90],
            "ATO-V2": [0.20, 0.30, 0.40, 0.95, 0.20, 0.75],
            "ATO-V3": [0.20, 0.80, 0.10, 0.10, 0.90, 0.30],
            "ATO-V4": [0.20, 0.10, 0.25, 0.10, 0.10, 0.20],
            "ATO-V5": [0.35, 0.45, 0.25, 0.40, 0.60, 0.40],
        }

        for vid, sigs in variant_signals.items():
            res = self.scanner.scan_signals(sigs, transaction_id=f"TXN-{vid}")
            self.assertEqual(res["matched_variant"], vid)
            self.assertIsNotNone(res["variant_name"])

    def test_batch_scan(self):
        signals_batch = [
            [0.95, 0.85, 0.90, 0.40, 0.20, 0.90],
            [0.10, 0.05, 0.10, 0.10, 0.15, 0.10],
        ]
        results = self.scanner.scan_batch(signals_batch)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["decision"], "BLOCK")
        self.assertEqual(results[1]["decision"], "APPROVE")

    def test_trained_mode(self):
        # Train with synthetic dataset
        self.scanner.train()
        signals = [0.95, 0.85, 0.90, 0.40, 0.20, 0.90]
        result = self.scanner.scan_signals(signals, transaction_id="TXN-TRAINED")
        self.assertGreater(result["risk_score"], 0.70)


if __name__ == "__main__":
    unittest.main()
