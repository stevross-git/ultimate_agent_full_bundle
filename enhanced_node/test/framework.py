#!/usr/bin/env python3
"""
Comprehensive Testing Framework for Enhanced Node Server
Tests all modular components independently and together
"""

import unittest
import json
import tempfile
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.server import EnhancedNodeServer
from core.database import EnhancedNodeDatabase, Agent, AgentHeartbeat
from control.task_manager import TaskControlManager
from control.remote_manager import AdvancedRemoteControlManager
from models.agents import EnhancedAgentInfo, EnhancedAgentStatus
from models.tasks import CentralTask
from models.commands import AgentCommand
from models.scripts import ScheduledCommand, BulkOperation, AgentScript
from utils.serialization import serialize_for_json, DateTimeJSONEncoder
from config.settings import NODE_ID, NODE_VERSION


class TestDatabase(unittest.TestCase):
    """Test database operations and models"""
    
    def setUp(self):
        """Set up test database"""
        self.db = EnhancedNodeDatabase(":memory:")
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
    
    def test_database_initialization(self):
        """Test database initialization"""
        self.assertIsNotNone(self.db.engine)
        self.assertIsNotNone(self.db.session)
    
    def test_agent_creation(self):
        """Test agent creation and storage"""
        agent = Agent(
            id="test-agent-1",
            name="Test Agent",
            host="localhost",
            version="1.0.0",
            agent_type="ultimate",
            registered_at=datetime.now()
        )
        
        self.db.session.add(agent)
        self.db.session.commit()
        
        retrieved = self.db.get_agent_by_id("test-agent-1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test Agent")
    
    def test_heartbeat_storage(self):
        """Test heartbeat storage and retrieval"""
        # First create an agent
        agent = Agent(
            id="test-agent-1",
            name="Test Agent",
            host="localhost",
            version="1.0.0"
        )
        self.db.session.add(agent)
        self.db.session.commit()
        
        # Add heartbeat
        heartbeat = AgentHeartbeat(
            agent_id="test-agent-1",
            timestamp=datetime.now(),
            status="online",
            cpu_percent=50.0,
            memory_percent=60.0
        )
        
        self.db.session.add(heartbeat)
        self.db.session.commit()
        
        # Retrieve heartbeats
        heartbeats = self.db.get_recent_heartbeats("test-agent-1", 5)
        self.assertEqual(len(heartbeats), 1)
        self.assertEqual(heartbeats[0].status, "online")
    
    def test_cleanup_old_data(self):
        """Test old data cleanup"""
        # Add old heartbeat
        old_heartbeat = AgentHeartbeat(
            agent_id="test-agent-1",
            timestamp=datetime.now() - timedelta(days=40),
            status="online"
        )
        
        self.db.session.add(old_heartbeat)
        self.db.session.commit()
        
        # Cleanup
        self.db.cleanup_old_data(30)
        
        # Verify cleanup
        heartbeats = self.db.get_recent_heartbeats("test-agent-1", 10)
        self.assertEqual(len(heartbeats), 0)


class TestModels(unittest.TestCase):
    """Test data models and serialization"""
    
    def test_enhanced_agent_info(self):
        """Test EnhancedAgentInfo model"""
        agent = EnhancedAgentInfo(
            id="test-agent",
            name="Test Agent",
            host="localhost",
            version="1.0.0",
            capabilities=["ai", "blockchain"],
            ai_models=["gpt-3", "bert"]
        )
        
        self.assertEqual(agent.id, "test-agent")
        self.assertEqual(len(agent.capabilities), 2)
        self.assertEqual(len(agent.ai_models), 2)
    
    def test_enhanced_agent_status(self):
        """Test EnhancedAgentStatus model"""
        status = EnhancedAgentStatus(
            id="test-agent",
            status="online",
            cpu_percent=75.5,
            memory_percent=60.0,
            tasks_running=3
        )
        
        self.assertEqual(status.status, "online")
        self.assertEqual(status.cpu_percent, 75.5)
        self.assertEqual(status.tasks_running, 3)
    
    def test_central_task(self):
        """Test CentralTask model"""
        task = CentralTask(
            id="test-task-1",
            task_type="neural_network_training",
            priority=8,
            config={"epochs": 100}
        )
        
        self.assertEqual(task.task_type, "neural_network_training")
        self.assertEqual(task.priority, 8)
        self.assertIsNotNone(task.created_at)
        self.assertEqual(task.config["epochs"], 100)
    
    def test_agent_command(self):
        """Test AgentCommand model"""
        command = AgentCommand(
            id="cmd-1",
            agent_id="agent-1",
            command_type="restart_agent",
            parameters={"delay": 5}
        )
        
        self.assertEqual(command.command_type, "restart_agent")
        self.assertEqual(command.parameters["delay"], 5)
        self.assertEqual(command.status, "pending")
        self.assertIsNotNone(command.created_at)
    
    def test_serialization(self):
        """Test JSON serialization"""
        agent = EnhancedAgentInfo(
            id="test-agent",
            name="Test Agent",
            host="localhost",
            version="1.0.0",
            registered_at=datetime.now()
        )
        
        serialized = serialize_for_json(agent)
        self.assertIsInstance(serialized, dict)
        self.assertEqual(serialized["id"], "test-agent")
        self.assertIsInstance(serialized["registered_at"], str)


class TestTaskManager(unittest.TestCase):
    """Test TaskControlManager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_server = Mock()
        self.mock_server.agents = {}
        self.mock_server.running = True
        self.mock_server.socketio = Mock()
        self.mock_server.db = Mock()
        self.mock_server.db.session = Mock()
        
        self.task_manager = TaskControlManager(self.mock_server)
    
    def test_task_creation(self):
        """Test task creation"""
        task = self.task_manager.create_task("neural_network_training")
        
        self.assertIsNotNone(task)
        self.assertEqual(task.task_type, "neural_network_training")
        self.assertIsNotNone(task.id)
        self.assertEqual(task.priority, 8)  # From template
    
    def test_task_assignment(self):
        """Test task assignment to agent"""
        task = self.task_manager.create_task("data_processing")
        agent_id = "test-agent-1"
        
        # Mock agent exists
        self.mock_server.agents[agent_id] = Mock()
        
        self.task_manager.assign_task_to_agent(task, agent_id)
        
        self.assertEqual(task.assigned_agent, agent_id)
        self.assertEqual(task.status, "assigned")
        self.assertIsNotNone(task.assigned_at)
        self.assertIn(task.id, self.task_manager.running_tasks)
    
    def test_task_completion(self):
        """Test task completion handling"""
        task = self.task_manager.create_task("sentiment_analysis")
        task_id = task.id
        agent_id = "test-agent-1"
        
        # Add to running tasks
        self.task_manager.running_tasks[task_id] = task
        
        # Complete task
        result = {"accuracy": 0.95, "sentiment": "positive"}
        self.task_manager.handle_task_completion(task_id, agent_id, True, result)
        
        self.assertEqual(task.status, "completed")
        self.assertEqual(task.progress, 100.0)
        self.assertEqual(task.result["accuracy"], 0.95)
        self.assertIn(task_id, self.task_manager.completed_tasks)
        self.assertNotIn(task_id, self.task_manager.running_tasks)
    
    def test_task_statistics(self):
        """Test task statistics calculation"""
        # Add some test data
        self.task_manager.task_metrics = {
            "total_assigned": 10,
            "total_completed": 8,
            "total_failed": 2,
            "success_rate": 80.0
        }
        
        stats = self.task_manager.get_task_statistics()
        
        self.assertEqual(stats["total_completed"], 8)
        self.assertEqual(stats["total_failed"], 2)
        self.assertEqual(stats["success_rate"], 80.0)


class TestRemoteManager(unittest.TestCase):
    """Test AdvancedRemoteControlManager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_server = Mock()
        self.mock_server.agents = {"agent-1": Mock(), "agent-2": Mock()}
        self.mock_server.agent_status = {
            "agent-1": EnhancedAgentStatus(
                id="agent-1",
                status="online",
                cpu_percent=50.0,
                memory_percent=60.0,
                last_heartbeat=datetime.now()
            )
        }
        self.mock_server.socketio = Mock()
        self.mock_server.db = Mock()
        self.mock_server.db.session = Mock()
        self.mock_server.logger = Mock()
        
        self.remote_manager = AdvancedRemoteControlManager(self.mock_server)
    
    def test_command_creation(self):
        """Test agent command creation"""
        command = self.remote_manager.create_agent_command(
            "agent-1", 
            "restart_agent", 
            {"delay": 5}
        )
        
        self.assertIsNotNone(command)
        self.assertEqual(command.agent_id, "agent-1")
        self.assertEqual(command.command_type, "restart_agent")
        self.assertEqual(command.parameters["delay"], 5)
        self.assertIn(command.id, self.remote_manager.active_commands)
    
    def test_bulk_operation_creation(self):
        """Test bulk operation creation"""
        target_agents = ["agent-1", "agent-2"]
        bulk_op = self.remote_manager.create_bulk_operation(
            "restart_agent",
            target_agents,
            {"delay": 10}
        )
        
        self.assertIsNotNone(bulk_op)
        self.assertEqual(bulk_op.operation_type, "restart_agent")
        self.assertEqual(bulk_op.target_agents, target_agents)
        self.assertEqual(bulk_op.parameters["delay"], 10)
        self.assertIn(bulk_op.id, self.remote_manager.bulk_operations)
    
    def test_scheduled_command_creation(self):
        """Test scheduled command creation"""
        future_time = datetime.now() + timedelta(hours=1)
        scheduled_cmd = self.remote_manager.create_scheduled_command(
            "agent-1",
            "backup_data",
            future_time,
            {"path": "/data"},
            repeat_interval=3600,
            max_repeats=5
        )
        
        self.assertIsNotNone(scheduled_cmd)
        self.assertEqual(scheduled_cmd.command.agent_id, "agent-1")
        self.assertEqual(scheduled_cmd.command.command_type, "backup_data")
        self.assertEqual(scheduled_cmd.scheduled_time, future_time)
        self.assertEqual(scheduled_cmd.repeat_interval, 3600)
        self.assertEqual(scheduled_cmd.max_repeats, 5)
    
    def test_health_check(self):
        """Test agent health check"""
        agent_status = self.mock_server.agent_status["agent-1"]
        health_check = self.remote_manager.perform_health_check("agent-1", agent_status)
        
        self.assertIsNotNone(health_check)
        self.assertEqual(health_check.agent_id, "agent-1")
        self.assertIn(health_check.status, ["healthy", "warning", "critical", "offline"])
        self.assertIsInstance(health_check.health_score, float)
    
    def test_script_deployment(self):
        """Test script deployment"""
        script = AgentScript(
            id="script-1",
            name="test_script",
            version="1.0",
            script_type="python",
            script_content="print('Hello World')",
            checksum="abc123",
            target_agents=["agent-1"]
        )
        
        self.remote_manager.agent_scripts[script.id] = script
        
        # Mock successful deployment
        with patch.object(self.remote_manager, 'execute_command_on_agent', return_value=True):
            success = self.remote_manager.deploy_script_to_agent("agent-1", script)
        
        self.assertTrue(success)
        self.assertEqual(script.deployment_results["agent-1"]["status"], "deployed")
    
    def test_command_history(self):
        """Test command history tracking"""
        # Create some commands
        for i in range(3):
            command = self.remote_manager.create_agent_command(
                "agent-1",
                f"command_{i}",
                {"param": i}
            )
        
        history = self.remote_manager.get_command_history("agent-1", 5)
        
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["command_type"], "command_0")
    
    def test_advanced_statistics(self):
        """Test advanced statistics calculation"""
        # Add some test data
        self.remote_manager.command_history["agent-1"] = [Mock(), Mock(), Mock()]
        self.remote_manager.active_commands = {"cmd-1": Mock()}
        self.remote_manager.scheduled_commands = {"sched-1": Mock()}
        self.remote_manager.bulk_operations = {"bulk-1": Mock()}
        self.remote_manager.agent_scripts = {"script-1": Mock()}
        
        stats = self.remote_manager.get_advanced_statistics()
        
        self.assertEqual(stats["total_commands_executed"], 3)
        self.assertEqual(stats["active_commands"], 1)
        self.assertEqual(stats["scheduled_commands"], 0)  # Only scheduled status counted
        self.assertEqual(stats["bulk_operations"], 1)
        self.assertEqual(stats["agent_scripts"], 1)


class TestEnhancedNodeServer(unittest.TestCase):
    """Test main server functionality"""
    
    def setUp(self):
        """Set up test server"""
        with patch('core.server.EnhancedNodeDatabase'):
            self.server = EnhancedNodeServer()
    
    def test_server_initialization(self):
        """Test server initialization"""
        self.assertIsNotNone(self.server.app)
        self.assertIsNotNone(self.server.socketio)
        self.assertIsNotNone(self.server.task_control)
        self.assertIsNotNone(self.server.advanced_remote_control)
        self.assertEqual(len(self.server.agents), 0)
    
    def test_agent_registration(self):
        """Test agent registration"""
        agent_data = {
            "agent_id": "test-agent-1",
            "name": "Test Agent",
            "host": "localhost",
            "version": "1.0.0",
            "agent_type": "ultimate",
            "capabilities": ["ai", "blockchain"],
            "gpu_available": True
        }
        
        result = self.server.register_agent(agent_data)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["agent_id"], "test-agent-1")
        self.assertIn("test-agent-1", self.server.agents)
        self.assertIn("test-agent-1", self.server.agent_status)
    
    def test_heartbeat_processing(self):
        """Test heartbeat processing"""
        # First register an agent
        agent_data = {
            "agent_id": "test-agent-1",
            "name": "Test Agent",
            "host": "localhost",
            "version": "1.0.0"
        }
        self.server.register_agent(agent_data)
        
        # Send heartbeat
        heartbeat_data = {
            "agent_id": "test-agent-1",
            "status": "online",
            "cpu_percent": 75.0,
            "memory_percent": 60.0,
            "tasks_running": 2,
            "tasks_completed": 5
        }
        
        result = self.server.process_agent_heartbeat(heartbeat_data)
        
        self.assertTrue(result["success"])
        
        # Check status update
        status = self.server.agent_status["test-agent-1"]
        self.assertEqual(status.status, "online")
        self.assertEqual(status.cpu_percent, 75.0)
        self.assertEqual(status.tasks_running, 2)
    
    def test_enhanced_node_stats(self):
        """Test node statistics calculation"""
        # Add test agent
        self.server.agents["agent-1"] = EnhancedAgentInfo(
            id="agent-1",
            name="Test Agent",
            host="localhost",
            version="1.0.0"
        )
        
        self.server.agent_status["agent-1"] = EnhancedAgentStatus(
            id="agent-1",
            status="online",
            cpu_percent=50.0,
            memory_percent=60.0,
            tasks_running=2,
            tasks_completed=10,
            ai_models_loaded=3,
            blockchain_balance=1.5,
            efficiency_score=85.0,
            last_heartbeat=datetime.now()
        )
        
        stats = self.server.get_enhanced_node_stats()
        
        self.assertEqual(stats["total_agents"], 1)
        self.assertEqual(stats["online_agents"], 1)
        self.assertEqual(stats["total_tasks_running"], 2)
        self.assertEqual(stats["total_ai_models"], 3)
        self.assertEqual(stats["avg_efficiency_score"], 85.0)
        self.assertIn("node_id", stats)
        self.assertIn("node_version", stats)


class TestAPIRoutes(unittest.TestCase):
    """Test API route functionality"""
    
    def setUp(self):
        """Set up test client"""
        with patch('core.server.EnhancedNodeDatabase'):
            self.server = EnhancedNodeServer()
            
        # Import and register routes
        from routes.api_v3 import register_api_v3_routes
        from routes.api_v5_remote import register_api_v5_routes
        
        register_api_v3_routes(self.server)
        register_api_v5_routes(self.server)
        
        self.client = self.server.app.test_client()
    
    def test_dashboard_route(self):
        """Test dashboard route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Enhanced Node Server', response.data)
    
    def test_agent_registration_api(self):
        """Test agent registration API"""
        agent_data = {
            "agent_id": "test-agent-1",
            "name": "Test Agent",
            "host": "localhost",
            "version": "1.0.0",
            "agent_type": "ultimate"
        }
        
        response = self.client.post(
            '/api/v3/agents/register',
            data=json.dumps(agent_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["agent_id"], "test-agent-1")
    
    def test_heartbeat_api(self):
        """Test heartbeat API"""
        # First register agent
        self.server.register_agent({
            "agent_id": "test-agent-1",
            "name": "Test Agent",
            "host": "localhost",
            "version": "1.0.0"
        })
        
        heartbeat_data = {
            "agent_id": "test-agent-1",
            "status": "online",
            "cpu_percent": 75.0,
            "memory_percent": 60.0
        }
        
        response = self.client.post(
            '/api/v3/agents/heartbeat',
            data=json.dumps(heartbeat_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
    
    def test_get_agents_api(self):
        """Test get agents API"""
        response = self.client.get('/api/v3/agents')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("agents", data)
        self.assertIn("stats", data)


class TestUtilities(unittest.TestCase):
    """Test utility functions"""
    
    def test_datetime_json_encoder(self):
        """Test datetime JSON encoder"""
        test_data = {
            "timestamp": datetime.now(),
            "name": "test",
            "value": 123
        }
        
        json_str = json.dumps(test_data, cls=DateTimeJSONEncoder)
        self.assertIsInstance(json_str, str)
        
        # Parse back
        parsed = json.loads(json_str)
        self.assertIn("timestamp", parsed)
        self.assertEqual(parsed["name"], "test")
    
    def test_serialize_for_json(self):
        """Test serialize_for_json function"""
        test_obj = EnhancedAgentInfo(
            id="test",
            name="Test Agent",
            host="localhost",
            version="1.0.0",
            registered_at=datetime.now()
        )
        
        serialized = serialize_for_json(test_obj)
        
        self.assertIsInstance(serialized, dict)
        self.assertEqual(serialized["id"], "test")
        self.assertIsInstance(serialized["registered_at"], str)


def run_all_tests():
    """Run all test suites"""
    print("🧪 Running Enhanced Node Server Test Suite")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_cases = [
        TestDatabase,
        TestModels,
        TestTaskManager,
        TestRemoteManager,
        TestEnhancedNodeServer,
        TestAPIRoutes,
        TestUtilities
    ]
    
    for test_case in test_cases:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_case)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
