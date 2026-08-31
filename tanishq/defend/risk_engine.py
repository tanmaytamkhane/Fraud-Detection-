import pandas as pd


class RiskEngine:
    """
    Combines different detection signals into a single
    risk score and final security decision.

    Current detection signals:
    - XGBoost
    - Behaviour score
    - Anomaly score

    Default fusion weights:
    - XGBoost   : 40%
    - Behaviour : 30%
    - Anomaly   : 30%

    HDC is intentionally NOT included yet.
    It will be integrated later as a fourth signal.

    Person 4's official mitigation thresholds:
    - < 0.20       -> APPROVE
    - 0.20 - 0.39  -> REVIEW
    - 0.40 - 0.59  -> STEP_UP_AUTH
    - 0.60 - 0.79  -> HOLD
    - >= 0.80      -> BLOCK
    """

    def __init__(
        self,
        xgb_weight=0.40,
        behaviour_weight=0.30,
        anomaly_weight=0.30
    ):
        self.weights = {
            "xgb": xgb_weight,
            "behaviour": behaviour_weight,
            "anomaly": anomaly_weight
        }

        self._validate_weights()

    def _validate_weights(self):
        """
        Make sure all fusion weights are valid
        and sum to exactly 1.0.
        """

        for name, weight in self.weights.items():

            if not 0.0 <= weight <= 1.0:
                raise ValueError(
                    f"{name} weight must be between 0 and 1. "
                    f"Current value: {weight}"
                )

        total = sum(self.weights.values())

        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"Risk weights must sum to 1.0. "
                f"Current sum: {total}"
            )

    def calculate_score(
        self,
        xgb_probability,
        behaviour_score,
        anomaly_score
    ):
        """
        Combine detection signals into one risk score.
        """

        score = (
            xgb_probability * self.weights["xgb"]
            + behaviour_score * self.weights["behaviour"]
            + anomaly_score * self.weights["anomaly"]
        )

        return round(score, 4)

    def decision(self, risk_score):
        """
        Convert risk score into the official mitigation action.

        < 0.20       -> APPROVE
        0.20 - 0.39  -> REVIEW
        0.40 - 0.59  -> STEP_UP_AUTH
        0.60 - 0.79  -> HOLD
        >= 0.80      -> BLOCK
        """

        if risk_score >= 0.80:
            return "BLOCK"

        if risk_score >= 0.60:
            return "HOLD"

        if risk_score >= 0.40:
            return "STEP_UP_AUTH"

        if risk_score >= 0.20:
            return "REVIEW"

        return "APPROVE"

    def risk_level(self, risk_score):
        """
        Convert numerical risk into a human-readable level.
        """

        if risk_score < 0.20:
            return "LOW"

        if risk_score < 0.40:
            return "MEDIUM"

        if risk_score < 0.80:
            return "HIGH"

        return "CRITICAL"

    def evaluate(
        self,
        transaction_id,
        xgb_probability,
        behaviour_score,
        anomaly_score
    ):
        """
        Evaluate one transaction.

        Existing P3 output fields are preserved.
        An 'action' field is also provided for Person 4.
        """

        risk_score = self.calculate_score(
            xgb_probability,
            behaviour_score,
            anomaly_score
        )

        action = self.decision(risk_score)

        return {
            "transaction_id": transaction_id,

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
            ),

            "risk_score": risk_score,

            "risk_level": self.risk_level(
                risk_score
            ),

            # Kept for backward compatibility with P3.
            "decision": action,

            # Matches Person 4's terminology.
            "action": action
        }

    def evaluate_dataframe(self, dataframe):
        """
        Evaluate multiple transactions.

        Expected columns:

        transaction_id
        xgb_probability
        behaviour_score
        anomaly_score
        """

        results = []

        for _, row in dataframe.iterrows():

            result = self.evaluate(
                transaction_id=row["transaction_id"],
                xgb_probability=row["xgb_probability"],
                behaviour_score=row["behaviour_score"],
                anomaly_score=row["anomaly_score"]
            )

            results.append(result)

        return pd.DataFrame(results)