"""
defend — Person 3 ATO Fraud Detection Package
==============================================
Provides real-time behavioral feature extraction, XGBoost classification,
IsolationForest anomaly detection, multi-signal risk fusion, adaptive memory,
decision explanation, and unified pipeline/adapter services.
"""

from defend.adapter import SignalAdapter
from defend.scanner import UnifiedScanner
from defend.features import FeatureEngine
from defend.behaviour import BehaviourEngine
from defend.baseline import XGBoostBaseline
from defend.anomaly import AnomalyDetector
from defend.risk_engine import RiskEngine
from defend.adaptive_memory import AdaptiveMemory
from defend.explain import ExplanationEngine
from defend.pipeline import DetectionPipeline

__all__ = [
    "SignalAdapter",
    "UnifiedScanner",
    "FeatureEngine",
    "BehaviourEngine",
    "XGBoostBaseline",
    "AnomalyDetector",
    "RiskEngine",
    "AdaptiveMemory",
    "ExplanationEngine",
    "DetectionPipeline",
]
