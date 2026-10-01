"""Generate schema fixtures only; their labels are contrived and are not benchmarks."""
import csv
import json
from pathlib import Path
import numpy as np
from pipeline.mm_loader import probe


def generate(directory=None, seed=42):
    root = Path(directory or Path(__file__).parent)
    root.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    pay = root / "paysim_like.csv"
    ibm = root / "ibm_like.csv"
    with pay.open("w", newline="") as f1, ibm.open("w", newline="") as f2:
        p = csv.writer(f1)
        b = csv.writer(f2)
        p.writerow(["step", "type", "amount", "nameOrig", "oldbalanceOrg", "newbalanceOrig", "nameDest", "oldbalanceDest", "newbalanceDest", "isFraud"])
        b.writerow(["Timestamp", "From Bank", "Account", "To Bank", "Account.1", "Amount Received", "Receiving Currency", "Payment Format", "Is Laundering"])
        for step in range(200):
            for j in range(20):
                fraud = j == 0 and step % 5 == 0
                sender = f"A{int(rng.integers(0, 200)):03d}"
                receiver = "HUB" if fraud else f"A{int(rng.integers(0, 200)):03d}"
                amount = round(float(rng.lognormal(4 if fraud else 4.5, .6)), 2)
                p.writerow([step, "TRANSFER", amount, sender, 1000, 1000-amount, receiver, 0, amount, int(fraud)])
                b.writerow([f"2025-01-{step//24+1:02d} {step%24:02d}:00:00", 1, sender, 1, receiver,
                            amount, "USD", "ACH", int(fraud)])
    base = json.loads((Path(__file__).parents[2] / "mm_config.json").read_text())
    for path, name, time_unit in ((pay, "paysim", "steps"), (ibm, "ibm", "ISO string")):
        cfg = dict(base)
        cfg["column_map"] = probe(path)["candidate_column_map"]
        cfg["time_unit"] = time_unit
        cfg["seconds_per_step"] = 3600 if name == "paysim" else None
        cfg["short_window_sec"] = 3600
        cfg["long_window_days"] = 1
        cfg["dormancy_days"] = 2
        cfg["model_dir"] = f"models/fixture_{name}"
        cfg["results_path"] = f"results/mm_fixture_{name}_results.json"
        (root / f"{name}_config.json").write_text(json.dumps(cfg, indent=2))
    return pay, ibm


if __name__ == "__main__":
    print(*generate())
