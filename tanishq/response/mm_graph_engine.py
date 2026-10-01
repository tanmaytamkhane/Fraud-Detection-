"""Transfer graph containing observed transfers only."""
import networkx as nx


class MMGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_transfer(self, transfer_id, sender, receiver, amount, risk_score, decision, timestamp=None, device_id=None):
        sender, receiver = str(sender), str(receiver)
        self.graph.add_node(sender)
        self.graph.add_node(receiver)
        old = self.graph.get_edge_data(sender, receiver, default={})
        self.graph.add_edge(sender, receiver, amount=float(old.get("amount", 0))+float(amount),
                            count=int(old.get("count", 0))+1, last_transfer_id=str(transfer_id),
                            last_timestamp=str(timestamp), decision=decision,
                            risk_score=max(float(old.get("risk_score", 0)), float(risk_score)))

    def get_network_risk(self, account, receiver=None):
        nodes = [str(x) for x in (account, receiver) if x is not None and str(x) in self.graph]
        if not nodes:
            return 0.0
        edges = set()
        for n in nodes:
            edges.update(self.graph.in_edges(n))
            edges.update(self.graph.out_edges(n))
        if not edges:
            return 0.0
        risks = [self.graph[u][v]["risk_score"] for u, v in edges]
        flagged = sum(self.graph[u][v]["decision"] in ("HOLD_TRANSFER", "BLOCK_CHAIN", "FREEZE_RECEIVER") for u, v in edges)
        return min(1.0, 0.6*sum(risks)/len(risks) + 0.4*flagged/len(edges))

    def get_mule_cluster(self, account, depth=2):
        account = str(account)
        if account not in self.graph:
            return {"found": False, "account": account, "nodes": [], "links": [], "rings": []}
        seen = {account}
        frontier = {account}
        for _ in range(depth):
            frontier = {v for n in frontier for v in set(self.graph.predecessors(n)) | set(self.graph.successors(n))} - seen
            seen |= frontier
        sub = self.graph.subgraph(seen)
        # SCCs prove observed directed cycles without enumerating exponentially many paths.
        cycles = [sorted(c) for c in nx.strongly_connected_components(sub) if len(c) > 1]
        return {"found": True, "account": account,
                "nodes": [{"id": n, "in_degree": sub.in_degree(n), "out_degree": sub.out_degree(n)} for n in sub],
                "links": [{"source": u, "target": v, **dict(d)} for u, v, d in sub.edges(data=True)],
                "rings": [{"ring_id": f"OBSERVED-{i+1}", "accounts": c[:20], "account_count": len(c)}
                          for i, c in enumerate(cycles[:20])]}
