"""Isolation Forest trained only on the normal training sample."""
import json
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest


class MMAnomaly:
    def __init__(self, model=None, quantiles=None):
        self.model = model
        self.quantiles = quantiles

    def fit(self, normal_x, seed=42):
        self.model = IsolationForest(n_estimators=100, max_samples=min(256, len(normal_x)),
                                     random_state=seed, n_jobs=2)
        self.model.fit(normal_x)
        raw = -self.model.score_samples(normal_x)
        self.quantiles = np.quantile(raw, np.linspace(0, 1, 101))
        return self

    def score(self, x):
        raw = -self.model.score_samples(x)
        return np.interp(raw, self.quantiles, np.linspace(0, 1, 101)).astype(np.float32)

    def save(self, directory):
        directory = Path(directory)
        joblib.dump(self.model, directory / "mm_anomaly.joblib")
        (directory / "mm_anomaly_quantiles.json").write_text(json.dumps(self.quantiles.tolist()))

    @classmethod
    def load(cls, directory):
        directory = Path(directory)
        return cls(joblib.load(directory / "mm_anomaly.joblib"),
                   np.asarray(json.loads((directory / "mm_anomaly_quantiles.json").read_text())))
