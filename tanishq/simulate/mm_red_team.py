"""Raw-event evasion sweep against the synthetic MM model.

Evasion e in [0,1] changes generation knobs: dwell' = round(dwell*(1+4e)),
shared_device_prob' = original*(1-e), pass_through_ratio' =
original*(1-0.2e), n_receivers' = max(1, round(original*(1-e/2))).
It does not alter detector thresholds. The result tests simulator robustness only.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from defend.mm_scanner import UnifiedMMScanner
from simulate.mm_world import build_world
from simulate.mm_simulator import simulate_mm


ROOT = Path(__file__).parents[1]


def run_mm_red_team(variants=None, n_attempts_per_variant=50, evasion_levels=(0, .25, .5, .75, 1), seed=42):
    definitions = json.loads((ROOT / "identify" / "attacks.json").read_text(encoding="utf-8"))
    mm = next(x for x in definitions["attacks"] if x["attack_id"] == "MM-001")
    selected = [v for v in mm["variants"] if variants is None or v["variant_id"] in variants]
    table = []
    for level in evasion_levels:
        world = build_world(n_accounts=200, n_steps=80, seed=seed)
        attacks = []
        for i, v in enumerate(selected):
            knobs = dict(v["simulation_config"])
            knobs["dwell_steps"] = round(knobs.get("dwell_steps", 1)*(1+4*level))
            knobs["shared_device_prob"] = knobs.get("shared_device_prob", 0)*(1-level)
            knobs["pass_through_ratio"] = knobs.get("pass_through_ratio", .9)*(1-.2*level)
            knobs["n_receivers"] = max(1, round(knobs.get("n_receivers", 1)*(1-level/2)))
            attacks.append(simulate_mm(world, v["variant_id"], knobs, n_attempts_per_variant, seed+i))
        d = pd.concat([world["transfers"], *attacks], ignore_index=True)
        d["transfer_id"] = [f"RED-{j}" for j in range(len(d))]
        d = d.sort_values(["timestamp", "transfer_id"], kind="stable")
        scanner = UnifiedMMScanner(ROOT / "mm_synthetic_config.json")
        rings = {}
        for row in d.itertuples(index=False):
            result = scanner.scan_transfer(str(row.transfer_id), float(row.timestamp),
                str(row.sender), str(row.receiver), float(row.amount), str(row.device_id))
            if row.is_fraud:
                record = rings.setdefault(row.ring_id, {"variant": row.variant_id, "risks": [], "effective": [], "actions": []})
                record["risks"].append(result["risk_score"])
                record["effective"].append(result["decision"]["effective_risk"])
                record["actions"].append(result["decision"]["action"])
        for variant in [v["variant_id"] for v in selected]:
            cases = [r for r in rings.values() if r["variant"] == variant]
            evaded = [r for r in cases if all(a in ("APPROVE", "REVIEW") for a in r["actions"])]
            table.append({"variant": variant, "evasion_level": level, "rings": len(cases),
                          "evasion_rate": len(evaded)/max(1, len(cases)),
                          "mean_peak_risk": sum(max(r["risks"]) for r in cases)/max(1, len(cases)),
                          "actions": {a: sum(a in r["actions"] for r in cases) for a in
                                      ("APPROVE", "REVIEW", "STEP_UP_AUTH", "HOLD_TRANSFER", "FREEZE_RECEIVER", "BLOCK_CHAIN")}})
    report = {"source": "synthetic attack injection and synthetic MM model",
              "warning": "Not a real-world evasion estimate; no adversarial retraining is performed.", "table": table}
    out = ROOT / "results" / "mm_red_team.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempts", type=int, default=50)
    ap.add_argument("--variants", nargs="*")
    args = ap.parse_args()
    run_mm_red_team(args.variants, args.attempts)
