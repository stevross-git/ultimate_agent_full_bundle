"""Simplified hierarchical mesh network with bandwidth optimization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class MeshNode:
    node_id: str
    cluster_id: str
    bandwidth_mbps: float
    is_leader: bool = False


@dataclass
class MeshCluster:
    cluster_id: str
    nodes: Dict[str, MeshNode] = field(default_factory=dict)
    leader: MeshNode | None = None

    def add_node(self, node: MeshNode) -> None:
        self.nodes[node.node_id] = node
        if node.is_leader or self.leader is None:
            self.leader = node


@dataclass
class BackhaulLink:
    """Dedicated high-bandwidth, low-latency connection between clusters."""

    cluster_a: str
    cluster_b: str
    bandwidth_mbps: float = 1000.0
    latency_ms: float = 10.0


class HierarchicalMeshNetwork:
    """Coordinate nodes in a hierarchical mesh."""

    def __init__(self) -> None:
        self.nodes: Dict[str, MeshNode] = {}
        self.clusters: Dict[str, MeshCluster] = {}
        self.backhaul: Dict[Tuple[str, str], BackhaulLink] = {}

    def add_node(self, node_id: str, cluster_id: str,
                 bandwidth_mbps: float = 100.0, *, is_leader: bool = False) -> None:
        cluster = self.clusters.setdefault(cluster_id, MeshCluster(cluster_id))
        node = MeshNode(node_id, cluster_id, bandwidth_mbps, is_leader=is_leader)
        cluster.add_node(node)
        if is_leader:
            cluster.leader = node
        self.nodes[node_id] = node

    def rebalance_leaders(self) -> None:
        """Choose the highest-bandwidth node as leader in each cluster."""
        for cluster in self.clusters.values():
            best = max(cluster.nodes.values(), key=lambda n: n.bandwidth_mbps)
            cluster.leader = best
            best.is_leader = True

    def route_path(self, src_id: str, dst_id: str) -> List[str]:
        src = self.nodes[src_id]
        dst = self.nodes[dst_id]
        if src.cluster_id == dst.cluster_id:
            return [src_id, dst_id]
        src_leader = self.clusters[src.cluster_id].leader.node_id
        dst_leader = self.clusters[dst.cluster_id].leader.node_id
        path = [src_id]
        if src_id != src_leader:
            path.append(src_leader)
        if src_leader != dst_leader:
            path.append(dst_leader)
        if dst_id != dst_leader:
            path.append(dst_id)
        return path

    def estimate_transfer_time(self, src_id: str, dst_id: str,
                               size_mb: float, optimize: bool = False) -> float:
        path = self.route_path(src_id, dst_id)
        if optimize and size_mb >= 100:
            size_mb *= 0.5  # pretend compression for large transfers
        total = 0.0
        for a, b in zip(path, path[1:]):
            bw = min(self.nodes[a].bandwidth_mbps,
                     self.nodes[b].bandwidth_mbps)
            total += size_mb / (bw or 1.0)
        return total

    def broadcast(self, src_id: str, size_mb: float, optimize: bool = False) -> float:
        """Broadcast a payload to all other nodes, returning total estimated time."""
        total = 0.0
        for dst_id in self.nodes:
            if dst_id == src_id:
                continue
            total += self.estimate_transfer_time(src_id, dst_id, size_mb, optimize=optimize)
        return total

    # ------------------------------------------------------------------
    # Advanced features
    # ------------------------------------------------------------------

    def add_backhaul_link(self, cluster_a: str, cluster_b: str,
                          bandwidth_mbps: float = 1000.0,
                          latency_ms: float = 10.0) -> None:
        """Add a dedicated backhaul channel between two clusters."""
        key = tuple(sorted((cluster_a, cluster_b)))
        self.backhaul[key] = BackhaulLink(cluster_a, cluster_b,
                                         bandwidth_mbps=bandwidth_mbps,
                                         latency_ms=latency_ms)

    def estimate_latency(self, src_id: str, dst_id: str,
                         size_mb: float = 1.0) -> float:
        """Estimate latency in milliseconds for a transfer."""
        path = self.route_path(src_id, dst_id)
        total = 0.0
        for a, b in zip(path, path[1:]):
            a_cluster = self.nodes[a].cluster_id
            b_cluster = self.nodes[b].cluster_id
            if a_cluster != b_cluster:
                key = tuple(sorted((a_cluster, b_cluster)))
                link = self.backhaul.get(key)
                if link:
                    bw = link.bandwidth_mbps
                    total += link.latency_ms
                else:
                    bw = min(self.nodes[a].bandwidth_mbps,
                             self.nodes[b].bandwidth_mbps)
                    total += 80  # base inter-cluster delay
            else:
                bw = min(self.nodes[a].bandwidth_mbps,
                         self.nodes[b].bandwidth_mbps)
                total += 5  # base intra-cluster delay
            total += (size_mb / (bw or 1.0)) * 1000
        return total

    def optimize_topology(self, latency_threshold_ms: float = 100.0) -> None:
        """Ensure backhaul links between clusters to keep latency under threshold."""
        clusters = list(self.clusters.keys())
        for i, c1 in enumerate(clusters):
            for c2 in clusters[i + 1:]:
                leader_a = self.clusters[c1].leader.node_id
                leader_b = self.clusters[c2].leader.node_id
                if self.estimate_latency(leader_a, leader_b) > latency_threshold_ms:
                    self.add_backhaul_link(c1, c2)
