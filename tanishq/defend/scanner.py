"""
Unified Scanner: Real-time ATO Fraud Detection Scanner
======================================================
Connects Person 1 (identify/ registry) → Person 2 (simulate/) → Person 3 (defend/) → Person 4 (response/)

Accepts the team's 6 normalized signals:
[device_risk, address_mismatch, amount_deviation, velocity, time_anomaly, channel_risk]

Converts via SignalAdapter and evaluates across BehaviourEngine, AnomalyDetector, and XGBoostBaseline,
fusing them in RiskEngine to produce final risk scores and actionable bank decisions.
"""

from typing import Union, List, Dict, Any, Optional
from datetime import datetime
import numpy as np
import pandas as pd

from identify import AttackRegistry
from pipeline.variant_labeler import label_variants, VARIANT_NAMES
from defend.adapter import SignalAdapter
from defend.behaviour import BehaviourEngine
from defend.anomaly import AnomalyDetector
from defend.baseline import XGBoostBaseline
from defend.risk_engine import RiskEngine
from defend.adaptive_memory import AdaptiveMemory
from defend.explain import ExplanationEngine


class UnifiedScanner:
    """
    Unified real-time fraud scanner for Person 3's defend module.
    Converts team signals, performs multi-engine fusion scoring,
    matches against Person 1's official ATO variants, and outputs
    results compatible with Person 4's ResponseEngine.
    """

    def __init__(
        self,
        auto_load_registry: bool = True,
        risk_engine: Optional[RiskEngine] = None,
        behaviour_engine: Optional[BehaviourEngine] = None,
        anomaly_detector: Optional[AnomalyDetector] = None,
        xgb_baseline: Optional[XGBoostBaseline] = None,
        adapter: Optional[SignalAdapter] = None,
    ):
        # 1. Person 1 Ground Truth Attack Registry
        self.registry = AttackRegistry()
        if auto_load_registry:
            try:
                self.registry.load()
            except Exception as e:
                print(f"[UnifiedScanner] Warning: Failed to load registry: {e}")

        # 2. Defend Components
        self.adapter = adapter or SignalAdapter()
        self.behaviour_engine = behaviour_engine or BehaviourEngine()
        self.anomaly_detector = anomaly_detector or AnomalyDetector()
        self.xgb = xgb_baseline or XGBoostBaseline()
        self.risk_engine = risk_engine or RiskEngine()
        self.memory = AdaptiveMemory()
        self.explanation_engine = ExplanationEngine()

        # Cache variant metadata from Person 1
        self.variants_catalog = self._load_variants_catalog()

    def _load_variants_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Load variant details and expected risk levels from AttackRegistry."""
        catalog = {}
        try:
            ato = self.registry.get_attack("ATO-001")
            if ato:
                for v in ato.variants:
                    catalog[v.variant_id] = {
                        "name": v.name,
                        "description": v.description,
                        "risk_level": v.risk_level,
                        "risk_score": v.risk_score,
                        "expected_mitigation": v.expected_mitigation,
                        "detection_difficulty": v.detection_difficulty,
                    }
        except Exception:
            pass
        return catalog

    def train(self, dataframe: Optional[pd.DataFrame] = None, use_simulated: bool = False):
        """
        Train the XGBoost classifier and AnomalyDetector.
        If use_simulated is True, loads Person 2's simulated ATO dataset through
        the pipeline (same features HDC uses). Otherwise, uses the synthetic
        training data generator for fast, calibrated baseline training.
        """
        if dataframe is None:
            if use_simulated:
                try:
                    from pipeline.loader import load_simulated_data
                    from pipeline.feature_engineer import engineer_features
                    raw = load_simulated_data(sample_frac=0.1)
                    df_signals = engineer_features(raw)
                    df_defend = self.adapter.team_to_defend_df(df_signals)
                    df_defend["label"] = df_signals["isFraud"].values
                    dataframe = df_defend
                except Exception as e:
                    print(f"[UnifiedScanner] Simulated data unavailable ({e}), using synthetic fallback.")
                    from tests.generate_training_data import generate_dataset
                    dataframe = generate_dataset()
            else:
                from tests.generate_training_data import generate_dataset
                dataframe = generate_dataset()

        # Train XGBoost
        self.xgb.train(dataframe)

        # Train AnomalyDetector
        self.anomaly_detector.fit(dataframe)

    def scan_signals(
        self,
        signals: Union[List[float], np.ndarray, Dict[str, float]],
        transaction_id: str = "TXN-001",
    ) -> Dict[str, Any]:
        """
        Scan a single transaction given the 6 team signals:
        [device_risk, address_mismatch, amount_deviation, velocity, time_anomaly, channel_risk]

        Returns:
            Dict containing risk_score, decision, action, risk_level, matched_variant,
            sub-scores (behaviour_score, anomaly_score, xgb_probability), adapted features,
            and explanation.
        """
        # 1. Normalize input signals
        if isinstance(signals, dict):
            signal_list = [
                signals.get("device_risk", 0.0),
                signals.get("address_mismatch", 0.0),
                signals.get("amount_deviation", 0.0),
                signals.get("velocity", 0.0),
                signals.get("time_anomaly", 0.0),
                signals.get("channel_risk", 0.0),
            ]
            signals_dict = signals
        elif isinstance(signals, (list, tuple, np.ndarray)):
            if len(signals) != 6:
                raise ValueError(f"Expected 6 signal values, got {len(signals)}")
            signal_list = [float(x) for x in signals]
            signals_dict = {
                "device_risk": signal_list[0],
                "address_mismatch": signal_list[1],
                "amount_deviation": signal_list[2],
                "velocity": signal_list[3],
                "time_anomaly": signal_list[4],
                "channel_risk": signal_list[5],
            }
        else:
            raise TypeError(f"Unsupported signals type: {type(signals)}")

        # 2. Convert to Defend Feature Schema
        defend_features = self.adapter.team_to_defend_dict(signals_dict)
        defend_features["transaction_id"] = transaction_id

        # 3. Behaviour Scoring
        behaviour_score = self.behaviour_engine.calculate_score(defend_features)

        # 4. XGBoost Probability (with fallback to behaviour_score if untrained)
        df_feat = pd.DataFrame([defend_features])
        if self.xgb.is_trained:
            try:
                pred_df = self.xgb.predict(df_feat)
                xgb_probability = float(pred_df["ato_probability"].iloc[0])
            except Exception:
                xgb_probability = behaviour_score
        else:
            xgb_probability = behaviour_score

        # 5. Anomaly Scoring (with fallback to behaviour_score if untrained)
        if self.anomaly_detector.is_trained:
            try:
                anom_df = self.anomaly_detector.analyze(df_feat)
                anomaly_score = float(anom_df["anomaly_score"].iloc[0])
            except Exception:
                anomaly_score = behaviour_score
        else:
            anomaly_score = behaviour_score

        # 6. Risk Engine Evaluation
        risk_result = self.risk_engine.evaluate(
            transaction_id=transaction_id,
            xgb_probability=xgb_probability,
            behaviour_score=behaviour_score,
            anomaly_score=anomaly_score,
        )

        # 7. Identify Variant (Person 1 ATO Variant classification)
        sig_arr = np.array(signal_list, dtype=np.float32).reshape(1, 6)
        matched_variant = str(label_variants(sig_arr)[0])
        variant_info = self.variants_catalog.get(matched_variant, {})

        # 8. Store in Adaptive Memory
        self.memory.store(
            transaction_id=transaction_id,
            features=defend_features,
            risk_score=risk_result["risk_score"],
            decision=risk_result["decision"],
        )

        # 9. Explanation
        explanation = self.explanation_engine.generate_text(
            transaction_id=transaction_id,
            features=defend_features,
            xgb_probability=risk_result["xgb_probability"],
            behaviour_score=risk_result["behaviour_score"],
            anomaly_score=risk_result["anomaly_score"],
            risk_score=risk_result["risk_score"],
            risk_level=risk_result["risk_level"],
            decision=risk_result["decision"],
        )

        return {
            "transaction_id": transaction_id,
            "risk_score": risk_result["risk_score"],
            "risk_level": risk_result["risk_level"],
            "decision": risk_result["decision"],
            "action": risk_result["action"],
            "matched_variant": matched_variant,
            "variant": matched_variant,
            "variant_name": variant_info.get("name", VARIANT_NAMES.get(matched_variant, "Normal Activity")),
            "expected_mitigation": variant_info.get("expected_mitigation", "approve"),
            "sub_scores": {
                "behaviour_score": risk_result["behaviour_score"],
                "xgb_probability": risk_result["xgb_probability"],
                "anomaly_score": risk_result["anomaly_score"],
            },
            "signals": signals_dict,
            "defend_features": defend_features,
            "explanation": explanation,
            "timestamp": datetime.now().isoformat(),
        }

    def scan_batch(
        self,
        signal_matrix: Union[List[List[float]], np.ndarray, pd.DataFrame],
        id_prefix: str = "TXN",
    ) -> List[Dict[str, Any]]:
        """
        Scan a batch of transactions.
        """
        results = []
        if isinstance(signal_matrix, pd.DataFrame):
            for i, (_, row) in enumerate(signal_matrix.iterrows()):
                txn_id = row.get("transaction_id", f"{id_prefix}-{i+1:04d}")
                sig_dict = {col: row[col] for col in SignalAdapter.TEAM_SIGNALS if col in row}
                results.append(self.scan_signals(sig_dict, transaction_id=txn_id))
        else:
            for i, sigs in enumerate(signal_matrix):
                txn_id = f"{id_prefix}-{i+1:04d}"
                results.append(self.scan_signals(sigs, transaction_id=txn_id))
        return results

    def get_variant_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Return the official ATO variant catalog from Person 1's AttackRegistry."""
        return self.variants_catalog
