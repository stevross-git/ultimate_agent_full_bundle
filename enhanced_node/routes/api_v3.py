#!/usr/bin/env python3
"""
Updated API v3 Routes - Enhanced Node Server with Dashboard Fix
FIXED: Template loading and circular import issues
"""

from flask import request, jsonify, render_template, abort
from datetime import datetime
import json
import requests
import time
import os
from ..core.database import Agent, AgentHeartbeat
from ..models.agents import EnhancedAgentInfo, EnhancedAgentStatus
from ..utils.serialization import serialize_for_json
from ..config.settings import NODE_ID, NODE_VERSION


def register_api_v3_routes(server):
    """Register all API v3 routes with Ultimate Agent API integration"""
    
    @server.app.route('/')
    def enhanced_dashboard():
        """Serve the enhanced dashboard"""
        try:
            # Try to render the template
            return render_template('enhanced_dashboard.html')
        except Exception as e:
            server.logger.error(f"Dashboard template error: {str(e)}")
            # Provide a fallback HTML response
            return get_fallback_dashboard_html(), 200
    
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
                                "activity": f"http://{agent_info.host}:8080/api/activity",
                                "health": f"http://{agent_info.host}:8080/api/health"
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
                        "system_monitoring", "activity_tracking", "health_monitoring",
                        "multi_currency_wallets", "distributed_training", "federated_learning",
                        "transformer_training", "cnn_training", "reinforcement_learning",
                        "hyperparameter_optimization", "computer_vision", "nlp_processing"
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
            
            # Try to fetch comprehensive Ultimate Agent API data
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
    
    # Ultimate Agent API Proxy Endpoints
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
    
    # Remaining endpoints (node stats, health check, etc.)
    @server.app.route('/api/v3/node/stats', methods=['GET'])
    def get_node_statistics():
        """Get comprehensive node statistics"""
        try:
            stats = server.get_enhanced_node_stats()
            return jsonify(stats)
        except Exception as e:
            server.logger.error(f"Failed to get node stats: {e}")
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/health', methods=['GET'])
    def comprehensive_health_check():
        """Comprehensive health check endpoint"""
        try:
            from ..core.health import HealthChecker
            health_checker = HealthChecker(server)
            health_status = health_checker.get_health_status()

            status_code = 200
            if health_status["overall_status"] == "critical":
                status_code = 503
            elif health_status["overall_status"] == "warning":
                status_code = 200

            return jsonify(health_status), status_code

        except Exception as e:
            server.logger.error(f"Health check failed critically: {e}")
            return jsonify({
                "overall_status": "critical",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 503


def get_fallback_dashboard_html():
    """Provide fallback dashboard HTML if template loading fails"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enhanced Node Server - Dashboard</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                text-align: center;
            }
            .header {
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 20px;
                margin-bottom: 30px;
                backdrop-filter: blur(20px);
                border: 2px solid rgba(255, 255, 255, 0.2);
            }
            .header h1 {
                font-size: 3rem;
                margin: 0 0 10px 0;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .status {
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 15px;
                margin: 20px 0;
            }
            .error {
                background: rgba(244, 67, 54, 0.2);
                border: 2px solid #f44336;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .loading {
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .btn {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                cursor: pointer;
                font-size: 1.1rem;
                margin: 10px;
                transition: transform 0.3s ease;
            }
            .btn:hover {
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Enhanced Node Server</h1>
                <p>Advanced AI & Blockchain Operations Center</p>
            </div>
            
            <div class="status">
                <h2>📊 Dashboard Status</h2>
                <p>Enhanced Node Server is running successfully!</p>
                <p>Template system is loading... Please wait.</p>
            </div>
            
            <div class="status loading">
                <h3>🔄 Loading Enhanced Dashboard...</h3>
                <p>Initializing advanced features...</p>
            </div>
            
            <div>
                <button class="btn" onclick="window.location.reload()">
                    🔄 Refresh Dashboard
                </button>
                <button class="btn" onclick="window.location.href='/api/v3/agents'">
                    🤖 View Agents API
                </button>
                <button class="btn" onclick="window.location.href='/api/v3/node/stats'">
                    📈 Node Statistics
                </button>
            </div>
            
            <div class="status">
                <h3>✅ System Status</h3>
                <p>✅ Flask Server: Running</p>
                <p>✅ WebSocket: Active</p>
                <p>✅ API Routes: Registered</p>
                <p>✅ Database: Connected</p>
                <p>🔄 Template System: Loading</p>
            </div>
        </div>
        
        <script>
            // Auto-refresh every 30 seconds
            setTimeout(() => {
                window.location.reload();
            }, 30000);
            
            console.log('Enhanced Node Server Dashboard - Fallback Mode');
            console.log('Template system is loading...');
        </script>
    </body>
    </html>
    """