"""
Signal Adapter: Converts between Team Normalized Signals and Defend Features
=============================================================================

Team Schema (pipeline/ / config.SIGNAL_NAMES):
- device_risk: float [0.0, 1.0]
- address_mismatch: float [0.0, 1.0]
- amount_deviation: float [0.0, 1.0]
- velocity: float [0.0, 1.0]
- time_anomaly: float [0.0, 1.0]
- channel_risk: float [0.0, 1.0]

Defend Schema (defend/):
- new_device: int (0 or 1)
- location_change: int (0 or 1)
- amount_deviation: float (z-score, 0.0 to 5.0+)
- velocity_deviation: float (ratio, 0.0 to 5.0+)
- time_deviation: float (hours, 0.0 to 6.0+)
- new_beneficiary: int (0 or 1)
"""

from typing import Union, List, Dict, Any
import numpy as np
import pandas as pd


class SignalAdapter:
    """
    Bidirectional adapter between the Team's 6 normalized signals (0.0 to 1.0)
    and Person 3's defend/ feature schema.
    """

    TEAM_SIGNALS = [
        "device_risk",
        "address_mismatch",
        "amount_deviation",
        "velocity",
        "time_anomaly",
        "channel_risk",
    ]

    DEFEND_FEATURES = [
        "new_device",
        "new_beneficiary",
        "amount_deviation",
        "velocity_deviation",
        "location_change",
        "time_deviation",
    ]

    def __init__(
        self,
        device_threshold: float = 0.5,
        location_threshold: float = 0.5,
        beneficiary_threshold: float = 0.5,
        amount_scale: float = 5.0,
        velocity_scale: float = 5.0,
        time_scale: float = 6.0,
    ):
        self.device_threshold = device_threshold
        self.location_threshold = location_threshold
        self.beneficiary_threshold = beneficiary_threshold
        self.amount_scale = amount_scale
        self.velocity_scale = velocity_scale
        self.time_scale = time_scale

    def team_to_defend_dict(self, signals: Union[List[float], np.ndarray, Dict[str, float]]) -> Dict[str, Any]:
        """
        Convert team signals (list, array, or dict) to a defend feature dictionary.

        Mapping:
        - device_risk -> new_device (>=0.5 -> 1, else 0)
        - address_mismatch -> location_change (>=0.5 -> 1, else 0)
        - amount_deviation -> amount_deviation (* 5.0)
        - velocity -> velocity_deviation (* 5.0)
        - time_anomaly -> time_deviation (* 6.0)
        - channel_risk -> new_beneficiary (>=0.5 -> 1, else 0)
        """
        if isinstance(signals, (list, tuple, np.ndarray)):
            if len(signals) != 6:
                raise ValueError(f"Expected 6 signal values, got {len(signals)}")
            dev_risk = float(signals[0])
            addr_mis = float(signals[1])
            amt_dev = float(signals[2])
            vel = float(signals[3])
            time_anom = float(signals[4])
            chan_risk = float(signals[5])
        elif isinstance(signals, (dict, pd.Series)):
            dev_risk = float(signals.get("device_risk", 0.0) if hasattr(signals, "get") else signals["device_risk"])
            addr_mis = float(signals.get("address_mismatch", 0.0) if hasattr(signals, "get") else signals["address_mismatch"])
            amt_dev = float(signals.get("amount_deviation", 0.0) if hasattr(signals, "get") else signals["amount_deviation"])
            vel = float(signals.get("velocity", 0.0) if hasattr(signals, "get") else signals["velocity"])
            time_anom = float(signals.get("time_anomaly", 0.0) if hasattr(signals, "get") else signals["time_anomaly"])
            chan_risk = float(signals.get("channel_risk", 0.0) if hasattr(signals, "get") else signals["channel_risk"])
        else:
            raise TypeError(f"Unsupported signal type: {type(signals)}")

        return {
            "new_device": int(dev_risk >= self.device_threshold),
            "location_change": int(addr_mis >= self.location_threshold),
            "amount_deviation": round(amt_dev * self.amount_scale, 4),
            "velocity_deviation": round(vel * self.velocity_scale, 4),
            "time_deviation": round(time_anom * self.time_scale, 4),
            "new_beneficiary": int(chan_risk >= self.beneficiary_threshold),
        }

    def team_to_defend_df(self, df_signals: pd.DataFrame) -> pd.DataFrame:
        """
        Convert a pandas DataFrame of team signals to defend features DataFrame.
        """
        rows = [self.team_to_defend_dict(row) for _, row in df_signals.iterrows()]
        df_defend = pd.DataFrame(rows)
        if "transaction_id" in df_signals.columns:
            df_defend.insert(0, "transaction_id", df_signals["transaction_id"].values)
        return df_defend

    def defend_to_team_dict(self, features: Union[List[float], np.ndarray, Dict[str, Any], pd.Series]) -> Dict[str, float]:
        """
        Convert defend feature dictionary or list back to the team's 6 normalized signals (0.0 to 1.0).

        Reverse Mapping:
        - new_device -> device_risk (0.0 or 1.0)
        - location_change -> address_mismatch (0.0 or 1.0)
        - amount_deviation -> amount_deviation (capped / 5.0)
        - velocity_deviation -> velocity (capped / 5.0)
        - time_deviation -> time_anomaly (capped / 6.0)
        - new_beneficiary -> channel_risk (0.0 or 1.0)
        """
        if isinstance(features, (dict, pd.Series)):
            new_dev = float(features.get("new_device", 0) if hasattr(features, "get") else features["new_device"])
            loc_chg = float(features.get("location_change", 0) if hasattr(features, "get") else features["location_change"])
            amt_dev = float(features.get("amount_deviation", 0.0) if hasattr(features, "get") else features["amount_deviation"])
            vel_dev = float(features.get("velocity_deviation", 0.0) if hasattr(features, "get") else features["velocity_deviation"])
            time_dev = float(features.get("time_deviation", 0.0) if hasattr(features, "get") else features["time_deviation"])
            new_ben = float(features.get("new_beneficiary", 0) if hasattr(features, "get") else features["new_beneficiary"])
        elif isinstance(features, (list, tuple, np.ndarray)):
            # Ordered as DEFEND_FEATURES: [new_device, new_beneficiary, amount_deviation, velocity_deviation, location_change, time_deviation]
            if len(features) != 6:
                raise ValueError(f"Expected 6 defend feature values, got {len(features)}")
            new_dev = float(features[0])
            new_ben = float(features[1])
            amt_dev = float(features[2])
            vel_dev = float(features[3])
            loc_chg = float(features[4])
            time_dev = float(features[5])
        else:
            raise TypeError(f"Unsupported features type: {type(features)}")

        return {
            "device_risk": min(max(new_dev, 0.0), 1.0),
            "address_mismatch": min(max(loc_chg, 0.0), 1.0),
            "amount_deviation": round(min(max(amt_dev / self.amount_scale, 0.0), 1.0), 4),
            "velocity": round(min(max(vel_dev / self.velocity_scale, 0.0), 1.0), 4),
            "time_anomaly": round(min(max(time_dev / self.time_scale, 0.0), 1.0), 4),
            "channel_risk": min(max(new_ben, 0.0), 1.0),
        }

    def defend_to_team_df(self, df_features: pd.DataFrame) -> pd.DataFrame:
        """
        Convert a pandas DataFrame of defend features to team signals DataFrame.
        """
        rows = [self.defend_to_team_dict(row) for _, row in df_features.iterrows()]
        df_team = pd.DataFrame(rows)
        if "transaction_id" in df_features.columns:
            df_team.insert(0, "transaction_id", df_features["transaction_id"].values)
        return df_team

    # Convenience aliases
    def adapt(self, signals: Union[List[float], np.ndarray, Dict[str, float]]) -> Dict[str, Any]:
        """Convert team signals to defend features dictionary."""
        return self.team_to_defend_dict(signals)

    def reverse(self, features: Union[List[float], np.ndarray, Dict[str, Any]]) -> Dict[str, float]:
        """Convert defend features to team signals dictionary."""
        return self.defend_to_team_dict(features)
