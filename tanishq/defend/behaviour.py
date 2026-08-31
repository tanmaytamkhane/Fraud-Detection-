import pandas as pd
import numpy as np


class BehaviourEngine:
    """
    Converts ATO behavioural features into a normalized
    behavioural risk score.
    """

    def __init__(self, weights=None):
        self.weights = weights or {
            "new_device": 0.20,
            "new_beneficiary": 0.20,
            "amount_deviation": 0.20,
            "velocity_deviation": 0.15,
            "location_change": 0.15,
            "time_deviation": 0.10
        }

        self._validate_weights()

    def _validate_weights(self):
        total = sum(self.weights.values())

        if not np.isclose(total, 1.0):
            raise ValueError(
                f"Behaviour weights must sum to 1.0. "
                f"Current sum: {total}"
            )

    def normalize_deviation(self, value, cap=5.0):
        """
        Convert an unbounded deviation into a 0-1 score.
        """

        value = max(0.0, float(value))

        return min(value / cap, 1.0)

    def calculate_score(self, features):
        """
        Calculate behavioural risk score for one transaction.
        """

        scores = {
            "new_device": float(features["new_device"]),

            "new_beneficiary": float(
                features["new_beneficiary"]
            ),

            "amount_deviation": self.normalize_deviation(
                features["amount_deviation"]
            ),

            "velocity_deviation": self.normalize_deviation(
                features["velocity_deviation"]
            ),

            "location_change": float(
                features["location_change"]
            ),

            "time_deviation": self.normalize_deviation(
                features["time_deviation"]
            )
        }

        weighted_score = sum(
            scores[feature] * self.weights[feature]
            for feature in scores
        )

        return round(weighted_score, 4)

    def risk_level(self, score):
        """
        Convert numerical risk into an interpretable level.
        """

        if score < 0.30:
            return "LOW"

        if score < 0.60:
            return "MEDIUM"

        if score < 0.80:
            return "HIGH"

        return "CRITICAL"

    def analyze(self, features):
        """
        Analyze one transaction.
        """

        score = self.calculate_score(features)

        return {
            "transaction_id": features["transaction_id"],
            "behaviour_score": score,
            "risk_level": self.risk_level(score)
        }

    def analyze_dataframe(self, feature_dataframe):
        """
        Analyze every transaction in a feature DataFrame.
        """

        results = []

        for _, row in feature_dataframe.iterrows():
            results.append(
                self.analyze(row)
            )

        return pd.DataFrame(results)