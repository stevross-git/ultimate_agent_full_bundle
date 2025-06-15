from ultimate_agent.network.mesh import HierarchicalMeshNetwork


def test_intra_cluster_route():
    mesh = HierarchicalMeshNetwork()
    mesh.add_node("a", "c1", bandwidth_mbps=100.0, is_leader=True)
    mesh.add_node("b", "c1", bandwidth_mbps=50.0)

    assert mesh.route_path("b", "a") == ["b", "a"]
    time_normal = mesh.estimate_transfer_time("b", "a", 100)
    assert abs(time_normal - 2.0) < 1e-6


def test_inter_cluster_bandwidth_opt():
    mesh = HierarchicalMeshNetwork()
    mesh.add_node("a", "c1", bandwidth_mbps=100.0, is_leader=True)
    mesh.add_node("b", "c1", bandwidth_mbps=50.0)
    mesh.add_node("c", "c2", bandwidth_mbps=80.0, is_leader=True)
    mesh.add_node("d", "c2", bandwidth_mbps=40.0)

    assert mesh.route_path("b", "d") == ["b", "a", "c", "d"]
    normal = mesh.estimate_transfer_time("b", "d", 200)
    optimized = mesh.estimate_transfer_time("b", "d", 200, optimize=True)
    assert optimized < normal


def test_rebalance_and_broadcast():
    mesh = HierarchicalMeshNetwork()
    mesh.add_node("a", "c1", bandwidth_mbps=50.0)
    mesh.add_node("b", "c1", bandwidth_mbps=120.0)
    mesh.add_node("c", "c2", bandwidth_mbps=30.0)
    mesh.add_node("d", "c2", bandwidth_mbps=90.0)
    mesh.rebalance_leaders()

    assert mesh.clusters["c1"].leader.node_id == "b"
    assert mesh.clusters["c2"].leader.node_id == "d"

    total = mesh.broadcast("b", 100)
    assert total > 0
