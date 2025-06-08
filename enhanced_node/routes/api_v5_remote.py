#!/usr/bin/env python3
"""
API v5 Remote Routes - Advanced Remote Control Features
"""

from flask import request, jsonify
from datetime import datetime
import uuid

from ..models.scripts import AgentScript
from ..utils.serialization import serialize_for_json


def register_api_v5_routes(server):
    """Register all API v5 remote control routes with the server"""
    
    @server.app.route('/api/v4/task-control/create-task', methods=['POST'])
    def create_central_task():
        """Create a new central task"""
        try:
            data = request.get_json()
            task_type = data.get('task_type')
            priority = data.get('priority', 5)
            
            if not task_type:
                return jsonify({"error": "task_type required"}), 400
            
            task = server.task_control.create_task(task_type)
            task.priority = priority
            
            server.task_control.pending_tasks.append(task)
            server.task_control.store_task_in_db(task)
            
            return jsonify({
                "success": True,
                "task_id": task.id,
                "message": f"Central task {task_type} created successfully"
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v4/task-control/statistics', methods=['GET'])
    def get_task_control_statistics():
        """Get task control statistics"""
        try:
            stats = server.task_control.get_task_statistics()
            return jsonify(stats)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v5/remote/agents/<agent_id>/command', methods=['POST'])
    @server.app.route('/api/v5/remote/agents/<agent_id>/bulk-command', methods=['POST'])
    def send_command_to_agent(agent_id):
        """Send command to specific agent"""
        try:
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            data = request.get_json()
            command_type = data.get('command_type')
            parameters = data.get('parameters', {})
            
            if not command_type:
                return jsonify({"error": "command_type required"}), 400
            
            command = server.advanced_remote_control.create_agent_command(
                agent_id, command_type, parameters
            )
            success = server.advanced_remote_control.execute_command_on_agent(command)
            
            if success:
                server.metrics['commands_total'].inc()
                return jsonify({
                    "success": True,
                    "command_id": command.id,
                    "message": f"Command {command_type} sent to agent {agent_id}"
                })
            else:
                return jsonify({"success": False, "error": "Failed to send command"}), 500
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v5/remote/bulk-operation', methods=['POST'])
    def create_bulk_operation():
        """Create bulk operation for multiple agents"""
        try:
            data = request.get_json()
            operation_type = data.get('operation_type')
            target_agents = data.get('target_agents', [])
            parameters = data.get('parameters', {})
            
            if not operation_type:
                return jsonify({"error": "operation_type required"}), 400
            
            if not target_agents:
                return jsonify({"error": "target_agents required"}), 400
            
            # Validate agents exist
            invalid_agents = [agent_id for agent_id in target_agents if agent_id not in server.agents]
            if invalid_agents:
                return jsonify({"error": f"Invalid agents: {invalid_agents}"}), 400
            
            bulk_op = server.advanced_remote_control.create_bulk_operation(
                operation_type, target_agents, parameters
            )
            server.metrics['bulk_operations_total'].inc()
            
            return jsonify({
                "success": True,
                "operation_id": bulk_op.id,
                "message": f"Bulk operation {operation_type} created for {len(target_agents)} agents"
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v5/remote/schedule-command', methods=['POST'])
    def schedule_command():
        """Schedule command for later execution"""
        try:
            data = request.get_json()
            agent_id = data.get('agent_id')
            command_type = data.get('command_type')
            scheduled_time_str = data.get('scheduled_time')
            parameters = data.get('parameters', {})
            repeat_interval = data.get('repeat_interval')
            max_repeats = data.get('max_repeats', 1)
            
            if not all([agent_id, command_type, scheduled_time_str]):
                return jsonify({"error": "agent_id, command_type, and scheduled_time required"}), 400
            
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            # Parse scheduled time
            try:
                scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid scheduled_time format"}), 400
            
            scheduled_cmd = server.advanced_remote_control.create_scheduled_command(
                agent_id, command_type, scheduled_time, parameters, repeat_interval, max_repeats
            )
            
            return jsonify({
                "success": True,
                "scheduled_command_id": scheduled_cmd.id,
                "message": f"Command {command_type} scheduled for agent {agent_id} at {scheduled_time}"
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v5/remote/deploy-script', methods=['POST'])
    def deploy_script():
        """Deploy script to agents"""
        try:
            data = request.get_json()
            script_name = data.get('script_name')
            script_content = data.get('script_content')
            script_type = data.get('script_type', 'python')
            target_agents = data.get('target_agents', [])
            
            if not all([script_name, script_content]):
                return jsonify({"error": "script_name and script_content required"}), 400
            
            if not target_agents:
                return jsonify({"error": "target_agents required"}), 400
            
            # Validate agents exist
            invalid_agents = [agent_id for agent_id in target_agents if agent_id not in server.agents]
            if invalid_agents:
                return jsonify({"error": f"Invalid agents: {invalid_agents}"}), 400
            
            script = AgentScript(
                id=f"script-{int(datetime.now().timestamp())}-{uuid.uuid4().hex[:8]}",
                name=script_name,
                version="1.0",
                script_type=script_type,
                script_content=script_content,
                checksum="",  # Will be calculated in __post_init__
                target_agents=target_agents
            )
            
            server.advanced_remote_control.agent_scripts[script.id] = script
            server.advanced_remote_control.store_script_in_db(script)
            
            # Deploy to agents
            deployment_results = {}
            for agent_id in target_agents:
                success = server.advanced_remote_control.deploy_script_to_agent(agent_id, script)
                deployment_results[agent_id] = "deployed" if success else "failed"
            
            server.metrics['scripts_deployed_total'].inc()
            
            return jsonify({
                "success": True,
                "script_id": script.id,
                "deployment_results": deployment_results,
                "message": f"Script {script_name} deployed to {len(target_agents)} agents"
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v5/remote/agents/<agent_id>/health', methods=['GET'])
    def get_agent_health(agent_id):
        """Get comprehensive agent health information"""
        try:
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            # Get recent health checks
            recent_health = server.db.get_agent_health_history(agent_id, 24)
            
            health_data = {
                "agent_id": agent_id,
                "current_status": server.agent_status.get(agent_id).status if agent_id in server.agent_status else "unknown",
                "recent_health_checks": [
                    {
                        "timestamp": check.timestamp.isoformat(),
                        "status": check.status,
                        "health_score": check.health_score,
                        "cpu_health": check.cpu_health,
                        "memory_health": check.memory_health,
                        "network_health": check.network_health,
                        "task_health": check.task_health,
                        "recovery_needed": check.recovery_needed,
                        "recovery_actions": check.recovery_actions
                    }
                    for check in recent_health
                ]
            }
            
            return jsonify(health_data)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v5/remote/agents/<agent_id>/history', methods=['GET'])
    def get_command_history(agent_id):
        """Get command history for agent"""
        try:
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            limit = request.args.get('limit', 50, type=int)
            history = server.advanced_remote_control.get_command_history(agent_id, limit)
            
            return jsonify({
                "agent_id": agent_id,
                "command_history": history,
                "total_commands": len(history)
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v5/remote/commands/<command_id>/replay', methods=['POST'])
    def replay_command(command_id):
        """Replay a previous command"""
        try:
            success = server.advanced_remote_control.replay_command(command_id)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": f"Command {command_id} replayed successfully"
                })
            else:
                return jsonify({"success": False, "error": "Failed to replay command"}), 500
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v5/remote/advanced-statistics', methods=['GET'])
    def get_advanced_remote_statistics():
        """Get advanced remote control statistics"""
        try:
            stats = server.advanced_remote_control.get_advanced_statistics()
            return jsonify(stats)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v5/remote/advanced-capabilities', methods=['GET'])
    def get_advanced_capabilities():
        """Get available advanced remote control capabilities"""
        try:
            return jsonify({
                "advanced_commands": server.advanced_remote_control.advanced_commands,
                "command_templates": server.advanced_remote_control.advanced_command_templates,
                "features": {
                    "bulk_operations": True,
                    "command_scheduling": True,
                    "script_deployment": True,
                    "health_monitoring": True,
                    "command_history": True,
                    "command_replay": True,
                    "auto_recovery": True
                }
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v5/remote/bulk-operations', methods=['GET'])
    def get_bulk_operations():
        """Get list of bulk operations"""
        try:
            operations = []
            for bulk_op in server.advanced_remote_control.bulk_operations.values():
                operations.append(serialize_for_json(bulk_op))
            
            return jsonify({
                "bulk_operations": operations,
                "total_operations": len(operations)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v5/remote/bulk-operations/<operation_id>', methods=['GET'])
    def get_bulk_operation_status(operation_id):
        """Get status of specific bulk operation"""
        try:
            if operation_id not in server.advanced_remote_control.bulk_operations:
                return jsonify({"error": "Bulk operation not found"}), 404
            
            bulk_op = server.advanced_remote_control.bulk_operations[operation_id]
            return jsonify(serialize_for_json(bulk_op))
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v5/remote/scheduled-commands', methods=['GET'])
    def get_scheduled_commands():
        """Get list of scheduled commands"""
        try:
            commands = []
            for scheduled_cmd in server.advanced_remote_control.scheduled_commands.values():
                commands.append(serialize_for_json(scheduled_cmd))
            
            return jsonify({
                "scheduled_commands": commands,
                "total_commands": len(commands)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v5/remote/scheduled-commands/<command_id>', methods=['DELETE'])
    def cancel_scheduled_command(command_id):
        """Cancel a scheduled command"""
        try:
            if command_id not in server.advanced_remote_control.scheduled_commands:
                return jsonify({"error": "Scheduled command not found"}), 404
            
            scheduled_cmd = server.advanced_remote_control.scheduled_commands[command_id]
            scheduled_cmd.status = "cancelled"
            server.advanced_remote_control.update_scheduled_command_in_db(scheduled_cmd)
            
            return jsonify({
                "success": True,
                "message": f"Scheduled command {command_id} cancelled"
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v5/remote/scripts', methods=['GET'])
    def get_deployed_scripts():
        """Get list of deployed scripts"""
        try:
            scripts = []
            for script in server.advanced_remote_control.agent_scripts.values():
                scripts.append(serialize_for_json(script))
            
            return jsonify({
                "scripts": scripts,
                "total_scripts": len(scripts)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v5/remote/scripts/<script_id>', methods=['GET'])
    def get_script_details(script_id):
        """Get details of specific script"""
        try:
            if script_id not in server.advanced_remote_control.agent_scripts:
                return jsonify({"error": "Script not found"}), 404
            
            script = server.advanced_remote_control.agent_scripts[script_id]
            return jsonify(serialize_for_json(script))
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500