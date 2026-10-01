"""Transparent MM behaviour score. It is a heuristic, not a probability."""
import numpy as np


def score_matrix(x):
    """Max of pass-through, hub, dormant, and shared-device patterns in [0,1]."""
    a = np.asarray(x)
    fan_out, fan_in, transit, ratio, device, dormancy = [a[:, i] for i in range(6)]
    return np.maximum.reduce((fan_out*ratio, fan_in*ratio, transit*ratio,
                              dormancy*ratio, device*np.maximum(fan_in, fan_out))).astype(np.float32)
