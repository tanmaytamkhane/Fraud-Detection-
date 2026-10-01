"""Causal six-signal MM feature extraction. Each row sees prior rows and itself only."""
from collections import defaultdict, deque
import math
import numpy as np
import pandas as pd

SIGNALS = ("fan_out_degree", "fan_in_degree", "transit_velocity_sec",
           "amount_layering_ratio", "shared_device_cluster", "account_dormancy_score")


def _squash(n, scale):
    return 1.0 - math.exp(-max(0.0, n) / scale)


class MMFeatureEngineer:
    def __init__(self, cfg):
        self.cfg = cfg
        unit = float(cfg.get("seconds_per_step") or 1) if cfg["time_unit"] == "steps" else 1.0
        self.short = float(cfg.get("short_window_steps", 1)) * unit if cfg["time_unit"] == "steps" else float(cfg.get("short_window_sec", 3600))
        self.long = float(cfg.get("long_window_steps", 24)) * unit if cfg["time_unit"] == "steps" else float(cfg.get("long_window_days", 30)) * 86400
        self.dormancy = float(cfg.get("dormancy_steps", 30)) * unit if cfg["time_unit"] == "steps" else float(cfg.get("dormancy_days", 30)) * 86400
        self.out = defaultdict(deque)
        self.ins = defaultdict(deque)
        self.device = defaultdict(deque)
        self.last_activity = {}

    def transform(self, frame):
        """Streaming transform; caller must feed ascending (timestamp, transfer_id).

        Fan degrees use unique counterparties in short window, 1-exp(-n/4).
        Transit score is exp(-dwell/short). Pass-through is capped outflow/
        inflow in short window; if a currency threshold is known, it is averaged
        with the structuring-band share. Device accounts use 1-exp(-n/3).
        Dormancy uses 1-exp(-gap/dormancy). Unknown/no history is zero.
        """
        out = np.zeros((len(frame), 6), dtype=np.float32)
        values = frame[["sender", "receiver", "amount", "time_value"]].itertuples(index=False, name=None)
        has_device = "device_id" in frame
        devs = frame["device_id"].to_numpy() if has_device else None
        threshold = self.cfg.get("currency_threshold")
        band = self.cfg.get("structuring_band", [0.85, 1.0])
        for i, (sender, receiver, amount, t) in enumerate(values):
            sender, receiver, amount, t = str(sender), str(receiver), float(amount), float(t)
            oq, iq = self.out[sender], self.ins[receiver]
            while oq and oq[0][0] < t - self.short: oq.popleft()
            while iq and iq[0][0] < t - self.short: iq.popleft()
            prev_in = self.ins[sender]
            while prev_in and prev_in[0][0] < t - self.short: prev_in.popleft()
            oq.append((t, receiver, amount))
            iq.append((t, sender, amount))
            out[i, 0] = _squash(len({x[1] for x in oq}), 4)
            out[i, 1] = _squash(len({x[1] for x in iq}), 4)
            if prev_in:
                out[i, 2] = math.exp(-(t - prev_in[-1][0]) / max(self.short, 1e-9))
                incoming = sum(x[2] for x in prev_in)
                outgoing = sum(x[2] for x in oq)
                ratio = min(outgoing / max(incoming, 1e-9), 1.0)
                if threshold:
                    structured = sum(band[0]*threshold <= x[2] < band[1]*threshold for x in oq) / len(oq)
                    ratio = 0.5 * ratio + 0.5 * structured
                out[i, 3] = ratio
            if has_device and pd.notna(devs[i]):
                dq = self.device[str(devs[i])]
                while dq and dq[0][0] < t - self.long: dq.popleft()
                dq.append((t, sender))
                out[i, 4] = _squash(max(0, len({x[1] for x in dq})-1), 3)
            gaps = [t-self.last_activity[a] for a in (sender, receiver) if a in self.last_activity]
            if gaps:
                out[i, 5] = _squash(max(gaps) / max(self.dormancy, 1e-9), 1)
            self.last_activity[sender] = t
            self.last_activity[receiver] = t
        return pd.DataFrame(out, columns=SIGNALS, index=frame.index)
