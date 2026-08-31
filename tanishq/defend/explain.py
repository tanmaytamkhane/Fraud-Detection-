class ExplanationEngine:
    """
    Generates human-readable explanations for ATO risk decisions.
    """

    def __init__(self):

        self.feature_messages = {
            "new_device": (
                "Transaction originated from a new device."
            ),
            "new_beneficiary": (
                "A new beneficiary was used."
            ),
            "amount_deviation": (
                "Transaction amount is significantly different "
                "from the user's normal spending pattern."
            ),
            "velocity_deviation": (
                "Transaction velocity is unusual compared "
                "with normal behaviour."
            ),
            "location_change": (
                "Transaction location differs from the "
                "user's normal location."
            ),
            "time_deviation": (
                "Transaction occurred at an unusual time."
            )
        }

    def _get_feature_reasons(self, features):
        """
        Identify behavioural features contributing to risk.
        """

        reasons = []

        if features.get("new_device", 0) == 1:
            reasons.append(
                self.feature_messages["new_device"]
            )

        if features.get("new_beneficiary", 0) == 1:
            reasons.append(
                self.feature_messages["new_beneficiary"]
            )

        if features.get("amount_deviation", 0) >= 2.0:
            reasons.append(
                self.feature_messages["amount_deviation"]
            )

        if features.get("velocity_deviation", 0) >= 2.0:
            reasons.append(
                self.feature_messages["velocity_deviation"]
            )

        if features.get("location_change", 0) == 1:
            reasons.append(
                self.feature_messages["location_change"]
            )

        if features.get("time_deviation", 0) >= 2.0:
            reasons.append(
                self.feature_messages["time_deviation"]
            )

        return reasons

    def generate(
        self,
        transaction_id,
        features,
        xgb_probability,
        behaviour_score,
        anomaly_score,
        risk_score,
        risk_level,
        decision
    ):
        """
        Generate a structured explanation for one transaction.
        """

        reasons = self._get_feature_reasons(features)

        if not reasons:
            reasons.append(
                "No major behavioural deviations were detected."
            )

        return {
            "transaction_id": transaction_id,
            "risk_level": risk_level,
            "decision": decision,
            "risk_score": round(risk_score, 4),

            "detection_signals": {
                "xgb_probability": round(
                    xgb_probability,
                    4
                ),
                "behaviour_score": round(
                    behaviour_score,
                    4
                ),
                "anomaly_score": round(
                    anomaly_score,
                    4
                )
            },

            "reasons": reasons
        }

    def generate_text(
        self,
        transaction_id,
        features,
        xgb_probability,
        behaviour_score,
        anomaly_score,
        risk_score,
        risk_level,
        decision
    ):
        """
        Generate a human-readable explanation.
        """

        explanation = self.generate(
            transaction_id,
            features,
            xgb_probability,
            behaviour_score,
            anomaly_score,
            risk_score,
            risk_level,
            decision
        )

        lines = [
            f"Transaction {transaction_id}",
            "",
            f"Risk Level: {explanation['risk_level']}",
            f"Decision: {explanation['decision']}",
            f"Risk Score: {explanation['risk_score']}",
            "",
            "Why was it flagged?"
        ]

        for reason in explanation["reasons"]:
            lines.append(f"• {reason}")

        lines.extend([
            "",
            "Detection Signals:",
            (
                f"• XGBoost probability: "
                f"{explanation['detection_signals']['xgb_probability']}"
            ),
            (
                f"• Behaviour score: "
                f"{explanation['detection_signals']['behaviour_score']}"
            ),
            (
                f"• Anomaly score: "
                f"{explanation['detection_signals']['anomaly_score']}"
            )
        ])

        return "\n".join(lines)