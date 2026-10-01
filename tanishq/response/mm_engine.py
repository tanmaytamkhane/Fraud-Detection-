"""Money movement actions using ResponseEngine's five risk tiers."""
from response.engine import ResponseEngine


class MMResponseEngine:
    def __init__(self):
        self.base = ResponseEngine()
        self.audit = []

    def execute_action(self, transfer_id, risk_score, network_risk=0.0, variant_id=None, graph_context=None, explanation=""):
        d = self.base.decide_action(risk_score, variant_id, network_risk)
        tier = d["action"]
        mapped = {"BLOCK": "FREEZE_RECEIVER", "HOLD": "HOLD_TRANSFER",
                  "STEP_UP_AUTH": "STEP_UP_AUTH", "REVIEW": "REVIEW", "APPROVE": "APPROVE"}[tier]
        if tier == "BLOCK" and graph_context and graph_context.get("rings"):
            mapped = "BLOCK_CHAIN"
            d["downstream_accounts"] = sorted({a for r in graph_context["rings"] for a in r["accounts"]})
        d.update(transaction_id=str(transfer_id), tier=tier, action=mapped,
                 explanation=explanation, graph_context=graph_context or {"found": False})
        self.audit.append(d)
        return d
