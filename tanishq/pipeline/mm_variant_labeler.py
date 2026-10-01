"""Prototype-distance MM typology hint, never a verified fraud label."""
import json
from pathlib import Path
import numpy as np
from pipeline.mm_feature_engineer import SIGNALS

_catalog = json.loads((Path(__file__).parents[1] / "identify" / "attacks.json").read_text(encoding="utf-8"))
_variants = next(a for a in _catalog["attacks"] if a["attack_id"] == "MM-001")["variants"]


def label_variant(signals, known_variant=None, available=None):
    if known_variant:
        return {"variant_id": known_variant, "source": "provided_ground_truth"}
    keys = [k for k in (available or SIGNALS) if k in SIGNALS]
    if not keys:
        return {"variant_id": None, "source": "insufficient_signals"}
    v = min(_variants, key=lambda item: np.mean([(float(signals.get(k, 0)) -
                    float(item["active_signals"].get(k, 0)))**2 for k in keys]))
    return {"variant_id": v["variant_id"], "variant_name": v["name"],
            "source": "unvalidated_prototype_hint"}
