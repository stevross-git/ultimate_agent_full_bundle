#!/usr/bin/env python3
"""
Enhanced WebSocket Events with Ultimate Agent API Integration
Updated websocket/events.py with Ultimate Agent API support
"""

import requests
import asyncio
from flask_socketio import emit, join_room, leave_room
from ..config.settings import NODE_ID, NODE_VERSION


def register_websocket_events(server):
    """Register all WebSocket events with Ultimate Agent API integration"""
    
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
            'advanced_control_enabled': True,
            'ultimate_agent_api_enabled': True,
            'api_proxy_enabled': True
        })
        server.logger.info("Client connected to Enhanced Node Server with Ultimate API")
    
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
    
    # NEW: Ultimate Agent API Integration Events
    @server.socketio.on('request_ultimate_api_summary')
    def handle_ultimate_api_summary_request():
        """Send Ultimate Agent API summary"""
        try:
            summary = {
                "total_agents": len(server.agents),
                "agents_with_api": 0,
                "total_ai_models": 0,
                "total_blockchain_balance": 0.0,
                "total_training_sessions": 0,
                "api_endpoints_available": [],
                "agent_details": []
            }
            
            for agent_id, agent_info in server.agents.items():
                try:
                    base_url = f"http://{agent_info.host}:8080"
                    
                    # Quick API check with timeout
                    response = requests.get(f"{base_url}/api/stats", timeout=2)
                    if response.status_code == 200:
                        summary["agents_with_api"] += 1
                        stats = response.json()
                        
                        agent_detail = {
                            "agent_id": agent_id,
                            "host": agent_info.host,
                            "api_url": base_url,
                            "ai_models_loaded": stats.get("ai_models_loaded", 0),
                            "total_earnings": stats.get("total_earnings", 0.0),
                            "tasks_running": stats.get("current_tasks", 0),
                            "tasks_completed": stats.get("tasks_completed", 0),
                            "api_status": "online"
                        }
                        
                        summary["agent_details"].append(agent_detail)
                        summary["total_ai_models"] += stats.get("ai_models_loaded", 0)
                        summary["total_blockchain_balance"] += stats.get("total_earnings", 0.0)
                        
                except Exception:
                    summary["agent_details"].append({
                        "agent_id": agent_id,
                        "host": agent_info.host,
                        "api_status": "offline"
                    })
            
            emit('ultimate_api_summary', summary)
            
        except Exception as e:
            emit('error', {'message': f'Failed to get Ultimate API summary: {str(e)}'})
    
    @server.socketio.on('test_agent_api')
    def handle_test_agent_api(data):
        """Test Ultimate Agent API for specific agent"""
        try:
            agent_id = data.get('agent_id')
            if not agent_id or agent_id not in server.agents:
                emit('api_test_result', {
                    'agent_id': agent_id,
                    'success': False,
                    'error': 'Agent not found'
                })
                return
            
            agent_info = server.agents[agent_id]
            base_url = f"http://{agent_info.host}:8080"
            
            # Test multiple endpoints
            test_results = {
                'agent_id': agent_id,
                'base_url': base_url,
                'tests': {}
            }
            
            # Test basic stats
            try:
                response = requests.get(f"{base_url}/api/stats", timeout=5)
                test_results['tests']['stats'] = {
                    'success': response.status_code == 200,
                    'status_code': response.status_code,
                    'data': response.json() if response.status_code == 200 else None
                }
            except Exception as e:
                test_results['tests']['stats'] = {
                    'success': False,
                    'error': str(e)
                }
            
            # Test AI capabilities
            try:
                response = requests.get(f"{base_url}/api/v3/ai/capabilities", timeout=5)
                test_results['tests']['ai_capabilities'] = {
                    'success': response.status_code == 200,
                    'status_code': response.status_code,
                    'data': response.json() if response.status_code == 200 else None
                }
            except Exception as e:
                test_results['tests']['ai_capabilities'] = {
                    'success': False,
                    'error': str(e)
                }
            
            # Test blockchain status
            try:
                response = requests.get(f"{base_url}/api/v3/blockchain/enhanced", timeout=5)
                test_results['tests']['blockchain'] = {
                    'success': response.status_code == 200,
                    'status_code': response.status_code,
                    'data': response.json() if response.status_code == 200 else None
                }
            except Exception as e:
                test_results['tests']['blockchain'] = {
                    'success': False,
                    'error': str(e)
                }
            
            # Calculate overall success
            successful_tests = sum(1 for test in test_results['tests'].values() if test.get('success', False))
            test_results['overall_success'] = successful_tests > 0
            test_results['success_rate'] = successful_tests / len(test_results['tests'])
            
            emit('api_test_result', test_results)
            
        except Exception as e:
            emit('api_test_result', {
                'agent_id': data.get('agent_id'),
                'success': False,
                'error': str(e)
            })
    
    @server.socketio.on('run_ai_inference')
    def handle_ai_inference_request(data):
        """Run AI inference on Ultimate Agent"""
        try:
            agent_id = data.get('agent_id')
            model = data.get('model', 'sentiment')
            input_text = data.get('input')
            
            if not agent_id or agent_id not in server.agents:
                emit('ai_inference_result', {
                    'success': False,
                    'error': 'Agent not found'
                })
                return
            
            if not input_text:
                emit('ai_inference_result', {
                    'success': False,
                    'error': 'Input text required'
                })
                return
            
            agent_info = server.agents[agent_id]
            base_url = f"http://{agent_info.host}:8080"
            
            # Send inference request
            response = requests.post(
                f"{base_url}/api/ai/inference",
                json={
                    'model': model,
                    'input': input_text,
                    'options': {
                        'return_confidence': True,
                        'return_details': True
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                emit('ai_inference_result', {
                    'success': True,
                    'agent_id': agent_id,
                    'model': model,
                    'input': input_text,
                    'result': result
                })
            else:
                emit('ai_inference_result', {
                    'success': False,
                    'agent_id': agent_id,
                    'error': f'API returned status {response.status_code}'
                })
            
        except Exception as e:
            emit('ai_inference_result', {
                'success': False,
                'agent_id': data.get('agent_id'),
                'error': str(e)
            })
    
    @server.socketio.on('start_agent_task')
    def handle_start_agent_task(data):
        """Start task on Ultimate Agent"""
        try:
            agent_id = data.get('agent_id')
            task_type = data.get('task_type')
            task_config = data.get('config', {})
            
            if not agent_id or agent_id not in server.agents:
                emit('task_start_result', {
                    'success': False,
                    'error': 'Agent not found'
                })
                return
            
            agent_info = server.agents[agent_id]
            base_url = f"http://{agent_info.host}:8080"
            
            # Send task start request
            response = requests.post(
                f"{base_url}/api/start_task",
                json={
                    'type': task_type,
                    'config': task_config
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                emit('task_start_result', {
                    'success': True,
                    'agent_id': agent_id,
                    'task_type': task_type,
                    'result': result
                })
                
                # Broadcast to dashboard
                emit('agent_task_started', {
                    'agent_id': agent_id,
                    'task_type': task_type,
                    'task_id': result.get('task_id'),
                    'timestamp': datetime.now().isoformat()
                }, room='dashboard')
                
            else:
                emit('task_start_result', {
                    'success': False,
                    'agent_id': agent_id,
                    'error': f'API returned status {response.status_code}'
                })
            
        except Exception as e:
            emit('task_start_result', {
                'success': False,
                'agent_id': data.get('agent_id'),
                'error': str(e)
            })
    
    @server.socketio.on('execute_smart_contract')
    def handle_smart_contract_execution(data):
        """Execute smart contract on Ultimate Agent"""
        try:
            agent_id = data.get('agent_id')
            contract_type = data.get('contract_type', 'task_rewards')
            method = data.get('method', 'claimReward')
            params = data.get('params', {})
            
            if not agent_id or agent_id not in server.agents:
                emit('smart_contract_result', {
                    'success': False,
                    'error': 'Agent not found'
                })
                return
            
            agent_info = server.agents[agent_id]
            base_url = f"http://{agent_info.host}:8080"
            
            # Send smart contract execution request
            response = requests.post(
                f"{base_url}/api/blockchain/smart-contract/execute",
                json={
                    'contract_type': contract_type,
                    'method': method,
                    'params': params
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                emit('smart_contract_result', {
                    'success': True,
                    'agent_id': agent_id,
                    'contract_type': contract_type,
                    'method': method,
                    'result': result
                })
                
                # Broadcast to dashboard
                emit('smart_contract_executed', {
                    'agent_id': agent_id,
                    'contract_type': contract_type,
                    'method': method,
                    'transaction_hash': result.get('transaction_hash'),
                    'timestamp': datetime.now().isoformat()
                }, room='dashboard')
                
            else:
                emit('smart_contract_result', {
                    'success': False,
                    'agent_id': agent_id,
                    'error': f'API returned status {response.status_code}'
                })
            
        except Exception as e:
            emit('smart_contract_result', {
                'success': False,
                'agent_id': data.get('agent_id'),
                'error': str(e)
            })
    
    @server.socketio.on('get_agent_performance')
    def handle_agent_performance_request(data):
        """Get performance metrics from Ultimate Agent"""
        try:
            agent_id = data.get('agent_id')
            
            if not agent_id or agent_id not in server.agents:
                emit('agent_performance_result', {
                    'success': False,
                    'error': 'Agent not found'
                })
                return
            
            agent_info = server.agents[agent_id]
            base_url = f"http://{agent_info.host}:8080"
            
            # Get performance metrics
            response = requests.get(f"{base_url}/api/performance/metrics", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                emit('agent_performance_result', {
                    'success': True,
                    'agent_id': agent_id,
                    'performance_data': result
                })
            else:
                emit('agent_performance_result', {
                    'success': False,
                    'agent_id': agent_id,
                    'error': f'API returned status {response.status_code}'
                })
            
        except Exception as e:
            emit('agent_performance_result', {
                'success': False,
                'agent_id': data.get('agent_id'),
                'error': str(e)
            })
    
    @server.socketio.on('bulk_agent_operation')
    def handle_bulk_agent_operation(data):
        """Execute operation across multiple Ultimate Agents"""
        try:
            operation = data.get('operation')
            target_agents = data.get('agents', [])
            operation_params = data.get('params', {})
            
            if not operation:
                emit('bulk_operation_result', {
                    'success': False,
                    'error': 'Operation type required'
                })
                return
            
            if not target_agents:
                # Use all agents with API
                target_agents = list(server.agents.keys())
            
            results = []
            for agent_id in target_agents:
                if agent_id not in server.agents:
                    results.append({
                        'agent_id': agent_id,
                        'success': False,
                        'error': 'Agent not found'
                    })
                    continue
                
                try:
                    agent_info = server.agents[agent_id]
                    base_url = f"http://{agent_info.host}:8080"
                    
                    if operation == 'start_task':
                        response = requests.post(
                            f"{base_url}/api/start_task",
                            json=operation_params,
                            timeout=10
                        )
                    elif operation == 'get_stats':
                        response = requests.get(f"{base_url}/api/stats", timeout=5)
                    elif operation == 'ai_inference':
                        response = requests.post(
                            f"{base_url}/api/ai/inference",
                            json=operation_params,
                            timeout=30
                        )
                    else:
                        results.append({
                            'agent_id': agent_id,
                            'success': False,
                            'error': f'Unknown operation: {operation}'
                        })
                        continue
                    
                    if response.status_code == 200:
                        results.append({
                            'agent_id': agent_id,
                            'success': True,
                            'result': response.json()
                        })
                    else:
                        results.append({
                            'agent_id': agent_id,
                            'success': False,
                            'error': f'API returned status {response.status_code}'
                        })
                
                except Exception as e:
                    results.append({
                        'agent_id': agent_id,
                        'success': False,
                        'error': str(e)
                    })
            
            # Calculate summary
            successful = sum(1 for r in results if r['success'])
            failed = len(results) - successful
            
            emit('bulk_operation_result', {
                'success': True,
                'operation': operation,
                'total_agents': len(results),
                'successful': successful,
                'failed': failed,
                'results': results
            })
            
        except Exception as e:
            emit('bulk_operation_result', {
                'success': False,
                'error': str(e)
            })
    
    @server.socketio.on('monitor_agent_apis')
    def handle_monitor_agent_apis():
        """Monitor all Ultimate Agent APIs and broadcast status"""
        try:
            api_status = {}
            
            for agent_id, agent_info in server.agents.items():
                try:
                    base_url = f"http://{agent_info.host}:8080"
                    response = requests.get(f"{base_url}/api/stats", timeout=3)
                    
                    if response.status_code == 200:
                        stats = response.json()
                        api_status[agent_id] = {
                            'status': 'online',
                            'api_url': base_url,
                            'response_time': response.elapsed.total_seconds(),
                            'stats': stats
                        }
                    else:
                        api_status[agent_id] = {
                            'status': 'error',
                            'api_url': base_url,
                            'error': f'HTTP {response.status_code}'
                        }
                
                except Exception as e:
                    api_status[agent_id] = {
                        'status': 'offline',
                        'api_url': f"http://{agent_info.host}:8080",
                        'error': str(e)
                    }
            
            emit('agent_apis_status', api_status)
            
        except Exception as e:
            emit('error', {'message': f'Failed to monitor agent APIs: {str(e)}'})
    
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
    
    # EXISTING: Advanced Remote Control WebSocket Events
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
    
    # EXISTING: Agent Status Events
    @server.socketio.on('request_agent_list')
    def handle_agent_list_request():
        """Send current agent list with Ultimate API integration"""
        try:
            agents_list = []
            for agent_id, agent_info in server.agents.items():
                agent_status = server.agent_status.get(agent_id)
                if agent_status:
                    from ..utils.serialization import serialize_for_json
                    agent_data = {
                        **serialize_for_json(agent_info),
                        **serialize_for_json(agent_status),
                        # Add Ultimate Agent API info
                        "ultimate_api": {
                            "url": f"http://{agent_info.host}:8080",
                            "dashboard_url": f"http://{agent_info.host}:8080",
                            "websocket_url": f"ws://{agent_info.host}:8080/socket.io/"
                        }
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
    
    # Utility Events
    @server.socketio.on('request_system_info')
    def handle_system_info_request():
        """Send system information with Ultimate API integration"""
        emit('system_info', {
            'node_id': NODE_ID,
            'node_version': NODE_VERSION,
            'features_enabled': {
                'task_control': True,
                'remote_management': True,
                'advanced_control': True,
                'ultimate_agent_api': True,
                'api_proxy': True,
                'health_monitoring': server.advanced_remote_control.health_monitor_running,
                'command_scheduling': server.advanced_remote_control.scheduler_running,
                'bulk_operations': True,
                'script_deployment': True
            },
            'ultimate_api_integration': {
                'enabled': True,
                'proxy_endpoints': [
                    '/api/v3/agents/{agent_id}/ai/inference',
                    '/api/v3/agents/{agent_id}/start_task',
                    '/api/v3/agents/{agent_id}/blockchain/transaction'
                ],
                'supported_operations': [
                    'ai_inference', 'task_control', 'blockchain_operations',
                    'performance_monitoring', 'bulk_operations'
                ]
            },
            'capabilities': {
                'max_agents': 1000,
                'max_concurrent_tasks': 100,
                'supported_agent_types': ['ultimate', 'standard', 'lite'],
                'supported_protocols': ['websocket', 'http', 'https'],
                'api_proxy_timeout': 60
            }
        })
    
    server.logger.info("Enhanced WebSocket events with Ultimate Agent API integration registered successfully")