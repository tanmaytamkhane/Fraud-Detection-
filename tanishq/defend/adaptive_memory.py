import pandas as pd
from datetime import datetime


class AdaptiveMemory:
    """
    Stores previous transaction decisions and outcomes.

    This provides a simple memory layer that can later
    be connected to the HDC adaptive learning system.
    """

    def __init__(self, max_size=10000):

        self.max_size = max_size

        self.memory = []

    def store(
        self,
        transaction_id,
        features,
        risk_score,
        decision,
        actual_label=None
    ):
        """
        Store a transaction and its security outcome.

        actual_label:
            0 = legitimate
            1 = ATO
            None = unknown/not yet confirmed
        """

        record = {
            "timestamp": datetime.now().isoformat(),
            "transaction_id": transaction_id,
            "features": dict(features),
            "risk_score": float(risk_score),
            "decision": decision,
            "actual_label": actual_label
        }

        self.memory.append(record)

        # Keep only the most recent records.
        if len(self.memory) > self.max_size:
            self.memory.pop(0)

    def update_outcome(
        self,
        transaction_id,
        actual_label
    ):
        """
        Update the confirmed outcome of a transaction.
        """

        for record in reversed(self.memory):

            if record["transaction_id"] == transaction_id:

                record["actual_label"] = actual_label

                return True

        return False

    def get_all(self):
        """
        Return all stored memory records.
        """

        return list(self.memory)

    def to_dataframe(self):
        """
        Convert memory into a DataFrame.
        """

        if not self.memory:
            return pd.DataFrame()

        records = []

        for record in self.memory:

            flattened = {
                "timestamp": record["timestamp"],
                "transaction_id": record["transaction_id"],
                "risk_score": record["risk_score"],
                "decision": record["decision"],
                "actual_label": record["actual_label"]
            }

            flattened.update(
                record["features"]
            )

            records.append(flattened)

        return pd.DataFrame(records)

    def get_confirmed_ato(self):
        """
        Return transactions confirmed as ATO.
        """

        return [
            record
            for record in self.memory
            if record["actual_label"] == 1
        ]

    def get_false_positives(self):
        """
        Return transactions that were flagged but
        later confirmed legitimate.
        """

        return [
            record
            for record in self.memory
            if (
                record["decision"] in ["REVIEW", "BLOCK"]
                and record["actual_label"] == 0
            )
        ]

    def size(self):
        """
        Return current memory size.
        """

        return len(self.memory)