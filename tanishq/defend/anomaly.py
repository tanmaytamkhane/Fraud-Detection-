import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


class AnomalyDetector:
    """
    Detects transactions that are unusual compared
    with legitimate behavioural patterns.
    """

    def __init__(
        self,
        contamination=0.05,
        random_state=42
    ):
        self.feature_columns = [
            "new_device",
            "new_beneficiary",
            "amount_deviation",
            "velocity_deviation",
            "location_change",
            "time_deviation"
        ]

        self.model = Pipeline([
            (
                "scaler",
                StandardScaler()
            ),
            (
                "isolation_forest",
                IsolationForest(
                    n_estimators=200,
                    contamination=contamination,
                    random_state=random_state
                )
            )
        ])

        self.normal_scores = None
        self.is_trained = False

    def fit(self, dataframe):
        """
        Train the anomaly detector using legitimate
        transactions.

        If a 'label' column exists:
            0 = legitimate
            1 = ATO

        Only legitimate transactions are used for training.
        """

        data = dataframe.copy()

        if "label" in data.columns:
            data = data[data["label"] == 0]

        X = data[self.feature_columns]

        if len(X) < 10:
            raise ValueError(
                "Need at least 10 legitimate transactions "
                "to train the anomaly detector."
            )

        self.model.fit(X)

        # Store scores of legitimate training behaviour.
        self.normal_scores = self.model.decision_function(X)

        self.is_trained = True

        return self

    def _calculate_anomaly_score(self, decision_scores):
        """
        Convert Isolation Forest scores into a 0-1
        anomaly score.

        Higher value = more anomalous.
        """

        if self.normal_scores is None:
            raise RuntimeError(
                "Anomaly detector has not been trained."
            )

        # Percentile of each score relative to normal behaviour.
        percentiles = np.array([
            np.mean(self.normal_scores <= score)
            for score in decision_scores
        ])

        # Isolation Forest gives lower scores to anomalies.
        anomaly_scores = 1.0 - percentiles

        return np.clip(
            anomaly_scores,
            0.0,
            1.0
        )

    def score(self, dataframe):
        """
        Calculate anomaly scores for transactions.
        """

        if not self.is_trained:
            raise RuntimeError(
                "Train the anomaly detector before scoring."
            )

        X = dataframe[self.feature_columns]

        decision_scores = self.model.decision_function(X)

        anomaly_scores = self._calculate_anomaly_score(
            decision_scores
        )

        predictions = self.model.predict(X)

        return pd.DataFrame({
            "anomaly_score": anomaly_scores,
            "is_anomalous": predictions == -1
        })

    def analyze(self, dataframe, threshold=0.95):
        """
        Return anomaly score and final anomaly decision.
        """

        results = self.score(dataframe)

        results["is_anomalous"] = (
            results["anomaly_score"] >= threshold
        )

        if "transaction_id" in dataframe.columns:
            results.insert(
                0,
                "transaction_id",
                dataframe["transaction_id"].values
            )

        return results