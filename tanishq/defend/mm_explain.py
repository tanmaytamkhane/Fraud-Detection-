"""Conservative MM explanations: only describe observed signals, never infer crime."""

LABELS = {
    "fan_out_degree": "Recent outgoing counterparty breadth",
    "fan_in_degree": "Recent incoming counterparty breadth",
    "transit_velocity_sec": "Fast pass-through relative to configured time window",
    "amount_layering_ratio": "Recent outbound-to-inbound amount ratio",
    "shared_device_cluster": "Accounts sharing an observed device",
    "account_dormancy_score": "Activity gap relative to configured dormancy window",
}


def explain(signals, available=None):
    available = set(available or LABELS)
    ranked = sorted(((k, float(v)) for k, v in signals.items() if k in available),
                    key=lambda x: x[1], reverse=True)
    relevant = [(k, v) for k, v in ranked if v >= .5][:3]
    if not relevant:
        return "No strong money movement signal in the available history."
    return "; ".join(f"{LABELS[k]} scored {v:.2f}" for k, v in relevant) + "."
