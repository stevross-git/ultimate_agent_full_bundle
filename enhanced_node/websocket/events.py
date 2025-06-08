#!/usr/bin/env python3
"""
WebSocket Events - Real-time communication with agents and dashboard
"""

from flask_socketio import emit, join_room, leave_room
from ..config.settings import NODE_ID, NODE_VERSION


def register_websocket_events(server):
    """Register all WebSocket events with the server"""
    
    @server.socketio.on('connect')
    def handle_connect(auth):
        """Handle client connection"""
        join_room('dashboard')
        emit('connected', {
            'node_id': NODE_ID,
            'node_version': NODE_VERSION,
            'features': ['ai', 'blockchain', 'cloud', 'analytics'],
            'task_control_enabled': True,
            'remote_management_enabled': True,
            'advanced_control_enabled': True
        })
        server.logger.info("Client connected to dashboard")
    
    @server.socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        server.logger.info("Client disconnected from dashboard")
    
    @server.socketio.on('join_agent_room')
    def handle_join_agent_room(data):
        """Join agent-specific room for targeted communication"""
        agent_id = data.get('agent_id')
        if agent_id and agent_id in server.agents:
            join_room(f'agent_{agent_id}')
            emit('joined_agent_room', {'agent_id': agent_id})
            server.logger.info(f"Client joined room for agent {agent_id}")
        else:
            emit('error', {'message': 'Invalid agent ID'})
    
    @server.socketio.on('leave_agent_room')
    def handle_leave_agent_room(data):
        """Leave agent-specific room"""
        agent_id = data.get('agent_id')
        if agent_id:
            leave_room(f'agent_{agent_id}')
            emit('left_agent_room', {'agent_id': agent_id})
            server.logger.info(f"Client left room for agent {agent_id}")
    
    # EXISTING: Task Control WebSocket Events
    @server.socketio.on('request_task_control_stats')
    def handle_task_control_stats_request():
        """Send task control statistics"""
        try:
            stats = server.task_control.get_task_statistics()
            emit('task_control_stats', stats)
        except Exception as e:
            emit('error', {'message': f'Failed to get task control stats: {str(e)}'})
    
    @server.socketio.on('central_task_completed')
    def handle_central_task_completed(data):
        """Handle central task completion from agents"""
        try:
            task_id = data.get('task_id')
            agent_id = data.get('agent_id')
            success = data.get('success', False)
            result = data.get('result', {})
            
            if task_id and agent_id:
                server.task_control.handle_task_completion(task_id, agent_id, success, result)
                
                # Broadcast update to dashboard
                emit('central_task_update', {
                    'task_id': task_id,
                    'agent_id': agent_id,
                    'status': 'completed' if success else 'failed',
                    'result': result
                }, room='dashboard')
                
                server.logger.info(f"Central task {task_id} {'completed' if success else 'failed'} by agent {agent_id}")
            
        except Exception as e:
            server.logger.error(f"Error handling central task completion: {e}")
            emit('error', {'message': f'Failed to handle task completion: {str(e)}'})
    
    @server.socketio.on('request_pending_tasks')
    def handle_pending_tasks_request(data):
        """Send pending tasks to requesting agent"""
        try:
            agent_id = data.get('agent_id')
            if agent_id and agent_id in server.agents:
                pending_tasks = server.task_control.get_pending_tasks(5)  # Get up to 5 tasks
                
                # Send tasks to specific agent
                emit('pending_tasks', {
                    'tasks': [
                        {
                            'task_id': task.id,
                            'task_type': task.task_type,
                            'priority': task.priority,
                            'config': task.config,
                            'requirements': task.requirements,
                            'estimated_duration': task.estimated_duration,
                            'reward': task.reward
                        }
                        for task in pending_tasks
                    ]
                }, room=f'agent_{agent_id}')
                
                server.logger.info(f"Sent {len(pending_tasks)} pending tasks to agent {agent_id}")
            
        except Exception as e:
            server.logger.error(f"Error sending pending tasks: {e}")
            emit('error', {'message': f'Failed to get pending tasks: {str(e)}'})
    
    @server.socketio.on('accept_central_task')
    def handle_accept_central_task(data):
        """Handle agent accepting a central task"""
        try:
            task_id = data.get('task_id')
            agent_id = data.get('agent_id')
            
            if task_id and agent_id:
                # Find the task in pending tasks
                for task in server.task_control.pending_tasks:
                    if task.id == task_id:
                        server.task_control.assign_task_to_agent(task, agent_id)
                        
                        emit('task_assigned', {
                            'task_id': task_id,
                            'agent_id': agent_id,
                            'message': f'Task {task_id} assigned to agent {agent_id}'
                        }, room='dashboard')
                        
                        server.logger.info(f"Task {task_id} assigned to agent {agent_id}")
                        break
                else:
                    emit('error', {'message': f'Task {task_id} not found in pending tasks'})
            
        except Exception as e:
            server.logger.error(f"Error accepting central task: {e}")
            emit('error', {'message': f'Failed to accept task: {str(e)}'})
    
    # NEW: Advanced Remote Control WebSocket Events
    @server.socketio.on('request_advanced_remote_stats')
    def handle_advanced_remote_stats_request():
        """Send advanced remote control statistics"""
        try:
            stats = server.advanced_remote_control.get_advanced_statistics()
            emit('advanced_remote_stats', stats)
        except Exception as e:
            emit('error', {'message': f'Failed to get advanced remote stats: {str(e)}'})
    
    @server.socketio.on('advanced_command_response')
    def handle_advanced_command_response(data):
        """Handle advanced command execution response from agents"""
        try:
            command_id = data.get('command_id')
            success = data.get('success', False)
            result = data.get('result', {})
            error = data.get('error')
            
            if command_id:
                server.advanced_remote_control.handle_command_response(
                    command_id, success, result, error
                )
                server.logger.info(f"Advanced command {command_id} response received: {'success' if success else 'failed'}")
            
        except Exception as e:
            server.logger.error(f"Error handling advanced command response: {e}")
            emit('error', {'message': f'Failed to handle command response: {str(e)}'})
    
    @server.socketio.on('request_bulk_operation_status')
    def handle_bulk_operation_status_request(data):
        """Get bulk operation status"""
        try:
            operation_id = data.get('operation_id')
            if operation_id in server.advanced_remote_control.bulk_operations:
                bulk_op = server.advanced_remote_control.bulk_operations[operation_id]
                emit('bulk_operation_status', {
                    'operation_id': operation_id,
                    'status': bulk_op.status,
                    'success_count': bulk_op.success_count,
                    'failure_count': bulk_op.failure_count,
                    'results': bulk_op.results
                })
            else:
                emit('error', {'message': f'Bulk operation {operation_id} not found'})
        except Exception as e:
            emit('error', {'message': f'Failed to get bulk operation status: {str(e)}'})
    
    @server.socketio.on('request_agent_health_status')
    def handle_agent_health_status_request(data):
        """Get real-time agent health status"""
        try:
            agent_id = data.get('agent_id')
            if agent_id in server.agents:
                # Get latest health check
                recent_health = server.db.get_agent_health_history(agent_id, 1)
                
                if recent_health:
                    latest_health = recent_health[0]
                    emit('agent_health_status', {
                        'agent_id': agent_id,
                        'status': latest_health.status,
                        'health_score': latest_health.health_score,
                        'cpu_health': latest_health.cpu_health,
                        'memory_health': latest_health.memory_health,
                        'network_health': latest_health.network_health,
                        'task_health': latest_health.task_health,
                        'recovery_needed': latest_health.recovery_needed,
                        'recovery_actions': latest_health.recovery_actions,
                        'timestamp': latest_health.timestamp.isoformat()
                    })
                else:
                    emit('agent_health_status', {
                        'agent_id': agent_id,
                        'status': 'unknown',
                        'message': 'No health data available'
                    })
            else:
                emit('error', {'message': f'Agent {agent_id} not found'})
        except Exception as e:
            emit('error', {'message': f'Failed to get agent health status: {str(e)}'})
    
    @server.socketio.on('request_command_history')
    def handle_command_history_request(data):
        """Get command history for an agent"""
        try:
            agent_id = data.get('agent_id')
            limit = data.get('limit', 50)
            
            if agent_id in server.agents:
                history = server.advanced_remote_control.get_command_history(agent_id, limit)
                emit('command_history', {
                    'agent_id': agent_id,
                    'commands': history,
                    'total_commands': len(history)
                })
            else:
                emit('error', {'message': f'Agent {agent_id} not found'})
        except Exception as e:
            emit('error', {'message': f'Failed to get command history: {str(e)}'})
    
    @server.socketio.on('request_scheduled_commands')
    def handle_scheduled_commands_request():
        """Get list of scheduled commands"""
        try:
            scheduled_commands = []
            for scheduled_cmd in server.advanced_remote_control.scheduled_commands.values():
                scheduled_commands.append({
                    'id': scheduled_cmd.id,
                    'agent_id': scheduled_cmd.command.agent_id,
                    'command_type': scheduled_cmd.command.command_type,
                    'scheduled_time': scheduled_cmd.scheduled_time.isoformat(),
                    'status': scheduled_cmd.status,
                    'repeat_interval': scheduled_cmd.repeat_interval,
                    'current_repeats': scheduled_cmd.current_repeats,
                    'max_repeats': scheduled_cmd.max_repeats
                })
            
            emit('scheduled_commands', {
                'commands': scheduled_commands,
                'total_commands': len(scheduled_commands)
            })
        except Exception as e:
            emit('error', {'message': f'Failed to get scheduled commands: {str(e)}'})
    
    @server.socketio.on('request_deployed_scripts')
    def handle_deployed_scripts_request():
        """Get list of deployed scripts"""
        try:
            scripts = []
            for script in server.advanced_remote_control.agent_scripts.values():
                scripts.append({
                    'id': script.id,
                    'name': script.name,
                    'version': script.version,
                    'script_type': script.script_type,
                    'target_agents': script.target_agents,
                    'status': script.status,
                    'created_at': script.created_at.isoformat() if script.created_at else None,
                    'deployed_at': script.deployed_at.isoformat() if script.deployed_at else None,
                    'deployment_results': script.deployment_results
                })
            
            emit('deployed_scripts', {
                'scripts': scripts,
                'total_scripts': len(scripts)
            })
        except Exception as e:
            emit('error', {'message': f'Failed to get deployed scripts: {str(e)}'})
    
    # EXISTING: Agent Status Events
    @server.socketio.on('request_agent_list')
    def handle_agent_list_request():
        """Send current agent list"""
        try:
            agents_list = []
            for agent_id, agent_info in server.agents.items():
                agent_status = server.agent_status.get(agent_id)
                if agent_status:
                    from ..utils.serialization import serialize_for_json
                    agent_data = {
                        **serialize_for_json(agent_info),
                        **serialize_for_json(agent_status)
                    }
                    agents_list.append(agent_data)
            
            emit('agent_list', {
                'agents': agents_list,
                'total_agents': len(agents_list),
                'timestamp': server.get_enhanced_node_stats()['timestamp']
            })
        except Exception as e:
            emit('error', {'message': f'Failed to get agent list: {str(e)}'})
    
    @server.socketio.on('request_node_stats')
    def handle_node_stats_request():
        """Send comprehensive node statistics"""
        try:
            stats = server.get_enhanced_node_stats()
            emit('node_stats', stats)
        except Exception as e:
            emit('error', {'message': f'Failed to get node stats: {str(e)}'})
    
    @server.socketio.on('ping')
    def handle_ping():
        """Handle ping for connection testing"""
        emit('pong', {'timestamp': server.get_enhanced_node_stats()['timestamp']})
    
    # Agent Registration Events (for agents connecting via WebSocket)
    @server.socketio.on('agent_register')
    def handle_agent_register(data):
        """Handle agent registration via WebSocket"""
        try:
            result = server.register_agent(data)
            emit('registration_result', result)
            
            # Notify dashboard of new agent
            emit('ultimate_agent_registered', {
                'agent_id': data.get('agent_id'),
                'agent_type': data.get('agent_type', 'ultimate'),
                'features': data.get('features', []),
                'timestamp': result.get('timestamp', '')
            }, room='dashboard')
            
        except Exception as e:
            emit('registration_result', {
                'success': False,
                'error': str(e)
            })
    
    @server.socketio.on('agent_heartbeat')
    def handle_agent_heartbeat_ws(data):
        """Handle agent heartbeat via WebSocket"""
        try:
            result = server.process_agent_heartbeat(data)
            emit('heartbeat_result', result)
        except Exception as e:
            emit('heartbeat_result', {
                'success': False,
                'error': str(e)
            })
    
    # Utility Events
    @server.socketio.on('request_system_info')
    def handle_system_info_request():
        """Send system information"""
        emit('system_info', {
            'node_id': NODE_ID,
            'node_version': NODE_VERSION,
            'features_enabled': {
                'task_control': True,
                'remote_management': True,
                'advanced_control': True,
                'health_monitoring': server.advanced_remote_control.health_monitor_running,
                'command_scheduling': server.advanced_remote_control.scheduler_running,
                'bulk_operations': True,
                'script_deployment': True
            },
            'capabilities': {
                'max_agents': 1000,
                'max_concurrent_tasks': 100,
                'supported_agent_types': ['ultimate', 'standard', 'lite'],
                'supported_protocols': ['websocket', 'http', 'https']
            }
        })
    
    server.logger.info("WebSocket events registered successfully")