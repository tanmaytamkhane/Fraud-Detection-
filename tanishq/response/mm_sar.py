"""Evidence-only suspicious activity report draft for human compliance review."""


def generate_sar_narrative(case):
    parts = []
    if case.get("sender") and case.get("receiver"):
        parts.append(f"Transfer {case.get('transfer_id', 'unknown')} moved funds from account {case['sender']} to account {case['receiver']}")
    if case.get("amount") is not None:
        parts.append(f"for amount {case['amount']}")
    if case.get("timestamp") is not None:
        parts.append(f"at {case['timestamp']}")
    factual = " ".join(parts).strip()
    pattern = case.get("explanation") or "The available evidence requires analyst review."
    action = case.get("action", "REVIEW")
    return f"Draft for compliance review: {factual}. Observed indicators: {pattern} Proposed action: {action}. Confirm account ownership, funds origin, and supporting records before filing."
