"""
test_response_enhancements.py — Tests for Graph Escalation, LLM Summary, and Red-Teaming
"""

import unittest
from response.engine import ResponseEngine
from response.graph_engine import NetworkRiskGraph
from response.llm_summarizer import generate_case_summary


class TestResponseEnhancements(unittest.TestCase):

    def setUp(self):
        self.engine = ResponseEngine()

    def test_default_backward_compatibility(self):
        """Ensure default execute_action output has exact expected fields and behavior."""
        # Unchanged call pattern
        res = self.engine.execute_action("TXN-90001", 0.85, "ATO-V1", silent=True)

        self.assertEqual(res["action"], "BLOCK")
        self.assertEqual(res["transaction_id"], "TXN-90001")
        self.assertEqual(res["risk_score"], 0.85)
        self.assertEqual(res["risk_percent"], "85.0%")
        self.assertEqual(res["network_risk"], 0.0)
        self.assertEqual(res["effective_risk"], 0.85)
        self.assertIn("message", res)
        self.assertIn("notify", res)

    def test_graph_network_risk_escalation(self):
        """Test that a transaction connected to previously blocked entities gets escalated."""
        # 1. First transaction on account 1234 with device D1 gets blocked
        self.engine.execute_action(
            transaction_id="TXN-FRAUD-1",
            risk_score=0.90,
            card1=1234,
            device_id="DEV-BAD-99",
            addr1=300,
            silent=True,
        )

        # 2. Second transaction on a DIFFERENT account (5678) using the SAME bad device
        res2 = self.engine.execute_action(
            transaction_id="TXN-BORDERLINE-2",
            risk_score=0.55,  # Normally STEP_UP_AUTH (threshold 0.40 - 0.59)
            card1=5678,
            device_id="DEV-BAD-99",
            addr1=300,
            silent=True,
        )

        # Network risk should be > 0 and effective risk should escalate to HOLD or BLOCK
        self.assertGreater(res2["network_risk"], 0.0)
        self.assertGreater(res2["effective_risk"], 0.55)
        self.assertIn(res2["action"], ["HOLD", "BLOCK"])

    def test_llm_summarizer_fallback(self):
        """Test that LLM summary generates a valid string even without API key."""
        decision = self.engine.decide_action(0.75, "ATO-V2")
        decision["transaction_id"] = "TXN-SUMMARY-1"

        explanation_text = (
            "Transaction TXN-SUMMARY-1\n"
            "Risk Level: HIGH\n"
            "Decision: HOLD\n"
            "Why was it flagged?\n"
            "• Transaction velocity is unusual compared with normal behaviour."
        )

        summary = generate_case_summary(
            decision=decision,
            explanation_text=explanation_text,
            variant_name="Velocity Burst (Known Device)",
        )

        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 10)
        self.assertIn("HOLD", summary)

    def test_execute_action_with_explanation(self):
        """Test execute_action attaching analyst_summary when explanation is provided."""
        res = self.engine.execute_action(
            transaction_id="TXN-ANALYST-1",
            risk_score=0.88,
            variant_id="ATO-V1",
            explanation_text="• Transaction originated from a new device.",
            silent=True,
        )

        self.assertIn("analyst_summary", res)
        self.assertIsInstance(res["analyst_summary"], str)


if __name__ == "__main__":
    unittest.main()
