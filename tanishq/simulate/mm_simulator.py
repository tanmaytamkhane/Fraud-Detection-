"""Inject transfer sequences into an account world using MM variant knobs."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from simulate.mm_world import build_world


def simulate_mm(world, variant_id, simulation_config, n_rings=20, seed=42):
    rng = np.random.default_rng(seed)
    accounts = list(world["profiles"])
    rows = []
    cfg = simulation_config
    for ring in range(n_rings):
        start = int(rng.integers(10, world["n_steps"]-20))
        n_send = max(1, int(cfg.get("n_senders", 1)))
        n_recv = max(1, int(cfg.get("n_receivers", 1)))
        selected = rng.choice(accounts, size=min(len(accounts), n_send+n_recv+3), replace=False).tolist()
        sources = selected[:n_send]
        middle = selected[n_send:n_send+n_recv]
        cashout = selected[-1]
        dwell = max(0, int(cfg.get("dwell_steps", 1)))
        shared = f"RING-DEV-{variant_id}-{ring}"
        def emit(ts, sender, receiver, amount, hop):
            device = shared if rng.random() < float(cfg.get("shared_device_prob", 0)) else world["profiles"][sender]["home_device"]
            rows.append({"timestamp": ts, "sender": sender, "receiver": receiver,
                         "amount": round(float(amount), 2), "device_id": device,
                         "lookalike_type": "", "is_fraud": True, "variant_id": variant_id,
                         "ring_id": f"{variant_id}-R{ring:03d}", "hop_level": hop})
        amount_min, amount_max = cfg.get("amount_range", [20, 500])
        if variant_id == "MM-V3":
            hub = middle[0]
            for sender in sources:
                emit(start, sender, hub, rng.uniform(amount_min, amount_max), 1)
            emit(start+dwell, hub, cashout, len(sources)*rng.uniform(amount_min, amount_max)*cfg.get("pass_through_ratio", .9), 2)
        elif variant_id == "MM-V4":
            # Reserve a quiet account for the ring by removing earlier synthetic activity.
            dormant = middle[0]
            world["transfers"] = world["transfers"][~((world["transfers"].sender == dormant) &
                (world["transfers"].timestamp >= start-int(cfg.get("dormant_steps_before_activation", 60))) &
                (world["transfers"].timestamp < start))]
            emit(start, sources[0], dormant, rng.uniform(amount_min, amount_max), 1)
            emit(start+dwell, dormant, cashout, rng.uniform(amount_min, amount_max)*cfg.get("pass_through_ratio", .85), 2)
        else:
            for receiver in middle:
                amt = rng.uniform(amount_min, amount_max)
                emit(start, sources[0], receiver, amt, 1)
                emit(start+dwell, receiver, cashout, amt*cfg.get("pass_through_ratio", .9), 2)
    return pd.DataFrame(rows)


def generate(output_dir=None, n_rings=20, seed=42):
    base = Path(output_dir or Path(__file__).parent)
    world = build_world(seed=seed)
    definitions = json.loads((Path(__file__).parents[1] / "identify" / "attacks.json").read_text(encoding="utf-8"))
    mm = next(x for x in definitions["attacks"] if x["attack_id"] == "MM-001")
    attacks = [simulate_mm(world, v["variant_id"], v["simulation_config"], n_rings, seed+i)
               for i, v in enumerate(mm["variants"])]
    df = pd.concat([world["transfers"], *attacks], ignore_index=True)
    df["transfer_id"] = [f"SIM-{i:08d}" for i in range(len(df))]
    df["channel"] = "TRANSFER"
    df = df.sort_values(["timestamp", "transfer_id"], kind="stable")
    base.mkdir(parents=True, exist_ok=True)
    path = base / "mm_raw_dataset.csv"
    df.to_csv(path, index=False)
    report = {"rows": len(df), "fraud_rows": int(df.is_fraud.sum()),
              "fraud_ratio": float(df.is_fraud.mean()),
              "variants": df.loc[df.is_fraud, "variant_id"].value_counts().to_dict(),
              "legit_lookalike_rate": float((~df.is_fraud & (df.lookalike_type != "ordinary")).mean()),
              "amount_quantiles": {str(k): v for k, v in df.groupby("is_fraud").amount.quantile([.1,.5,.9]).items()},
              "warning": "Synthetic stress-test data; do not present its metrics as real-world accuracy."}
    (base / "mm_validation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return path, report


if __name__ == "__main__":
    generate()
