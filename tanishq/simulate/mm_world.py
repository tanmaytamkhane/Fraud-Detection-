"""Synthetic transfer world for controlled MM stress tests, not ground truth evidence."""
import numpy as np
import pandas as pd


def build_world(n_accounts=800, n_steps=200, seed=42):
    rng = np.random.default_rng(seed)
    profiles = {}
    for i in range(n_accounts):
        profiles[f"ACC-{i:04d}"] = {"typical_amount": float(rng.lognormal(4.5, .8)),
                                    "activity_rate": float(rng.uniform(.02, .25)),
                                    "home_device": f"DEV-{i//2:04d}" if i < 100 else f"DEV-{i:04d}"}
    accounts = list(profiles)
    rows = []
    for step in range(n_steps):
        for sender in accounts:
            p = profiles[sender]
            for _ in range(rng.poisson(p["activity_rate"])):
                receiver = accounts[int(rng.integers(0, n_accounts))]
                if receiver == sender:
                    continue
                rows.append((step, sender, receiver, round(float(rng.lognormal(np.log(p["typical_amount"]), .85)), 2),
                             p["home_device"], "ordinary"))
    # Legitimate lookalikes create overlap with fraud features.
    for step in range(8, n_steps, 12):
        payer = accounts[int(rng.integers(0, n_accounts))]
        merchant = accounts[int(rng.integers(0, n_accounts))]
        for j in range(10):
            employee = accounts[int(rng.integers(0, n_accounts))]
            rows.append((step, payer, employee, round(float(rng.lognormal(4.5, .3)), 2), profiles[payer]["home_device"], "payroll"))
            rows.append((step, employee, merchant, round(float(rng.lognormal(3.4, .5)), 2), profiles[employee]["home_device"], "marketplace"))
    frame = pd.DataFrame(rows, columns=["timestamp", "sender", "receiver", "amount", "device_id", "lookalike_type"])
    frame["is_fraud"] = False
    frame["variant_id"] = ""
    frame["ring_id"] = ""
    frame["hop_level"] = 0
    return {"profiles": profiles, "transfers": frame, "seed": seed, "n_steps": n_steps}
