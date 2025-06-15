from ultimate_agent.ai.swarm import SwarmCoordinator


def test_swarm_majority():
    swarm = SwarmCoordinator()
    swarm.register_node("n1", task_fn=lambda d: 1)
    swarm.register_node("n2", task_fn=lambda d: 1)
    swarm.register_node("n3", weight=0.5, task_fn=lambda d: 0)

    result = swarm.coordinate_task("data")
    assert result["success"] is True
    assert result["participants"] == 3
    assert result["result"] == 1


def test_swarm_average():
    swarm = SwarmCoordinator()
    swarm.register_node("n1", weight=2.0, task_fn=lambda d: 2)
    swarm.register_node("n2", task_fn=lambda d: 4)

    result = swarm.coordinate_task(None)
    assert result["success"] is True
    assert abs(result["result"] - 2.6666) < 1e-3
