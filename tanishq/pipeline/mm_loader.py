"""Explicit CSV mapping and read-only dataset probe for money movement."""
import argparse
import json
from pathlib import Path
import pandas as pd

REQUIRED = ("sender", "receiver", "amount", "timestamp")
CANDIDATES = {
    "transfer_id": ["TX_ID", "transfer_id", "id"],
    "sender": ["SENDER_ACCOUNT_ID", "nameOrig", "sender", "Account"],
    "receiver": ["RECEIVER_ACCOUNT_ID", "nameDest", "receiver", "Account.1"],
    "sender_bank": ["From Bank"], "receiver_bank": ["To Bank"],
    "amount": ["TX_AMOUNT", "amount", "Amount Received"],
    "timestamp": ["TIMESTAMP", "step", "Timestamp"],
    "label": ["IS_FRAUD", "isFraud", "Is Laundering"],
    "device_id": ["device_id", "Device ID"],
    "ip": ["ip_subnet", "IP"],
    "channel": ["TX_TYPE", "type", "Payment Format"],
    "variant": ["variant_id", "ALERT_TYPE"],
}


def probe(path):
    sample = pd.read_csv(path, nrows=10000, low_memory=False)
    guesses = {key: next((c for c in names if c in sample.columns), None)
               for key, names in CANDIDATES.items()}
    out = {"file": str(path), "sample_rows": len(sample), "columns": list(sample.columns),
           "dtypes": {c: str(t) for c, t in sample.dtypes.items()},
           "null_rate": sample.isna().mean().round(4).to_dict(),
           "candidate_column_map": guesses,
           "warnings": ["Column guesses require confirmation before training."]}
    if guesses["timestamp"]:
        s = sample[guesses["timestamp"]]
        out["sample_time_range"] = [str(s.min()), str(s.max())]
    if guesses["label"]:
        out["sample_class_counts"] = {str(k): int(v) for k, v in sample[guesses["label"]].value_counts().items()}
    return out


def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    for k in REQUIRED:
        if not cfg.get("column_map", {}).get(k):
            raise ValueError(f"Confirm column_map.{k} in config")
    if cfg.get("split") != "time":
        raise ValueError("Only chronological split is supported")
    if cfg.get("time_unit") == "steps" and cfg.get("seconds_per_step") is None:
        print("WARNING: timestamp step duration unknown; windows and transit are in steps, not seconds.")
    return cfg


def load_transfers(path, cfg, chunksize=100000):
    """Yield canonical chunks. Never import ALERT_ID: it reveals the outcome."""
    mapping = cfg["column_map"]
    for chunk in pd.read_csv(path, chunksize=chunksize, low_memory=False):
        missing = [k for k in REQUIRED if mapping[k] not in chunk]
        if missing:
            raise ValueError(f"Missing mapped fields: {missing}")
        cols = {v: k for k, v in mapping.items() if v and v in chunk}
        d = chunk[list(cols)].rename(columns=cols)
        if "transfer_id" not in d:
            d["transfer_id"] = [f"row-{i}" for i in chunk.index]
        d["sender"] = d["sender"].astype(str)
        d["receiver"] = d["receiver"].astype(str)
        if "sender_bank" in d:
            d["sender"] = d["sender_bank"].astype(str) + ":" + d["sender"]
        if "receiver_bank" in d:
            d["receiver"] = d["receiver_bank"].astype(str) + ":" + d["receiver"]
        d["amount"] = pd.to_numeric(d["amount"], errors="raise")
        if (d["amount"] < 0).any():
            raise ValueError("Negative transfer amount")
        if cfg["time_unit"] == "ISO string":
            d["time_value"] = pd.to_datetime(d["timestamp"], utc=True).astype("int64") / 1e9
        else:
            d["time_value"] = pd.to_numeric(d["timestamp"], errors="raise").astype(float)
            if cfg["time_unit"] == "steps" and cfg.get("seconds_per_step"):
                d["time_value"] *= float(cfg["seconds_per_step"])
        if "label" in d:
            positives = set(str(x).lower() for x in cfg["label_positive_values"])
            d["label"] = d["label"].astype(str).str.lower().isin(positives).astype("int8")
        yield d


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", required=True)
    args = ap.parse_args()
    result = probe(args.probe)
    print(json.dumps(result, indent=2))
    draft = json.loads((Path(__file__).parents[1] / "mm_config.json").read_text())
    draft["column_map"] = result["candidate_column_map"]
    dest = Path("mm_config.draft.json")
    dest.write_text(json.dumps(draft, indent=2), encoding="utf-8")
    print(f"Draft mapping: {dest.resolve()} (review before use)")
