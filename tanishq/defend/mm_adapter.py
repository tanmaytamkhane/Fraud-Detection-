"""Stable six-signal ordering for MM HDC and tabular models."""
import numpy as np
from pipeline.mm_feature_engineer import SIGNALS


def signal_array(signals):
    return np.asarray([signals.get(k, 0.0) for k in SIGNALS], dtype=np.float32)
