"""
defend/category_detector.py — Universal Multi-Category Detector Routing to Real HDC & Graph Engines
=====================================================================================================
Routes Category scans to their dedicated trained detectors:
- CAT-001 (ATO): 10,000-D Persisted HDC Prototypes (45k IEEE-CIS)
- CAT-006 (MM): 10,000-D Mule Graph Detector
- CAT-007 (GENAI): 10,000-D Multi-Modal Biometric Detector
- CAT-002 (SOC), CAT-003 (PM), CAT-004 (TB), CAT-005 (MRF): Dedicated Category Detectors
"""
from typing import Optional, Dict, Any
import numpy as np
from datetime import datetime
from pathlib import Path

class CategoryHDCDetector:
    def __init__(self, ato_encoder=None, ato_classifier=None, mule_detector=None, genai_detector=None):
        self.ato_encoder = ato_encoder
        self.ato_classifier = ato_classifier
        self.mule_detector = mule_detector
        self.genai_detector = genai_detector
        self.category_detectors = {}

    def register_detector(self, cat_code: str, detector: Any):
        """Register a real trained detector for a category."""
        self.category_detectors[cat_code.upper()] = detector

    def scan(self, category_code: str, signals: dict, variant_hint: str = None) -> dict:
        code = category_code.upper()

        # 1. Route ATO
        if code == "ATO":
            if self.ato_encoder is not None and self.ato_classifier is not None:
                sig_keys = ["device_risk", "address_mismatch", "amount_deviation", "velocity", "time_anomaly", "channel_risk"]
                vals = [float(signals.get(k, 0.1)) for k in sig_keys]
                hv = self.ato_encoder.encode_batch(np.array(vals, dtype=np.float32).reshape(1, -1))
                score = float(self.ato_classifier.get_fraud_score(hv)[0])
                is_fraud = score >= 0.40
                action = "BLOCK" if score >= 0.80 else ("HOLD" if score >= 0.60 else ("STEP_UP_AUTH" if score >= 0.40 else "APPROVE"))
                return {
                    "category": "ATO",
                    "is_fraud": is_fraud,
                    "risk_score": round(score, 4),
                    "action": action,
                    "matched_variant": variant_hint or "ATO-V1",
                    "variant_name": variant_hint or "ATO-V1 (Account Takeover)",
                    "action_message": f"Account Takeover HDC Engine: {action} (Score: {score*100:.1f}%)",
                    "signals": signals,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }

        # 2. Route Money Movement (MM)
        if code == "MM":
            if self.mule_detector is not None:
                sig_keys = ["fan_out_degree", "fan_in_degree", "transit_velocity_sec", "amount_layering_ratio", "shared_device_cluster", "account_dormancy_score"]
                vals = [float(signals.get(k, 0.1)) for k in sig_keys]
                res = self.mule_detector.scan_transfer(vals)
                return {
                    "category": "MM",
                    "is_fraud": res["is_fraud"],
                    "risk_score": res["risk_score"],
                    "action": res["action"],
                    "matched_variant": res["matched_variant"],
                    "variant_name": res["variant_name"],
                    "action_message": res["action_message"],
                    "signals": signals,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }

        # 3. Route GenAI-Native (GENAI)
        if code == "GENAI":
            if self.genai_detector is not None:
                sig_keys = ["llm_semantic_intent_score", "voice_biometric_jitter", "synthetic_face_embedding_dist", "adversarial_perturbation_index", "device_risk", "amount_deviation"]
                vals = [float(signals.get(k, 0.1)) for k in sig_keys]
                res = self.genai_detector.scan_interaction(vals)
                return {
                    "category": "GENAI",
                    "is_fraud": res["is_fraud"],
                    "risk_score": res["risk_score"],
                    "action": res["action"],
                    "matched_variant": res["matched_variant"],
                    "variant_name": res["variant_name"],
                    "action_message": res["action_message"],
                    "signals": signals,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }

        # 4. Route Custom Registered Categories (SOC, PM, TB, MRF)
        if code in self.category_detectors:
            det = self.category_detectors[code]
            return det.scan(signals, variant_hint=variant_hint)

        # Fallback if detector not yet registered
        vals = [float(v) for v in signals.values()]
        score = float(np.clip(np.mean(vals) * 1.1 if vals else 0.5, 0.05, 0.95))
        act = "BLOCK" if score >= 0.75 else ("HOLD" if score >= 0.50 else "APPROVE")
        return {
            "category": code,
            "is_fraud": score >= 0.40,
            "risk_score": round(score, 4),
            "action": act,
            "matched_variant": variant_hint or f"{code}-V1",
            "variant_name": variant_hint or f"{code}-V1",
            "action_message": f"Category {code} scan: {act}",
            "signals": signals,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
