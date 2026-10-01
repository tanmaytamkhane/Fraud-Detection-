"""Inference on raw MM transfers using persisted HDC and XGBoost models."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from hdc.encoder import HDCEncoder
from hdc.model import HDCClassifier
from pipeline.mm_feature_engineer import MMFeatureEngineer, SIGNALS
from pipeline.mm_loader import load_config
from pipeline.mm_variant_labeler import label_variant
from pipeline.mm_schema import validate_transfer
from response.mm_graph_engine import MMGraph
from response.mm_engine import MMResponseEngine
from xgboost import XGBClassifier
from defend.mm_explain import explain
from response.mm_sar import generate_sar_narrative
from defend.mm_behaviour import score_matrix as behaviour_scores
from defend.mm_anomaly import MMAnomaly
from train_mm import fuse

ROOT = Path(__file__).parents[1]


class UnifiedMMScanner:
    def __init__(self, config_path=None):
        self.config = load_config(config_path or ROOT / "mm_config.json")
        model_dir = ROOT / self.config.get("model_dir", "models")
        results_path = ROOT / self.config.get("results_path", "results/mm_results.json")
        meta = json.loads((model_dir / "hdc_mm_encoder_meta.json").read_text())
        self.encoder = HDCEncoder(dim=meta["dim"], num_levels=meta["num_levels"], seed=meta["seed"])
        self.hdc = HDCClassifier(dim=meta["dim"])
        data = np.load(model_dir / "hdc_mm_prototypes.npz")
        self.hdc.prototypes = data["prototypes"]
        self.hdc.threshold = float(data["threshold"][0])
        self.hdc.is_trained = True
        self.xgb = XGBClassifier()
        self.xgb.load_model(str(model_dir / "xgb_mm_model.json"))
        self.xgb.set_params(n_jobs=1)
        self.anomaly = MMAnomaly.load(model_dir)
        self.threshold = json.loads(results_path.read_text())["metrics"]["fused"]["threshold"]
        self.features = MMFeatureEngineer(self.config)
        self.graph = MMGraph()
        self.response = MMResponseEngine()
        self.last_time = -float("inf")

    def scan_transfer(self, transfer_id, timestamp, sender, receiver, amount, device_id=None, channel=None):
        """A transfer must arrive in nondecreasing timestamp order for causal state."""
        validate_transfer(locals())
        t = float(timestamp)
        if t < self.last_time:
            raise ValueError("Transfer is older than scanner state; replay chronologically")
        self.last_time = t
        row = {"transfer_id": str(transfer_id), "time_value": t, "sender": str(sender),
               "receiver": str(receiver), "amount": float(amount)}
        if device_id is not None:
            row["device_id"] = str(device_id)
        frame = pd.DataFrame([row])
        signals = self.features.transform(frame).iloc[0]
        x = signals.to_numpy(dtype=np.float32).reshape(1, 6)
        hdc = float(self.hdc.get_fraud_score(self.encoder.encode_batch(x))[0])
        xgb = float(self.xgb.predict_proba(x)[0, 1])
        behaviour = float(behaviour_scores(x)[0])
        anomaly = float(self.anomaly.score(x)[0])
        fused = float(fuse(hdc,xgb,behaviour,anomaly))
        context_before = self.graph.get_mule_cluster(sender)
        network_risk = self.graph.get_network_risk(sender, receiver)
        top = sorted(signals.items(), key=lambda kv: kv[1], reverse=True)[:3]
        available = list(SIGNALS)
        if device_id is None:
            available.remove("shared_device_cluster")
        explanation = explain(signals.to_dict(), available)
        variant = label_variant(signals.to_dict(), available=available)
        decision = self.response.execute_action(transfer_id, fused, network_risk,
                                                variant_id=variant["variant_id"],
                                                graph_context=context_before, explanation=explanation)
        if decision["action"] != "APPROVE":
            decision["analyst_summary"] = explanation
            decision["sar_draft"] = generate_sar_narrative({"transfer_id": transfer_id,
                "sender": sender, "receiver": receiver, "amount": amount,
                "timestamp": timestamp, "explanation": explanation, "action": decision["action"]})
        self.graph.add_transfer(transfer_id, sender, receiver, amount, fused, decision["action"], timestamp, device_id)
        return {"transfer_id": str(transfer_id), "risk_score": fused,
                "is_fraud": bool(fused >= self.threshold), "decision": decision,
                "matched_variant": variant["variant_id"], "variant_name": variant.get("variant_name"),
                "variant_source": variant["source"],
                "sub_scores": {"hdc": hdc, "xgb": xgb, "behaviour": behaviour, "anomaly": anomaly},
                "signals": {k: float(v) for k, v in signals.items()},
                "signal_attributions": {k: float(v) for k, v in top},
                "explanation": explanation, "graph_context": self.graph.get_mule_cluster(sender)}

    def scan_batch(self, rows):
        return [self.scan_transfer(**r) for r in rows]
