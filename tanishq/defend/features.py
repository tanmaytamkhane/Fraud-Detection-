"""
P3 Behavioural Feature Schema

Each transaction is converted into six behavioural signals:

1. new_device
   0 = known device
   1 = new/unrecognized device

2. new_beneficiary
   0 = known beneficiary
   1 = new beneficiary

3. amount_deviation
   Non-negative deviation from the user's normal transaction amount.
   Higher value = more unusual amount.

4. velocity_deviation
   Non-negative deviation from the user's normal transaction frequency.
   Higher value = more unusual transaction velocity.

5. location_change
   0 = normal/expected location
   1 = location differs from normal behaviour

6. time_deviation
   Non-negative deviation from the user's normal transaction time.
   Higher value = more unusual transaction time.

These are the canonical features currently used by the
Person 3 detection pipeline.

NOTE:
Person 1's HDC pipeline currently uses a different six-signal schema.
An explicit adapter will be created later when HDC integration begins.
"""


import pandas as pd
import numpy as np


class FeatureEngine:
    """
    Converts raw transaction data into behavioural features
    used by the ATO detection pipeline.
    """

    def __init__(self, user_profiles):
        self.user_profiles = user_profiles

    def new_device(self, user_id, device_id):
        profile = self.user_profiles[user_id]
        return int(device_id not in profile["devices"])

    def new_beneficiary(self, user_id, beneficiary_id):
        profile = self.user_profiles[user_id]
        return int(
            beneficiary_id not in profile["beneficiaries"]
        )

    def amount_deviation(self, user_id, amount):
        profile = self.user_profiles[user_id]

        mean_amount = profile["mean_amount"]
        std_amount = profile["std_amount"]

        if std_amount == 0:
            return 0.0

        return abs(amount - mean_amount) / std_amount

    def location_change(self, user_id, location):
        profile = self.user_profiles[user_id]

        return int(
            location not in profile["locations"]
        )

    def time_deviation(self, user_id, timestamp):
        profile = self.user_profiles[user_id]

        hour = timestamp.hour

        normal_start = profile["normal_hours"][0]
        normal_end = profile["normal_hours"][1]

        if normal_start <= hour <= normal_end:
            return 0.0

        distance_from_start = min(
            abs(hour - normal_start),
            24 - abs(hour - normal_start)
        )

        distance_from_end = min(
            abs(hour - normal_end),
            24 - abs(hour - normal_end)
        )

        return float(
            min(distance_from_start, distance_from_end)
        )

    def velocity_deviation(
        self,
        user_id,
        timestamp,
        transaction_history
    ):
        history = transaction_history[
            transaction_history["user_id"] == user_id
        ].copy()

        if history.empty:
            return 0.0

        history["timestamp"] = pd.to_datetime(
            history["timestamp"]
        )

        current_time = pd.to_datetime(timestamp)

        one_hour_ago = current_time - pd.Timedelta(hours=1)

        recent_transactions = history[
            (history["timestamp"] >= one_hour_ago)
            & (history["timestamp"] < current_time)
        ]

        current_velocity = len(recent_transactions)

        history["hour"] = history["timestamp"].dt.floor("h")

        hourly_counts = history.groupby("hour").size()

        if hourly_counts.empty:
            return 0.0

        normal_velocity = hourly_counts.mean()

        if normal_velocity == 0:
            return float(current_velocity)

        return float(current_velocity / normal_velocity)

    def extract_features(
        self,
        transaction,
        transaction_history
    ):
        user_id = transaction["user_id"]

        timestamp = pd.to_datetime(
            transaction["timestamp"]
        )

        return {
            "transaction_id": transaction["transaction_id"],

            "new_device": self.new_device(
                user_id,
                transaction["device_id"]
            ),

            "new_beneficiary": self.new_beneficiary(
                user_id,
                transaction["beneficiary_id"]
            ),

            "amount_deviation": self.amount_deviation(
                user_id,
                transaction["amount"]
            ),

            "velocity_deviation": self.velocity_deviation(
                user_id,
                timestamp,
                transaction_history
            ),

            "location_change": self.location_change(
                user_id,
                transaction["location"]
            ),

            "time_deviation": self.time_deviation(
                user_id,
                timestamp
            )
        }

    def transform(self, transactions):
        features = []

        for _, transaction in transactions.iterrows():

            result = self.extract_features(
                transaction,
                transactions
            )

            features.append(result)
        return pd.DataFrame(features)