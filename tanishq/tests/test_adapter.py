import unittest
import numpy as np
import pandas as pd
from defend.adapter import SignalAdapter


class TestSignalAdapter(unittest.TestCase):

    def setUp(self):
        self.adapter = SignalAdapter()

    def test_forward_conversion_list(self):
        # [device_risk, address_mismatch, amount_deviation, velocity, time_anomaly, channel_risk]
        signals = [0.95, 0.85, 0.90, 0.40, 0.20, 0.90]
        features = self.adapter.team_to_defend_dict(signals)

        self.assertEqual(features["new_device"], 1)
        self.assertEqual(features["location_change"], 1)
        self.assertAlmostEqual(features["amount_deviation"], 4.5, places=2)
        self.assertAlmostEqual(features["velocity_deviation"], 2.0, places=2)
        self.assertAlmostEqual(features["time_deviation"], 1.2, places=2)
        self.assertEqual(features["new_beneficiary"], 1)

    def test_forward_conversion_dict(self):
        signals = {
            "device_risk": 0.2,
            "address_mismatch": 0.1,
            "amount_deviation": 0.4,
            "velocity": 0.6,
            "time_anomaly": 0.5,
            "channel_risk": 0.3,
        }
        features = self.adapter.team_to_defend_dict(signals)

        self.assertEqual(features["new_device"], 0)
        self.assertEqual(features["location_change"], 0)
        self.assertAlmostEqual(features["amount_deviation"], 2.0, places=2)
        self.assertAlmostEqual(features["velocity_deviation"], 3.0, places=2)
        self.assertAlmostEqual(features["time_deviation"], 3.0, places=2)
        self.assertEqual(features["new_beneficiary"], 0)

    def test_reverse_conversion(self):
        defend_features = {
            "new_device": 1,
            "new_beneficiary": 1,
            "amount_deviation": 4.5,
            "velocity_deviation": 2.0,
            "location_change": 1,
            "time_deviation": 1.2,
        }
        team_signals = self.adapter.defend_to_team_dict(defend_features)

        self.assertEqual(team_signals["device_risk"], 1.0)
        self.assertEqual(team_signals["address_mismatch"], 1.0)
        self.assertAlmostEqual(team_signals["amount_deviation"], 0.9, places=2)
        self.assertAlmostEqual(team_signals["velocity"], 0.4, places=2)
        self.assertAlmostEqual(team_signals["time_anomaly"], 0.2, places=2)
        self.assertEqual(team_signals["channel_risk"], 1.0)

    def test_dataframe_conversion(self):
        df_team = pd.DataFrame([
            {"device_risk": 0.9, "address_mismatch": 0.8, "amount_deviation": 0.6, "velocity": 0.4, "time_anomaly": 0.5, "channel_risk": 0.7, "transaction_id": "T1"},
            {"device_risk": 0.1, "address_mismatch": 0.2, "amount_deviation": 0.1, "velocity": 0.2, "time_anomaly": 0.1, "channel_risk": 0.1, "transaction_id": "T2"},
        ])
        df_defend = self.adapter.team_to_defend_df(df_team)
        self.assertEqual(len(df_defend), 2)
        self.assertIn("transaction_id", df_defend.columns)
        self.assertEqual(df_defend.iloc[0]["new_device"], 1)
        self.assertEqual(df_defend.iloc[1]["new_device"], 0)

        df_back = self.adapter.defend_to_team_df(df_defend)
        self.assertEqual(len(df_back), 2)
        self.assertIn("transaction_id", df_back.columns)


if __name__ == "__main__":
    unittest.main()
