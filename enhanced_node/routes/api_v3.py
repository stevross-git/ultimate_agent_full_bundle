#!/usr/bin/env python3
"""
Complete API v3 Routes - Enhanced Node Server with Ultimate Agent API Integration
All existing features preserved + new Ultimate Agent API features added
"""

from flask import request, jsonify
from datetime import datetime
import json
import requests
import time

from ..core.database import Agent, AgentHeartbeat
from ..models.agents import EnhancedAgentInfo, EnhancedAgentStatus
from ..utils.serialization import serialize_for_json
from ..config.settings import NODE_ID, NODE_VERSION


def register_api_v3_routes(server):
    """Register all API v3 routes with Ultimate Agent API integration"""
    
    @server.app.route('/')
    def enhanced_dashboard():
        """Serve enhanced node dashboard with Ultimate Agent API integration"""
        return get_enhanced_dashboard_html()
    
    @server.app.route('/api/v3/agents/register', methods=['POST'])
    @server.app.route('/api/agents/register', methods=['POST'])  # Legacy support
    @server.limiter.limit("10 per minute")
    def register_ultimate_agent():
        """Register Ultimate Pain Network Agent"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "No data provided"}), 400
            
            result = server.register_agent(data)
            return jsonify(result)
            
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400
        except Exception as e:
            server.logger.error(f"Agent registration failed: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @server.app.route('/api/v3/agents/heartbeat', methods=['POST'])
    @server.app.route('/api/agents/heartbeat', methods=['POST'])  # Legacy support
    def ultimate_agent_heartbeat():
        """Process Ultimate agent heartbeat"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "No data provided"}), 400
            
            result = server.process_agent_heartbeat(data)
            return jsonify(result)
            
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400
        except Exception as e:
            server.logger.error(f"Heartbeat processing failed: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @server.app.route('/api/v3/agents', methods=['GET'])
    def get_enhanced_agents():
        """Get enhanced agent information with Ultimate Agent API details"""
        try:
            # Get agent list with current status
            agents_list = []
            for agent_id, agent_info in server.agents.items():
                agent_status = server.agent_status.get(agent_id)
                if agent_status:
                    info_json = serialize_for_json(agent_info)
                    status_json = serialize_for_json(agent_status)

                    if not isinstance(info_json, dict):
                        info_json = {"agent_info": info_json}

                    if not isinstance(status_json, dict):
                        status_json = {"agent_status": status_json}

                    # Enhanced agent data with Ultimate Agent API capabilities
                    agent_data = {
                        **info_json, 
                        **status_json,
                        # Ultimate Agent API specific fields
                        "ultimate_agent_api": {
                            "dashboard_port": getattr(agent_info, 'dashboard_port', 8080),
                            "api_endpoints": {
                                "stats": f"http://{agent_info.host}:8080/api/stats",
                                "enhanced_stats": f"http://{agent_info.host}:8080/api/v3/stats/enhanced",
                                "ai_capabilities": f"http://{agent_info.host}:8080/api/v3/ai/capabilities",
                                "blockchain_enhanced": f"http://{agent_info.host}:8080/api/v3/blockchain/enhanced",
                                "training_status": f"http://{agent_info.host}:8080/api/training",
                                "performance_metrics": f"http://{agent_info.host}:8080/api/performance/metrics",
                                "system_info": f"http://{agent_info.host}:8080/api/system",
                                "capabilities": f"http://{agent_info.host}:8080/api/capabilities",
                                "tasks": f"http://{agent_info.host}:8080/api/tasks",
                                "start_task": f"http://{agent_info.host}:8080/api/start_task",
                                "ai_inference": f"http://{agent_info.host}:8080/api/ai/inference",
                                "blockchain_balance": f"http://{agent_info.host}:8080/api/blockchain/balance",
                                "smart_contract": f"http://{agent_info.host}:8080/api/blockchain/smart-contract/execute",
                                "database_stats": f"http://{agent_info.host}:8080/api/database/stats",
                                "network_status": f"http://{agent_info.host}:8080/api/network",
                                "activity": f"http://{agent_info.host}:8080/api/activity"
                            },
                            "websocket_url": f"ws://{agent_info.host}:8080/socket.io/",
                            "dashboard_url": f"http://{agent_info.host}:8080",
                            "api_version": "v4",
                            "modular_architecture": True,
                            "enhanced_features": True
                        }
                    }
                    agents_list.append(agent_data)

            # Get enhanced statistics
            stats = server.get_enhanced_node_stats()

            return jsonify({
                "success": True,
                "node_id": NODE_ID,
                "node_version": NODE_VERSION,
                "timestamp": datetime.now().isoformat(),
                "agents": agents_list,
                "stats": stats,
                "ai_summary": server.get_ai_summary(),
                "blockchain_summary": server.get_blockchain_summary(),
                "ultimate_agent_integration": {
                    "enabled": True,
                    "total_agents_with_api": len(agents_list),
                    "supported_features": [
                        "ai_inference", "blockchain_operations", "smart_contracts",
                        "performance_monitoring", "remote_management", "websocket_events",
                        "task_control", "neural_training", "database_operations",
                        "system_monitoring", "activity_tracking"
                    ]
                }
            })

        except Exception as e:
            server.logger.error(f"Failed to get agents: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @server.app.route('/api/v3/agents/<agent_id>', methods=['GET'])
    def get_agent_details(agent_id):
        """Get detailed information about a specific agent with Ultimate API integration"""
        try:
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            agent_info = server.agents[agent_id]
            agent_status = server.agent_status.get(agent_id)
            
            # Get recent heartbeats
            recent_heartbeats = server.db.get_recent_heartbeats(agent_id, 10)
            
            # Get performance history
            performance_history = list(server.performance_history.get(agent_id, []))
            
            # Try to fetch Ultimate Agent API data
            ultimate_api_data = {}
            try:
                base_url = f"http://{agent_info.host}:8080"
                
                # Fetch basic stats
                stats_response = requests.get(f"{base_url}/api/stats", timeout=5)
                if stats_response.status_code == 200:
                    ultimate_api_data["basic_stats"] = stats_response.json()
                
                # Fetch enhanced stats
                enhanced_response = requests.get(f"{base_url}/api/v3/stats/enhanced", timeout=5)
                if enhanced_response.status_code == 200:
                    ultimate_api_data["enhanced_stats"] = enhanced_response.json()
                
                # Fetch AI capabilities
                ai_response = requests.get(f"{base_url}/api/v3/ai/capabilities", timeout=5)
                if ai_response.status_code == 200:
                    ultimate_api_data["ai_capabilities"] = ai_response.json()
                
                # Fetch blockchain status
                blockchain_response = requests.get(f"{base_url}/api/v3/blockchain/enhanced", timeout=5)
                if blockchain_response.status_code == 200:
                    ultimate_api_data["blockchain_status"] = blockchain_response.json()
                
                # Fetch training status
                training_response = requests.get(f"{base_url}/api/training", timeout=5)
                if training_response.status_code == 200:
                    ultimate_api_data["training_status"] = training_response.json()
                
                # Fetch performance metrics
                metrics_response = requests.get(f"{base_url}/api/performance/metrics", timeout=5)
                if metrics_response.status_code == 200:
                    ultimate_api_data["performance_metrics"] = metrics_response.json()
                
                # Fetch system info
                system_response = requests.get(f"{base_url}/api/system", timeout=5)
                if system_response.status_code == 200:
                    ultimate_api_data["system_info"] = system_response.json()
                
                # Fetch capabilities
                capabilities_response = requests.get(f"{base_url}/api/capabilities", timeout=5)
                if capabilities_response.status_code == 200:
                    ultimate_api_data["capabilities"] = capabilities_response.json()
                
                # Fetch current tasks
                tasks_response = requests.get(f"{base_url}/api/tasks", timeout=5)
                if tasks_response.status_code == 200:
                    ultimate_api_data["current_tasks"] = tasks_response.json()
                
                # Mark API as available
                ultimate_api_data["api_available"] = True
                ultimate_api_data["api_url"] = base_url
                    
            except Exception as api_error:
                server.logger.warning(f"Could not fetch Ultimate Agent API data for {agent_id}: {api_error}")
                ultimate_api_data["api_error"] = str(api_error)
                ultimate_api_data["api_available"] = False
            
            result = {
                "agent_info": serialize_for_json(agent_info),
                "current_status": serialize_for_json(agent_status) if agent_status else None,
                "recent_heartbeats": [
                    {
                        "timestamp": hb.timestamp.isoformat(),
                        "cpu_percent": hb.cpu_percent,
                        "memory_percent": hb.memory_percent,
                        "gpu_percent": hb.gpu_percent,
                        "tasks_running": hb.tasks_running,
                        "efficiency_score": hb.efficiency_score
                    } for hb in recent_heartbeats
                ],
                "performance_history": performance_history,
                "ultimate_agent_api": ultimate_api_data
            }
            
            return jsonify(result)
            
        except Exception as e:
            server.logger.error(f"Failed to get agent details: {e}")
            return jsonify({"error": str(e)}), 500
    
    # NEW: Ultimate Agent API Proxy Endpoints
    @server.app.route('/api/v3/agents/<agent_id>/ai/inference', methods=['POST'])
    def proxy_ai_inference(agent_id):
        """Proxy AI inference requests to Ultimate Agent"""
        try:
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            agent_info = server.agents[agent_id]
            data = request.get_json()
            
            # Forward request to Ultimate Agent
            response = requests.post(
                f"http://{agent_info.host}:8080/api/ai/inference",
                json=data,
                timeout=30
            )
            
            return jsonify(response.json()), response.status_code
            
        except Exception as e:
            return jsonify({"error": f"Inference request failed: {str(e)}"}), 500
    
    @server.app.route('/api/v3/agents/<agent_id>/start_task', methods=['POST'])
    def proxy_start_task(agent_id):
        """Proxy task start requests to Ultimate Agent"""
        try:
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            agent_info = server.agents[agent_id]
            data = request.get_json()
            
            # Forward request to Ultimate Agent
            response = requests.post(
                f"http://{agent_info.host}:8080/api/start_task",
                json=data,
                timeout=10
            )
            
            return jsonify(response.json()), response.status_code
            
        except Exception as e:
            return jsonify({"error": f"Task start request failed: {str(e)}"}), 500
    
    @server.app.route('/api/v3/agents/<agent_id>/cancel_task/<task_id>', methods=['POST'])
    def proxy_cancel_task(agent_id, task_id):
        """Proxy task cancellation to Ultimate Agent"""
        try:
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            agent_info = server.agents[agent_id]
            
            # Forward request to Ultimate Agent
            response = requests.post(
                f"http://{agent_info.host}:8080/api/cancel_task/{task_id}",
                timeout=10
            )
            
            return jsonify(response.json()), response.status_code
            
        except Exception as e:
            return jsonify({"error": f"Task cancellation failed: {str(e)}"}), 500
    
    @server.app.route('/api/v3/agents/<agent_id>/blockchain/transaction', methods=['POST'])
    def proxy_blockchain_transaction(agent_id):
        """Proxy blockchain transaction to Ultimate Agent"""
        try:
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            agent_info = server.agents[agent_id]
            data = request.get_json()
            
            # Forward request to Ultimate Agent
            response = requests.post(
                f"http://{agent_info.host}:8080/api/blockchain/smart-contract/execute",
                json=data,
                timeout=60
            )
            
            return jsonify(response.json()), response.status_code
            
        except Exception as e:
            return jsonify({"error": f"Blockchain transaction failed: {str(e)}"}), 500
    
    @server.app.route('/api/v3/agents/<agent_id>/blockchain/balance', methods=['GET'])
    def proxy_blockchain_balance(agent_id):
        """Proxy blockchain balance request to Ultimate Agent"""
        try:
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            agent_info = server.agents[agent_id]
            
            # Forward request to Ultimate Agent
            response = requests.get(
                f"http://{agent_info.host}:8080/api/blockchain/balance",
                timeout=10
            )
            
            return jsonify(response.json()), response.status_code
            
        except Exception as e:
            return jsonify({"error": f"Balance request failed: {str(e)}"}), 500
    
    @server.app.route('/api/v3/agents/<agent_id>/remote/command', methods=['POST'])
    def proxy_remote_command(agent_id):
        """Proxy remote command to Ultimate Agent"""
        try:
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            agent_info = server.agents[agent_id]
            data = request.get_json()
            
            # Forward request to Ultimate Agent
            response = requests.post(
                f"http://{agent_info.host}:8080/api/v4/remote/command",
                json=data,
                timeout=30
            )
            
            return jsonify(response.json()), response.status_code
            
        except Exception as e:
            return jsonify({"error": f"Remote command failed: {str(e)}"}), 500
    
    @server.app.route('/api/v3/ultimate-agent-summary')
    def get_ultimate_agent_summary():
        """Get summary of all Ultimate Agent API capabilities across agents"""
        try:
            summary = {
                "total_agents": len(server.agents),
                "agents_with_api": 0,
                "total_ai_models": 0,
                "total_blockchain_balance": 0.0,
                "total_training_sessions": 0,
                "total_tasks_running": 0,
                "total_tasks_completed": 0,
                "api_endpoints_available": [],
                "agent_details": []
            }
            
            for agent_id, agent_info in server.agents.items():
                try:
                    base_url = f"http://{agent_info.host}:8080"
                    
                    # Check if agent has Ultimate API
                    response = requests.get(f"{base_url}/api/stats", timeout=3)
                    if response.status_code == 200:
                        summary["agents_with_api"] += 1
                        stats = response.json()
                        
                        agent_detail = {
                            "agent_id": agent_id,
                            "host": agent_info.host,
                            "api_url": base_url,
                            "dashboard_url": f"http://{agent_info.host}:8080",
                            "ai_models_loaded": stats.get("ai_models_loaded", 0),
                            "total_earnings": stats.get("total_earnings", 0.0),
                            "tasks_running": stats.get("current_tasks", 0),
                            "tasks_completed": stats.get("tasks_completed", 0),
                            "uptime_hours": stats.get("uptime_hours", 0),
                            "registered": stats.get("registered", False),
                            "api_status": "online"
                        }
                        
                        summary["agent_details"].append(agent_detail)
                        summary["total_ai_models"] += stats.get("ai_models_loaded", 0)
                        summary["total_blockchain_balance"] += stats.get("total_earnings", 0.0)
                        summary["total_tasks_running"] += stats.get("current_tasks", 0)
                        summary["total_tasks_completed"] += stats.get("tasks_completed", 0)
                        
                except Exception:
                    summary["agent_details"].append({
                        "agent_id": agent_id,
                        "host": agent_info.host,
                        "api_status": "offline"
                    })
            
            return jsonify(summary)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v3/agents/<agent_id>/bulk-operation', methods=['POST'])
    def proxy_bulk_operation(agent_id):
        """Execute bulk operation on Ultimate Agent"""
        try:
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            agent_info = server.agents[agent_id]
            data = request.get_json()
            
            operation = data.get('operation')
            if not operation:
                return jsonify({"error": "Operation type required"}), 400
            
            results = []
            
            # Handle different bulk operations
            if operation == 'restart_agent':
                response = requests.post(
                    f"http://{agent_info.host}:8080/api/v4/remote/command",
                    json={"command_type": "restart_agent", "parameters": data.get('parameters', {})},
                    timeout=10
                )
                results.append({"operation": "restart", "result": response.json()})
            
            elif operation == 'get_status':
                response = requests.get(f"http://{agent_info.host}:8080/api/stats", timeout=5)
                results.append({"operation": "status", "result": response.json()})
            
            elif operation == 'start_training':
                task_data = {
                    "type": data.get('task_type', 'neural_network_training'),
                    "config": data.get('config', {})
                }
                response = requests.post(
                    f"http://{agent_info.host}:8080/api/start_task",
                    json=task_data,
                    timeout=10
                )
                results.append({"operation": "training", "result": response.json()})
            
            return jsonify({
                "success": True,
                "agent_id": agent_id,
                "operation": operation,
                "results": results
            })
            
        except Exception as e:
            return jsonify({"error": f"Bulk operation failed: {str(e)}"}), 500
    
    # Existing endpoints...
    @server.app.route('/api/v3/node/stats', methods=['GET'])
    def get_node_statistics():
        """Get comprehensive node statistics"""
        try:
            stats = server.get_enhanced_node_stats()
            return jsonify(stats)
        except Exception as e:
            server.logger.error(f"Failed to get node stats: {e}")
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/stats', methods=['GET'])
    def legacy_stats():
        """Legacy stats endpoint for backward compatibility"""
        try:
            enhanced_stats = server.get_enhanced_node_stats()
            return jsonify({
                "node_id": enhanced_stats["node_id"],
                "total_agents": enhanced_stats["total_agents"],
                "online_agents": enhanced_stats["online_agents"],
                "offline_agents": enhanced_stats["offline_agents"],
                "total_tasks_running": enhanced_stats["total_tasks_running"],
                "total_tasks_completed": enhanced_stats["total_tasks_completed"],
                "avg_cpu_percent": enhanced_stats["avg_cpu_percent"],
                "avg_memory_mb": enhanced_stats.get("avg_memory_percent", 0) * 10,
                "timestamp": enhanced_stats["timestamp"],
                "task_control_enabled": True,
                "remote_management_enabled": True,
                "advanced_control_enabled": True,
                "ultimate_agent_api_enabled": True
            })
        except Exception as e:
            server.logger.error(f"Failed to get legacy stats: {e}")
            return jsonify({"error": str(e)}), 500
    
    # Health and monitoring endpoints
    @server.app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        try:
            stats = server.get_enhanced_node_stats()
            return jsonify({
                "status": "healthy",
                "health_score": stats.get("health_score", 100),
                "timestamp": datetime.now().isoformat(),
                "node_id": NODE_ID,
                "version": NODE_VERSION,
                "agents_online": stats.get("online_agents", 0),
                "services": {
                    "task_control": True,
                    "remote_management": True,
                    "websocket": True,
                    "database": True
                }
            })
        except Exception as e:
            return jsonify({
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500


def get_enhanced_dashboard_html():
    """Generate enhanced dashboard HTML with Ultimate Agent API integration"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enhanced Node Server v{NODE_VERSION} - ULTIMATE AGENT API INTEGRATION</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: radial-gradient(circle at 25% 25%, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
                color: white;
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{ max-width: 1800px; margin: 0 auto; }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding: 40px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 25px;
                backdrop-filter: blur(30px);
                border: 2px solid rgba(255, 255, 255, 0.2);
                position: relative;
                overflow: hidden;
            }}
            .header::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: conic-gradient(transparent, rgba(255, 255, 255, 0.1), transparent);
                animation: rotate 10s linear infinite;
            }}
            @keyframes rotate {{ to {{ transform: rotate(360deg); }} }}
            .header h1 {{
                font-size: 3rem;
                font-weight: 900;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #f093fb);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 15px;
                position: relative;
                z-index: 1;
            }}
            .ultimate-api-badge {{
                display: inline-block;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                padding: 10px 25px;
                border-radius: 25px;
                font-size: 1rem;
                font-weight: 700;
                margin: 10px 8px;
                position: relative;
                z-index: 1;
                animation: ultimatePulse 3s infinite;
                box-shadow: 0 0 20px rgba(255, 107, 107, 0.3);
            }}
            @keyframes ultimatePulse {{
                0%, 100% {{ box-shadow: 0 0 15px rgba(255, 107, 107, 0.3), 0 0 30px rgba(78, 205, 196, 0.2); }}
                50% {{ box-shadow: 0 0 25px rgba(78, 205, 196, 0.6), 0 0 50px rgba(255, 107, 107, 0.4); }}
            }}
            .advanced-badge {{
                display: inline-block;
                background: linear-gradient(45deg, #4ecdc4, #45b7d1);
                padding: 8px 20px;
                border-radius: 20px;
                font-size: 0.9rem;
                font-weight: 700;
                margin: 10px 5px;
                position: relative;
                z-index: 1;
            }}
            .feature-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin: 20px 0;
                position: relative;
                z-index: 1;
            }}
            .feature-badge {{
                background: rgba(255, 255, 255, 0.15);
                padding: 8px 12px;
                border-radius: 12px;
                text-align: center;
                font-weight: 600;
                backdrop-filter: blur(10px);
                font-size: 0.85rem;
                transition: all 0.3s ease;
            }}
            .feature-badge:hover {{
                background: rgba(255, 255, 255, 0.25);
                transform: translateY(-2px);
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                backdrop-filter: blur(20px);
                transition: all 0.3s ease;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .stat-card:hover {{
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.15);
            }}
            .stat-value {{
                font-size: 2.2em;
                font-weight: 700;
                color: #4ecdc4;
                margin-bottom: 8px;
            }}
            .stat-label {{
                font-size: 0.9em;
                opacity: 0.9;
            }}
            .ultimate-api-section {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 25px;
                margin: 25px 0;
                backdrop-filter: blur(20px);
                border: 2px solid rgba(78, 205, 196, 0.3);
            }}
            .agent-list {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .agent-card {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s ease;
            }}
            .agent-card:hover {{
                transform: translateY(-3px);
                border-color: rgba(78, 205, 196, 0.5);
            }}
            .api-controls {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }}
            .control-button {{
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 15px 20px;
                border-radius: 15px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }}
            .control-button:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
            }}
            .api-button {{
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            }}
            .api-button:hover {{
                background: linear-gradient(45deg, #ff5252, #26a69a);
            }}
            .loading {{
                text-align: center;
                opacity: 0.7;
                padding: 40px;
                font-style: italic;
            }}
            .api-status {{
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }}
            .api-online {{ background: #4caf50; }}
            .api-offline {{ background: #f44336; }}
            .api-warning {{ background: #ff9800; }}
            .notification {{
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 10px;
                color: white;
                font-weight: 600;
                z-index: 1000;
                animation: slideIn 0.3s ease;
            }}
            .notification.success {{ background: #4caf50; }}
            .notification.error {{ background: #f44336; }}
            .notification.warning {{ background: #ff9800; }}
            .notification.info {{ background: #2196f3; }}
            @keyframes slideIn {{ from {{ transform: translateX(100%); }} to {{ transform: translateX(0); }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Enhanced Node Server</h1>
                <div class="ultimate-api-badge">ULTIMATE AGENT API INTEGRATED</div>
                <div class="advanced-badge">MODULAR ARCHITECTURE</div>
                <div class="advanced-badge">ALL FEATURES PRESERVED</div>
                <div class="advanced-badge">API PROXY ENABLED</div>
                <p style="font-size: 1.1rem; margin: 15px 0; position: relative; z-index: 1;">
                    v{NODE_VERSION} - Ultimate Agent API Integration
                </p>
                
                <div class="feature-grid">
                    <div class="feature-badge">AI Inference API</div>
                    <div class="feature-badge">Blockchain API</div>
                    <div class="feature-badge">Task Control API</div>
                    <div class="feature-badge">Performance API</div>
                    <div class="feature-badge">Smart Contracts</div>
                    <div class="feature-badge">WebSocket Events</div>
                    <div class="feature-badge">Remote Commands</div>
                    <div class="feature-badge">Database API</div>
                    <div class="feature-badge">Security API</div>
                    <div class="feature-badge">Analytics API</div>
                    <div class="feature-badge">API Proxy</div>
                    <div class="feature-badge">Real-time Data</div>
                </div>
                
                <p style="position: relative; z-index: 1; opacity: 0.8; font-size: 0.9rem;">
                    Node ID: {NODE_ID} | Ultimate Agent API Integration Active
                </p>
            </div>
            
            <div class="stats-grid" id="statsGrid">
                <div class="loading">Loading Ultimate Agent API data...</div>
            </div>
            
            <div class="ultimate-api-section">
                <h2>Ultimate Agent API Control Center</h2>
                <div class="api-controls">
                    <button class="control-button api-button" onclick="testAllAgentAPIs()">
                        Test All Agent APIs
                    </button>
                    <button class="control-button api-button" onclick="runAIInference()">
                        Run AI Inference
                    </button>
                    <button class="control-button api-button" onclick="executeSmartContract()">
                        Execute Smart Contract
                    </button>
                    <button class="control-button api-button" onclick="startTrainingAcrossAgents()">
                        Start Training (All Agents)
                    </button>
                    <button class="control-button api-button" onclick="getPerformanceMetrics()">
                        Get Performance Metrics
                    </button>
                    <button class="control-button api-button" onclick="showUltimateApiSummary()">
                        Ultimate API Summary
                    </button>
                    <button class="control-button api-button" onclick="bulkRestartAgents()">
                        Bulk Restart Agents
                    </button>
                    <button class="control-button api-button" onclick="getBlockchainBalances()">
                        Get All Balances
                    </button>
                </div>
            </div>
            
            <div class="ultimate-api-section" id="agentApiSection">
                <h2>Agents with Ultimate API</h2>
                <div class="agent-list" id="agentsList">
                    <div class="loading">Loading agent API data...</div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 40px;">
                <button class="control-button" onclick="refreshData()">
                    Refresh Data
                </button>
                <button class="control-button api-button" onclick="openApiDocumentation()">
                    Ultimate API Docs
                </button>
            </div>
        </div>
        
        <script>
            let socket;
            let agentsWithApi = [];
            
            document.addEventListener('DOMContentLoaded', () => {{
                initSocket();
                refreshData();
                loadUltimateApiSummary();
                setInterval(refreshData, 10000); // Update every 10 seconds
            }});
            
            function initSocket() {{
                try {{
                    socket = io();
                    socket.on('connect', () => console.log('Connected to Enhanced Node Server with Ultimate API'));
                    socket.on('ultimate_agent_registered', (data) => {{
                        console.log('Ultimate Agent registered:', data);
                        refreshData();
                    }});
                    socket.on('ultimate_agent_status_update', (data) => {{
                        console.log('Ultimate Agent status update:', data);
                        refreshData();
                    }});
                }} catch (e) {{
                    console.log('WebSocket not available');
                }}
            }}
            
            async function refreshData() {{
                try {{
                    const response = await fetch('/api/v3/agents');
                    const data = await response.json();
                    
                    updateStats(data.stats);
                    updateAgentsList(data.agents);
                    
                }} catch (error) {{
                    console.error('Failed to refresh data:', error);
                }}
            }}
            
            async function loadUltimateApiSummary() {{
                try {{
                    const response = await fetch('/api/v3/ultimate-agent-summary');
                    const summary = await response.json();
                    console.log('Ultimate Agent API Summary:', summary);
                    agentsWithApi = summary.agent_details || [];
                }} catch (error) {{
                    console.error('Failed to load Ultimate API summary:', error);
                }}
            }}
            
            function updateStats(stats) {{
                const statsGrid = document.getElementById('statsGrid');
                statsGrid.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-value">${{stats.total_agents}}</div>
                        <div class="stat-label">Total Agents</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${{stats.online_agents}}</div>
                        <div class="stat-label">Online Agents</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${{stats.total_tasks_running}}</div>
                        <div class="stat-label">Tasks Running</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${{stats.total_ai_models}}</div>
                        <div class="stat-label">AI Models</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${{stats.total_blockchain_balance.toFixed(3)}}</div>
                        <div class="stat-label">Total ETH Balance</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${{stats.avg_efficiency_score.toFixed(1)}}%</div>
                        <div class="stat-label">Avg Efficiency</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${{stats.health_score.toFixed(0)}}%</div>
                        <div class="stat-label">Health Score</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">API</div>
                        <div class="stat-label">Ultimate Integration</div>
                    </div>
                `;
            }}
            
            function updateAgentsList(agents) {{
                const agentsList = document.getElementById('agentsList');
                
                if (!agents || agents.length === 0) {{
                    agentsList.innerHTML = '<div class="loading">No agents registered</div>';
                    return;
                }}
                
                agentsList.innerHTML = agents.map(agent => {{
                    const apiData = agent.ultimate_agent_api || {{}};
                    const hasApi = apiData.api_endpoints ? true : false;
                    
                    return `
                        <div class="agent-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <h3>${{agent.name || agent.id}}</h3>
                                <span class="api-status ${{hasApi ? 'api-online' : 'api-offline'}}"></span>
                            </div>
                            <div style="margin-bottom: 10px;">
                                <strong>Host:</strong> ${{agent.host}}:${{apiData.dashboard_port || 8080}}
                            </div>
                            <div style="margin-bottom: 10px;">
                                <strong>Status:</strong> ${{agent.status || 'unknown'}}
                            </div>
                            ${{hasApi ? `
                                <div style="margin-bottom: 10px;">
                                    <strong>API Version:</strong> ${{apiData.api_version}}
                                </div>
                                <div style="margin-bottom: 15px;">
                                    <strong>Features:</strong> AI, Blockchain, WebSocket, Remote Control
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                                    <button class="control-button" style="padding: 8px; font-size: 0.8em;" 
                                            onclick="testAgentAPI('${{agent.id}}')">
                                        Test API
                                    </button>
                                    <button class="control-button api-button" style="padding: 8px; font-size: 0.8em;" 
                                            onclick="openAgentDashboard('${{agent.host}}', ${{apiData.dashboard_port || 8080}})">
                                        Dashboard
                                    </button>
                                </div>
                            ` : `
                                <div style="color: #ff9800; font-style: italic;">
                                    Ultimate Agent API not available
                                </div>
                            `}}
                        </div>
                    `;
                }}).join('');
            }}
            
            async function testAllAgentAPIs() {{
                showNotification('Testing all agent APIs...', 'info');
                
                try {{
                    const response = await fetch('/api/v3/ultimate-agent-summary');
                    const summary = await response.json();
                    
                    let results = `Ultimate Agent API Test Results:\\n\\n`;
                    results += `Total Agents: ${{summary.total_agents}}\\n`;
                    results += `Agents with API: ${{summary.agents_with_api}}\\n`;
                    results += `Total AI Models: ${{summary.total_ai_models}}\\n`;
                    results += `Total Balance: ${{summary.total_blockchain_balance.toFixed(4)}} ETH\\n\\n`;
                    
                    summary.agent_details.forEach(agent => {{
                        results += `Agent ${{agent.agent_id}}:\\n`;
                        results += `  - API: ${{agent.api_url}}\\n`;
                        results += `  - AI Models: ${{agent.ai_models_loaded}}\\n`;
                        results += `  - Tasks: ${{agent.tasks_running}} running, ${{agent.tasks_completed}} completed\\n`;
                        results += `  - Earnings: ${{agent.total_earnings.toFixed(4)}} ETH\\n\\n`;
                    }});
                    
                    alert(results);
                    showNotification('API test completed!', 'success');
                    
                }} catch (error) {{
                    console.error('API test failed:', error);
                    showNotification('API test failed!', 'error');
                }}
            }}
            
            async function runAIInference() {{
                if (agentsWithApi.length === 0) {{
                    showNotification('No agents with Ultimate API available', 'warning');
                    return;
                }}
                
                const agentId = agentsWithApi[0].agent_id;
                const text = prompt('Enter text for sentiment analysis:', 'This Ultimate Agent API integration is amazing!');
                
                if (!text) return;
                
                try {{
                    showNotification('Running AI inference...', 'info');
                    
                    const response = await fetch(`/api/v3/agents/${{agentId}}/ai/inference`, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            model: 'sentiment',
                            input: text,
                            options: {{ return_confidence: true }}
                        }})
                    }});
                    
                    const result = await response.json();
                    
                    if (result.success) {{
                        alert(`AI Inference Result:\\n\\nText: "${{text}}"\\nSentiment: ${{result.prediction}}\\nConfidence: ${{(result.confidence * 100).toFixed(1)}}%`);
                        showNotification('AI inference completed!', 'success');
                    }} else {{
                        throw new Error(result.error);
                    }}
                    
                }} catch (error) {{
                    console.error('AI inference failed:', error);
                    showNotification('AI inference failed!', 'error');
                }}
            }}
            
            async function executeSmartContract() {{
                if (agentsWithApi.length === 0) {{
                    showNotification('No agents with Ultimate API available', 'warning');
                    return;
                }}
                
                const agentId = agentsWithApi[0].agent_id;
                const amount = prompt('Enter reward amount (ETH):', '0.1');
                
                if (!amount) return;
                
                try {{
                    showNotification('Executing smart contract...', 'info');
                    
                    const response = await fetch(`/api/v3/agents/${{agentId}}/blockchain/transaction`, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            contract_type: 'task_rewards',
                            method: 'claimReward',
                            params: {{
                                amount: parseFloat(amount),
                                task_id: `task-${{Date.now()}}`
                            }}
                        }})
                    }});
                    
                    const result = await response.json();
                    
                    if (result.success) {{
                        alert(`Smart Contract Executed!\\n\\nTransaction Hash: ${{result.transaction_hash}}\\nAmount: ${{amount}} ETH\\nGas Used: ${{result.gas_used}}`);
                        showNotification('Smart contract executed!', 'success');
                    }} else {{
                        throw new Error(result.error);
                    }}
                    
                }} catch (error) {{
                    console.error('Smart contract execution failed:', error);
                    showNotification('Smart contract execution failed!', 'error');
                }}
            }}
            
            async function startTrainingAcrossAgents() {{
                if (agentsWithApi.length === 0) {{
                    showNotification('No agents with Ultimate API available', 'warning');
                    return;
                }}
                
                const taskType = prompt('Enter training task type:', 'neural_network_training');
                if (!taskType) return;
                
                try {{
                    showNotification('Starting training across all agents...', 'info');
                    
                    const results = [];
                    for (const agent of agentsWithApi) {{
                        try {{
                            const response = await fetch(`/api/v3/agents/${{agent.agent_id}}/start_task`, {{
                                method: 'POST',
                                headers: {{ 'Content-Type': 'application/json' }},
                                body: JSON.stringify({{
                                    type: taskType,
                                    config: {{ epochs: 10, batch_size: 32 }}
                                }})
                            }});
                            
                            const result = await response.json();
                            results.push({{
                                agent_id: agent.agent_id,
                                success: result.success,
                                task_id: result.task_id,
                                error: result.error
                            }});
                        }} catch (error) {{
                            results.push({{
                                agent_id: agent.agent_id,
                                success: false,
                                error: error.message
                            }});
                        }}
                    }}
                    
                    let summary = `Training Started Across Agents:\\n\\n`;
                    results.forEach(r => {{
                        summary += `Agent ${{r.agent_id}}: `;
                        summary += r.success ? `Task ${{r.task_id}}` : `Error: ${{r.error}}`;
                        summary += `\\n`;
                    }});
                    
                    alert(summary);
                    showNotification('Bulk training initiated!', 'success');
                    
                }} catch (error) {{
                    console.error('Bulk training failed:', error);
                    showNotification('Bulk training failed!', 'error');
                }}
            }}
            
            async function bulkRestartAgents() {{
                if (agentsWithApi.length === 0) {{
                    showNotification('No agents with Ultimate API available', 'warning');
                    return;
                }}
                
                if (!confirm('This will restart all agents with Ultimate API. Continue?')) return;
                
                try {{
                    showNotification('Restarting all agents...', 'info');
                    
                    const results = [];
                    for (const agent of agentsWithApi) {{
                        try {{
                            const response = await fetch(`/api/v3/agents/${{agent.agent_id}}/bulk-operation`, {{
                                method: 'POST',
                                headers: {{ 'Content-Type': 'application/json' }},
                                body: JSON.stringify({{
                                    operation: 'restart_agent',
                                    parameters: {{ delay: 5 }}
                                }})
                            }});
                            
                            const result = await response.json();
                            results.push({{
                                agent_id: agent.agent_id,
                                success: result.success
                            }});
                        }} catch (error) {{
                            results.push({{
                                agent_id: agent.agent_id,
                                success: false,
                                error: error.message
                            }});
                        }}
                    }}
                    
                    const successful = results.filter(r => r.success).length;
                    showNotification(`Restart command sent to ${{successful}}/${{results.length}} agents`, 'success');
                    
                }} catch (error) {{
                    console.error('Bulk restart failed:', error);
                    showNotification('Bulk restart failed!', 'error');
                }}
            }}
            
            async function getBlockchainBalances() {{
                if (agentsWithApi.length === 0) {{
                    showNotification('No agents with Ultimate API available', 'warning');
                    return;
                }}
                
                try {{
                    showNotification('Getting blockchain balances...', 'info');
                    
                    const results = [];
                    for (const agent of agentsWithApi) {{
                        try {{
                            const response = await fetch(`/api/v3/agents/${{agent.agent_id}}/blockchain/balance`);
                            const result = await response.json();
                            results.push({{
                                agent_id: agent.agent_id,
                                balances: result.balances || {{}},
                                total_value: result.total_value_usd || 0
                            }});
                        }} catch (error) {{
                            results.push({{
                                agent_id: agent.agent_id,
                                error: error.message
                            }});
                        }}
                    }}
                    
                    let summary = 'Blockchain Balances:\\n\\n';
                    results.forEach(r => {{
                        summary += `Agent ${{r.agent_id}}:\\n`;
                        if (r.balances) {{
                            Object.entries(r.balances).forEach(([currency, amount]) => {{
                                summary += `  ${{currency}}: ${{amount}}\\n`;
                            }});
                            summary += `  Total Value: $$${{r.total_value}}\\n\\n`;
                        }} else {{
                            summary += `  Error: ${{r.error}}\\n\\n`;
                        }}
                    }});
                    
                    alert(summary);
                    showNotification('Balance check completed!', 'success');
                    
                }} catch (error) {{
                    console.error('Balance check failed:', error);
                    showNotification('Balance check failed!', 'error');
                }}
            }}
            
            async function testAgentAPI(agentId) {{
                try {{
                    showNotification(`Testing API for ${{agentId}}...`, 'info');
                    
                    const response = await fetch(`/api/v3/agents/${{agentId}}`);
                    const data = await response.json();
                    
                    const apiData = data.ultimate_agent_api;
                    if (apiData && !apiData.api_error) {{
                        alert(`${{agentId}} API Test Successful!\\n\\nAPI Available: ${{apiData.api_available}}\\nAPI URL: ${{apiData.api_url}}`);
                        showNotification('API test successful!', 'success');
                    }} else {{
                        throw new Error(apiData.api_error || 'API not available');
                    }}
                    
                }} catch (error) {{
                    console.error(`API test failed for ${{agentId}}:`, error);
                    showNotification(`API test failed for ${{agentId}}!`, 'error');
                }}
            }}
            
            function openAgentDashboard(host, port) {{
                const url = `http://${{host}}:${{port}}`;
                window.open(url, '_blank');
            }}
            
            function openApiDocumentation() {{
                alert('Ultimate Agent API Documentation\\n\\nComprehensive API documentation is available in the ultimate_agent_api_docs.md file.\\n\\nKey endpoints:\\n- /api/stats - Agent statistics\\n- /api/v3/ai/capabilities - AI capabilities\\n- /api/v3/blockchain/enhanced - Blockchain status\\n- /api/start_task - Start tasks\\n- /api/ai/inference - Run AI inference\\n- WebSocket events for real-time updates');
            }}
            
            function showNotification(message, type) {{
                const notification = document.createElement('div');
                notification.className = `notification ${{type}}`;
                notification.textContent = message;
                document.body.appendChild(notification);
                
                setTimeout(() => {{
                    notification.remove();
                }}, 3000);
                
                console.log(`[${{type.toUpperCase()}}] ${{message}}`);
            }}
            
            function showUltimateApiSummary() {{
                loadUltimateApiSummary().then(() => {{
                    let summary = 'Ultimate Agent API Integration Summary\\n\\n';
                    summary += `Total Agents with API: ${{agentsWithApi.length}}\\n`;
                    summary += `Total AI Models: ${{agentsWithApi.reduce((sum, a) => sum + a.ai_models_loaded, 0)}}\\n`;
                    summary += `Total Earnings: ${{agentsWithApi.reduce((sum, a) => sum + a.total_earnings, 0).toFixed(4)}} ETH\\n`;
                    summary += `Total Tasks Completed: ${{agentsWithApi.reduce((sum, a) => sum + a.tasks_completed, 0)}}\\n\\n`;
                    summary += 'Available API Features:\\n';
                    summary += '• AI Inference & Training\\n';
                    summary += '• Blockchain & Smart Contracts\\n';
                    summary += '• Performance Monitoring\\n';
                    summary += '• Real-time WebSocket Events\\n';
                    summary += '• Remote Command Execution\\n';
                    summary += '• Database Operations\\n';
                    summary += '• Task Control & Management\\n';
                    summary += '• Bulk Operations\\n';
                    alert(summary);
                }});
            }}
            
            console.log('Enhanced Node Server Dashboard with Ultimate Agent API Integration Ready');
            console.log('Features: API Proxy, Real-time Integration, Multi-Agent Control');
        </script>
    </body>
    </html>
    """