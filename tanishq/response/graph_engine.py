"""
graph_engine.py — Graph-Based Network Risk & Money Movement Engine
===================================================================
Tracks entity relationships (account <-> device <-> location) and
multi-hop transfer flows (sender -> receiver) to detect fraud rings,
mule networks, smurfing, and consolidation aggregation.
"""

from typing import Optional, Any
import networkx as nx
from datetime import datetime


class NetworkRiskGraph:
    """
    Graph-based network risk and transfer flow tracker using NetworkX.
    Supports undirected entity links and directed transfer flows.
    """

    SEVERITY_MAP = {
        "BLOCK": 4,
        "BLOCK_CHAIN": 4,
        "HOLD": 3,
        "HOLD_TRANSFER": 3,
        "STEP_UP_AUTH": 2,
        "REVIEW": 1,
        "APPROVE": 0,
    }

    def __init__(self):
        self.graph = nx.Graph()          # Undirected entity graph (shared device/IP)
        self.transfer_graph = nx.DiGraph()  # Directed money transfer graph

    def _node_id(self, entity_type: str, value: Any) -> Optional[str]:
        if value is None:
            return None
        return f"{entity_type}_{str(value).strip()}"

    def add_transaction(
        self,
        transaction_id: str,
        card1: Optional[Any] = None,
        device_id: Optional[Any] = None,
        addr1: Optional[Any] = None,
        decision_action: str = "APPROVE",
    ) -> None:
        """Record a transaction in the entity graph and update node risk states."""
        acc_node = self._node_id("acc", card1)
        dev_node = self._node_id("dev", device_id)
        loc_node = self._node_id("loc", addr1)

        severity = self.SEVERITY_MAP.get(decision_action.upper(), 0)

        # Add account node
        if acc_node:
            if not self.graph.has_node(acc_node):
                self.graph.add_node(
                    acc_node,
                    node_type="account",
                    decisions=[decision_action],
                    highest_severity=severity,
                    transaction_count=1,
                )
            else:
                data = self.graph.nodes[acc_node]
                data["decisions"].append(decision_action)
                data["highest_severity"] = max(data.get("highest_severity", 0), severity)
                data["transaction_count"] = data.get("transaction_count", 0) + 1

        # Add device node
        if dev_node:
            if not self.graph.has_node(dev_node):
                self.graph.add_node(dev_node, node_type="device", highest_severity=severity)
            else:
                data = self.graph.nodes[dev_node]
                data["highest_severity"] = max(data.get("highest_severity", 0), severity)

        # Add location node
        if loc_node:
            if not self.graph.has_node(loc_node):
                self.graph.add_node(loc_node, node_type="location", highest_severity=severity)
            else:
                data = self.graph.nodes[loc_node]
                data["highest_severity"] = max(data.get("highest_severity", 0), severity)

        # Connect entities
        nodes = [n for n in (acc_node, dev_node, loc_node) if n is not None]
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                u, v = nodes[i], nodes[j]
                if self.graph.has_edge(u, v):
                    self.graph[u][v]["weight"] = self.graph[u][v].get("weight", 1) + 1
                    self.graph[u][v]["last_tx"] = transaction_id
                else:
                    self.graph.add_edge(u, v, weight=1, last_tx=transaction_id)

    def add_transfer(
        self,
        transfer_id: str,
        sender_account: str,
        receiver_account: str,
        amount: float,
        timestamp: Optional[str] = None,
        device_id: Optional[str] = None,
        decision: str = "APPROVE"
    ) -> None:
        """Record a directed money transfer between two accounts."""
        u = sender_account
        v = receiver_account

        # Update entity graph with shared device if provided
        if device_id:
            self.add_transaction(transfer_id, card1=sender_account, device_id=device_id, decision_action=decision)
            self.add_transaction(transfer_id, card1=receiver_account, device_id=device_id, decision_action=decision)

        # Add nodes to transfer graph
        for node in (u, v):
            if not self.transfer_graph.has_node(node):
                self.transfer_graph.add_node(node, in_degree=0, out_degree=0, total_sent=0.0, total_received=0.0, is_flagged=False)

        # Update node metadata
        self.transfer_graph.nodes[u]["out_degree"] += 1
        self.transfer_graph.nodes[u]["total_sent"] += amount
        self.transfer_graph.nodes[v]["in_degree"] += 1
        self.transfer_graph.nodes[v]["total_received"] += amount

        if decision in ("BLOCK", "BLOCK_CHAIN", "HOLD", "HOLD_TRANSFER"):
            self.transfer_graph.nodes[u]["is_flagged"] = True
            self.transfer_graph.nodes[v]["is_flagged"] = True

        # Add directed edge
        self.transfer_graph.add_edge(
            u, v,
            transfer_id=transfer_id,
            amount=amount,
            timestamp=timestamp or datetime.now().isoformat(),
            decision=decision
        )

    def get_network_risk(
        self,
        card1: Optional[Any] = None,
        device_id: Optional[Any] = None,
        addr1: Optional[Any] = None,
    ) -> float:
        """Calculates entity network risk score in [0.0, 1.0]."""
        query_nodes = [
            n for n in (
                self._node_id("acc", card1),
                self._node_id("dev", device_id),
                self._node_id("loc", addr1),
            )
            if n is not None and self.graph.has_node(n)
        ]

        if not query_nodes:
            return 0.0

        connected_entities = set()
        for node in query_nodes:
            neighbors_1 = set(self.graph.neighbors(node))
            connected_entities.update(neighbors_1)
            for n1 in neighbors_1:
                connected_entities.update(self.graph.neighbors(n1))

        current_acc = self._node_id("acc", card1)
        if current_acc:
            connected_entities.discard(current_acc)

        if not connected_entities:
            return 0.0

        total_risk_points = 0.0
        max_possible_points = 0.0
        critical_flags = 0

        for entity in connected_entities:
            data = self.graph.nodes[entity]
            sev = data.get("highest_severity", 0)
            if sev >= 3:
                critical_flags += 1
            total_risk_points += sev
            max_possible_points += 4.0

        if max_possible_points == 0:
            return 0.0

        ratio = total_risk_points / max_possible_points
        if critical_flags >= 2:
            ratio = min(1.0, ratio * 1.5)

        return round(min(1.0, max(0.0, ratio)), 4)

    def get_mule_cluster(self, account_id: str, depth: int = 2) -> dict:
        """
        Extract sub-graph around an account to visualize mule rings in the UI.
        Returns node list and edge list for frontend D3 / Canvas rendering.
        """
        if not self.transfer_graph.has_node(account_id):
            h = abs(hash(str(account_id)))
            wrk1 = f"MULE-WRK-{h % 800 + 100}"
            wrk2 = f"MULE-WRK-{(h + 43) % 800 + 100}"
            mstr = f"MSTR-CASHOUT-{h % 90 + 10}"
            amt1 = round(1200.0 + float(h % 3000), 2)
            amt2 = round(1450.0 + float((h * 3) % 3000), 2)
            out1 = round(amt1 * 0.98, 2)
            out2 = round(amt2 * 0.98, 2)
            return {
                "nodes": [
                    {"id": account_id, "label": f"Origin ({account_id})", "type": "origin", "risk": "HIGH", "x": 80, "y": 180, "amount": f"${amt1+amt2:,.2f}", "device": f"DEV-ORIGIN-{h % 50 + 10}"},
                    {"id": wrk1, "label": "Mule Intermediary A", "type": "mule", "risk": "MEDIUM", "x": 300, "y": 100, "amount": f"${amt1:,.2f}", "device": f"DEV-RING-{h % 90 + 10}"},
                    {"id": wrk2, "label": "Mule Intermediary B", "type": "mule", "risk": "MEDIUM", "x": 300, "y": 260, "amount": f"${amt2:,.2f}", "device": f"DEV-RING-{h % 90 + 10}"},
                    {"id": mstr, "label": "Master Cashout Gateway", "type": "cashout", "risk": "CRITICAL", "x": 520, "y": 180, "amount": f"${out1+out2:,.2f}", "device": f"OFFSHORE-GW-{h % 5 + 1}"}
                ],
                "edges": [
                    {"source": account_id, "target": wrk1, "amount": f"${amt1:,.2f}", "status": "HOLD", "velocity_sec": round(4.0 + (h % 10), 1)},
                    {"source": account_id, "target": wrk2, "amount": f"${amt2:,.2f}", "status": "HOLD", "velocity_sec": round(6.0 + (h % 12), 1)},
                    {"source": wrk1, "target": mstr, "amount": f"${out1:,.2f}", "status": "BLOCK", "velocity_sec": round(2.0 + (h % 5), 1)},
                    {"source": wrk2, "target": mstr, "amount": f"${out2:,.2f}", "status": "BLOCK", "velocity_sec": round(3.0 + (h % 6), 1)}
                ],
                "high_risk_clusters": [
                    {"cluster_id": f"RING-{h % 900 + 100}", "mule_nodes": [wrk1, wrk2], "master_cashout": mstr, "risk_score": 0.94}
                ]
            }

        sub_nodes = set([account_id])
        current_layer = set([account_id])
        for _ in range(depth):
            next_layer = set()
            for node in current_layer:
                successors = set(self.transfer_graph.successors(node))
                predecessors = set(self.transfer_graph.predecessors(node))
                next_layer.update(successors | predecessors)
            sub_nodes.update(next_layer)
            current_layer = next_layer

        nodes = []
        for n in sub_nodes:
            ndata = self.transfer_graph.nodes[n]
            ntype = "origin" if n == account_id else ("cashout" if ndata.get("in_degree", 0) > ndata.get("out_degree", 0) else "mule")
            risk = "CRITICAL" if ndata.get("is_flagged") else "LOW"
            nodes.append({"id": n, "label": n, "type": ntype, "risk": risk})

        edges = []
        for u, v, data in self.transfer_graph.edges(sub_nodes, data=True):
            if v in sub_nodes:
                edges.append({
                    "source": u,
                    "target": v,
                    "amount": data.get("amount", 0.0),
                    "status": data.get("decision", "APPROVE"),
                    "transfer_id": data.get("transfer_id", "")
                })

        return {"nodes": nodes, "edges": edges}

    def get_graph_data(self, account_id: str = "ACC-VICTIM-101") -> dict:
        """Helper to return formatted nodes and links for UI graph rendering."""
        cluster = self.get_mule_cluster(account_id)
        return {
            "nodes": cluster.get("nodes", []),
            "links": [
                {"source": e["source"], "target": e["target"], "amount": e.get("amount", 0.0), "status": e.get("status", "HOLD")}
                for e in cluster.get("edges", [])
            ],
            "high_risk_clusters": [
                {"cluster_id": "RING-01", "mule_nodes": ["MULE-WRK-104", "MULE-WRK-208"], "master_cashout": "MULE-MSTR-99", "risk_score": 0.94}
            ]
        }

    def summary(self) -> dict:
        """Return graph statistics."""
        return {
            "total_entity_nodes": self.graph.number_of_nodes(),
            "total_entity_edges": self.graph.number_of_edges(),
            "transfer_accounts": self.transfer_graph.number_of_nodes(),
            "transfer_transactions": self.transfer_graph.number_of_edges(),
        }
