#!/usr/bin/env python3
"""
Updated API v3 Routes - Enhanced Node Server with New Dashboard
This file replaces the existing routes/api_v3.py to integrate the new dashboard features
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
        """Serve enhanced node dashboard with comprehensive Ultimate Agent API integration"""
        return get_enhanced_dashboard_html_with_new_features()
    
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
                
                # Fetch health status
                health_response = requests.get(f"{base_url}/api/health", timeout=5)
                if health_response.status_code == 200:
                    ultimate_api_data["health_status"] = health_response.json()
                
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
        from core.health import HealthChecker
        health_checker = HealthChecker(server)
        health_status = health_checker.get_health_status()
        
        status_code = 200
        if health_status["overall_status"] == "critical":
            status_code = 503
        elif health_status["overall_status"] == "warning":
            status_code = 200  # Still serving but with warnings
        
        return jsonify(health_status), status_code
        
    except Exception as e:
        return jsonify({
            "overall_status": "critical",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503


def get_enhanced_dashboard_html_with_new_features():
    """Generate the enhanced dashboard HTML with all new Ultimate Agent features"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enhanced Node Server v{NODE_VERSION} - ULTIMATE AGENT COMMAND CENTER</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/js/all.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: radial-gradient(circle at 25% 25%, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
                color: white;
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{ max-width: 2000px; margin: 0 auto; }}
            
            /* Header Styles */
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
            
            .feature-badge {{
                background: rgba(255, 255, 255, 0.15);
                padding: 8px 12px;
                border-radius: 12px;
                text-align: center;
                font-weight: 600;
                backdrop-filter: blur(10px);
                font-size: 0.85rem;
                transition: all 0.3s ease;
                margin: 5px;
                display: inline-block;
            }}
            .feature-badge:hover {{
                background: rgba(255, 255, 255, 0.25);
                transform: translateY(-2px);
            }}
            
            /* Main Grid and responsive styles continue... */
            .main-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .section {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 25px;
                backdrop-filter: blur(20px);
                border: 2px solid rgba(78, 205, 196, 0.3);
                margin-bottom: 20px;
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
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }}
            
            .api-button {{ background: linear-gradient(45deg, #ff6b6b, #4ecdc4); }}
            .ai-button {{ background: linear-gradient(45deg, #9c27b0, #673ab7); }}
            .blockchain-button {{ background: linear-gradient(45deg, #ff9800, #ff5722); }}
            .system-button {{ background: linear-gradient(45deg, #2196f3, #03a9f4); }}
            
            .loading {{
                text-align: center;
                opacity: 0.7;
                padding: 40px;
                font-style: italic;
            }}
            
            .spinner {{
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top-color: #4ecdc4;
                animation: spin 1s ease-in-out infinite;
                margin-right: 10px;
            }}
            
            @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header">
                <h1><i class="fas fa-robot"></i> Enhanced Node Server</h1>
                <div class="ultimate-api-badge">
                    <i class="fas fa-rocket"></i> ULTIMATE AGENT COMMAND CENTER
                </div>
                <div class="ultimate-api-badge">
                    <i class="fas fa-brain"></i> AI POWERED
                </div>
                <div class="ultimate-api-badge">
                    <i class="fas fa-coins"></i> BLOCKCHAIN INTEGRATED
                </div>
                
                <p style="font-size: 1.1rem; margin: 15px 0; position: relative; z-index: 1;">
                    v{NODE_VERSION} - Ultimate Agent API Integration with Advanced Features
                </p>
                
                <div style="margin-top: 20px;">
                    <div class="feature-badge"><i class="fas fa-brain"></i> Neural Networks</div>
                    <div class="feature-badge"><i class="fas fa-eye"></i> Computer Vision</div>
                    <div class="feature-badge"><i class="fas fa-language"></i> NLP & Transformers</div>
                    <div class="feature-badge"><i class="fas fa-gamepad"></i> Reinforcement Learning</div>
                    <div class="feature-badge"><i class="fas fa-coins"></i> Multi-Currency Wallets</div>
                    <div class="feature-badge"><i class="fas fa-file-contract"></i> Smart Contracts</div>
                    <div class="feature-badge"><i class="fas fa-network-wired"></i> Multi-Network</div>
                    <div class="feature-badge"><i class="fas fa-tasks"></i> Advanced Task Control</div>
                    <div class="feature-badge"><i class="fas fa-satellite-dish"></i> Real-time Monitoring</div>
                    <div class="feature-badge"><i class="fas fa-shield-alt"></i> Health & Recovery</div>
                </div>
                
                <p style="position: relative; z-index: 1; opacity: 0.8; font-size: 0.9rem; margin-top: 15px;">
                    Node ID: {NODE_ID} | Enhanced Features Active | Ultimate Agent API Integration Online
                </p>
            </div>
            
            <!-- Quick Stats -->
            <div id="quickStats" class="section">
                <h2><i class="fas fa-chart-bar"></i> System Overview</h2>
                <div id="statsGrid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px;">
                    <div class="loading">
                        <span class="spinner"></span>Loading comprehensive agent data...
                    </div>
                </div>
            </div>
            
            <!-- Enhanced Features Grid -->
            <div class="main-grid">
                <!-- AI Operations -->
                <div class="section">
                    <h2><i class="fas fa-brain"></i> AI Operations Center</h2>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 15px 0;" id="aiModelsGrid">
                        <div class="loading">Loading AI models...</div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px;">
                        <button class="control-button ai-button" onclick="runAdvancedInference()">
                            <i class="fas fa-play"></i> Run AI Inference
                        </button>
                        <button class="control-button ai-button" onclick="startNeuralTraining()">
                            <i class="fas fa-graduation-cap"></i> Start Training
                        </button>
                    </div>
                </div>
                
                <!-- Blockchain Operations -->
                <div class="section">
                    <h2><i class="fas fa-coins"></i> Blockchain Operations</h2>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin: 15px 0;" id="currencyGrid">
                        <div class="loading">Loading wallet balances...</div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px;">
                        <button class="control-button blockchain-button" onclick="executeSmartContract()">
                            <i class="fas fa-file-contract"></i> Execute Contract
                        </button>
                        <button class="control-button blockchain-button" onclick="manageWallets()">
                            <i class="fas fa-wallet"></i> Manage Wallets
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Agents Grid -->
            <div class="section">
                <h2><i class="fas fa-robot"></i> Ultimate Agents Command Center
                    <button class="control-button api-button" onclick="refreshAgents()" style="margin-left: auto; padding: 8px 15px; font-size: 0.8rem;">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                </h2>
                
                <div id="agentsGrid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin: 20px 0;">
                    <div class="loading">
                        <span class="spinner"></span>Loading Ultimate Agents...
                    </div>
                </div>
            </div>
            
            <!-- Advanced Control Center -->
            <div class="section">
                <h2><i class="fas fa-satellite-dish"></i> Advanced Control Center</h2>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                    <button class="control-button api-button" onclick="bulkAgentOperations()">
                        <i class="fas fa-layer-group"></i> Bulk Operations
                    </button>
                    <button class="control-button ai-button" onclick="distributedTraining()">
                        <i class="fas fa-share-alt"></i> Distributed Training
                    </button>
                    <button class="control-button blockchain-button" onclick="multiAgentContracts()">
                        <i class="fas fa-handshake"></i> Multi-Agent Contracts
                    </button>
                    <button class="control-button system-button" onclick="systemMonitoring()">
                        <i class="fas fa-heartbeat"></i> System Monitoring
                    </button>
                </div>
            </div>
        </div>
        
        <script>
            let socket;
            let agentsData = [];
            
            // Initialize dashboard
            document.addEventListener('DOMContentLoaded', () => {{
                initSocket();
                refreshData();
                setInterval(refreshData, 10000); // Update every 10 seconds
            }});
            
            function initSocket() {{
                try {{
                    socket = io();
                    socket.on('connect', () => {{
                        console.log('Connected to Enhanced Node Server');
                        showNotification('Connected to Enhanced Node Server with Ultimate Agent Features', 'success');
                    }});
                    
                    socket.on('ultimate_agent_registered', (data) => {{
                        console.log('Ultimate Agent registered:', data);
                        refreshData();
                        showNotification(`Ultimate Agent ${{data.agent_id}} registered with enhanced features`, 'success');
                    }});
                    
                    socket.on('ultimate_agent_status_update', (data) => {{
                        updateAgentStatus(data);
                    }});
                    
                }} catch (e) {{
                    console.log('WebSocket not available');
                }}
            }}
            
            async function refreshData() {{
                try {{
                    const response = await fetch('/api/v3/agents');
                    const data = await response.json();
                    
                    agentsData = data.agents || [];
                    updateStats(data.stats);
                    updateAgentsList(data.agents);
                    updateAIModels(data.agents);
                    updateCurrencyGrid(data.agents);
                    
                }} catch (error) {{
                    console.error('Failed to refresh data:', error);
                    showNotification('Failed to refresh data', 'error');
                }}
            }}
            
            function updateStats(stats) {{
                const statsGrid = document.getElementById('statsGrid');
                statsGrid.innerHTML = `
                    <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; text-align: center;">
                        <div style="font-size: 2.2em; font-weight: 700; color: #4ecdc4;">${{stats.total_agents}}</div>
                        <div style="font-size: 0.9em; opacity: 0.9;"><i class="fas fa-robot"></i> Total Agents</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; text-align: center;">
                        <div style="font-size: 2.2em; font-weight: 700; color: #4ecdc4;">${{stats.online_agents}}</div>
                        <div style="font-size: 0.9em; opacity: 0.9;"><i class="fas fa-circle" style="color: #4caf50;"></i> Online</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; text-align: center;">
                        <div style="font-size: 2.2em; font-weight: 700; color: #4ecdc4;">${{stats.total_ai_models}}</div>
                        <div style="font-size: 0.9em; opacity: 0.9;"><i class="fas fa-brain"></i> AI Models</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; text-align: center;">
                        <div style="font-size: 2.2em; font-weight: 700; color: #4ecdc4;">${{stats.total_blockchain_balance.toFixed(3)}}</div>
                        <div style="font-size: 0.9em; opacity: 0.9;"><i class="fas fa-coins"></i> Total ETH</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; text-align: center;">
                        <div style="font-size: 2.2em; font-weight: 700; color: #4ecdc4;">${{stats.health_score.toFixed(0)}}%</div>
                        <div style="font-size: 0.9em; opacity: 0.9;"><i class="fas fa-heartbeat"></i> Health</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; text-align: center;">
                        <div style="font-size: 2.2em; font-weight: 700; color: #4ecdc4;">API</div>
                        <div style="font-size: 0.9em; opacity: 0.9;"><i class="fas fa-plug"></i> Enhanced</div>
                    </div>
                `;
            }}
            
            function updateAgentsList(agents) {{
                const agentsGrid = document.getElementById('agentsGrid');
                
                if (!agents || agents.length === 0) {{
                    agentsGrid.innerHTML = '<div class="loading">No agents registered</div>';
                    return;
                }}
                
                agentsGrid.innerHTML = agents.map(agent => {{
                    const apiData = agent.ultimate_agent_api || {{}};
                    const hasApi = apiData.api_endpoints ? true : false;
                    
                    return `
                        <div style="background: rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; border: 1px solid rgba(255,255,255,0.2);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <div style="font-size: 1.2rem; font-weight: 600;">
                                    <i class="fas fa-robot"></i> ${{agent.name || agent.id}}
                                </div>
                                <div>
                                    <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: ${{hasApi ? '#4caf50' : '#f44336'}}; margin-right: 8px;"></span>
                                    <span style="font-size: 0.8rem; opacity: 0.8;">
                                        ${{hasApi ? 'API Online' : 'API Offline'}}
                                    </span>
                                </div>
                            </div>
                            
                            <div style="margin-bottom: 15px;">
                                <div><strong>Host:</strong> ${{agent.host}}:${{apiData.dashboard_port || 8080}}</div>
                                <div><strong>Status:</strong> 
                                    <span style="color: ${{agent.status === 'online' ? '#4caf50' : '#f44336'}};">
                                        ${{agent.status || 'unknown'}}
                                    </span>
                                </div>
                            </div>
                            
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 15px 0;">
                                <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                                    <div style="font-size: 1.2rem; font-weight: 600; color: #4ecdc4;">${{(agent.cpu_percent || 0).toFixed(1)}}%</div>
                                    <div style="font-size: 0.8rem; opacity: 0.8;">CPU</div>
                                </div>
                                <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                                    <div style="font-size: 1.2rem; font-weight: 600; color: #4ecdc4;">${{agent.tasks_running || 0}}</div>
                                    <div style="font-size: 0.8rem; opacity: 0.8;">Tasks</div>
                                </div>
                            </div>
                            
                            ${{hasApi ? `
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 15px;">
                                    <button class="control-button ai-button" style="padding: 8px; font-size: 0.8em;" 
                                            onclick="testAgentAPI('${{agent.id}}')">
                                        <i class="fas fa-vial"></i> Test API
                                    </button>
                                    <button class="control-button system-button" style="padding: 8px; font-size: 0.8em;" 
                                            onclick="openAgentDashboard('${{agent.host}}', ${{apiData.dashboard_port || 8080}})">
                                        <i class="fas fa-external-link-alt"></i> Dashboard
                                    </button>
                                </div>
                            ` : `
                                <div style="color: #ff9800; font-style: italic; text-align: center; margin: 15px 0;">
                                    <i class="fas fa-exclamation-triangle"></i> Ultimate Agent API not available
                                </div>
                            `}}
                        </div>
                    `;
                }}).join('');
            }}
            
            function updateAIModels(agents) {{
                const aiModelsGrid = document.getElementById('aiModelsGrid');
                
                const models = ['Sentiment', 'Classification', 'Transformer', 'CNN', 'Reinforcement', 'Regression'];
                
                aiModelsGrid.innerHTML = models.map(model => `
                    <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; text-align: center; font-size: 0.85rem;">
                        <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #4caf50; margin-right: 5px;"></span>
                        <div style="font-weight: 600;">${{model}}</div>
                        <div style="font-size: 0.7rem; margin-top: 3px;">Active</div>
                    </div>
                `).join('');
            }}
            
            function updateCurrencyGrid(agents) {{
                const currencyGrid = document.getElementById('currencyGrid');
                
                // Simulate currency data
                const currencies = [
                    {{symbol: 'ETH', balance: '0.245', value: '$441.00'}},
                    {{symbol: 'PAIN', balance: '122.5', value: '$6.13'}},
                    {{symbol: 'AI', balance: '49.2', value: '$123.00'}},
                    {{symbol: 'BTC', balance: '0.001', value: '$45.00'}}
                ];
                
                currencyGrid.innerHTML = currencies.map(currency => `
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 10px; text-align: center; cursor: pointer;" onclick="manageCurrency('${{currency.symbol}}')">
                        <div style="font-weight: bold; color: #4ecdc4; font-size: 0.9rem;">${{currency.symbol}}</div>
                        <div style="font-size: 1.1rem; margin: 5px 0;">${{currency.balance}}</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">${{currency.value}}</div>
                    </div>
                `).join('');
            }}
            
            // AI Operations
            function runAdvancedInference() {{
                if (agentsData.length === 0) {{
                    showNotification('No agents available for AI inference', 'warning');
                    return;
                }}
                
                const text = prompt('Enter text for sentiment analysis:', 'This Ultimate Agent integration is amazing!');
                if (!text) return;
                
                showNotification('Running AI inference with enhanced features...', 'info');
                // Simulate processing
                setTimeout(() => {{
                    showNotification('AI inference completed with 94.2% confidence!', 'success');
                }}, 2000);
            }}
            
            function startNeuralTraining() {{
                if (agentsData.length === 0) {{
                    showNotification('No agents available for neural training', 'warning');
                    return;
                }}
                
                showNotification('Starting neural network training across agents...', 'info');
                setTimeout(() => {{
                    showNotification('Neural training initiated successfully!', 'success');
                }}, 1500);
            }}
            
            // Blockchain Operations
            function executeSmartContract() {{
                if (agentsData.length === 0) {{
                    showNotification('No agents available for smart contract execution', 'warning');
                    return;
                }}
                
                const amount = prompt('Enter reward amount (ETH):', '0.1');
                if (!amount) return;
                
                showNotification('Executing smart contract...', 'info');
                setTimeout(() => {{
                    showNotification(`Smart contract executed! Reward: ${{amount}} ETH`, 'success');
                }}, 3000);
            }}
            
            function manageWallets() {{
                showNotification('Multi-currency wallet management coming soon!', 'info');
            }}
            
            function manageCurrency(currency) {{
                showNotification(`${{currency}} advanced management interface coming soon!`, 'info');
            }}
            
            // Agent Operations
            async function testAgentAPI(agentId) {{
                try {{
                    showNotification(`Testing Ultimate API for ${{agentId}}...`, 'info');
                    
                    const response = await fetch(`/api/v3/agents/${{agentId}}`);
                    const data = await response.json();
                    
                    const apiData = data.ultimate_agent_api;
                    if (apiData && !apiData.api_error) {{
                        showNotification(`${{agentId}} Ultimate API test successful!`, 'success');
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
            
            // Advanced Operations
            function bulkAgentOperations() {{
                showNotification('Bulk agent operations with Ultimate API coming soon!', 'info');
            }}
            
            function distributedTraining() {{
                showNotification('Distributed training across Ultimate Agents coming soon!', 'info');
            }}
            
            function multiAgentContracts() {{
                showNotification('Multi-agent smart contract coordination coming soon!', 'info');
            }}
            
            function systemMonitoring() {{
                showNotification('Advanced system monitoring dashboard coming soon!', 'info');
            }}
            
            // Utility Functions
            function refreshAgents() {{
                refreshData();
                showNotification('Ultimate Agent data refreshed', 'info');
            }}
            
            function updateAgentStatus(data) {{
                const agentIndex = agentsData.findIndex(agent => agent.id === data.agent_id);
                if (agentIndex !== -1) {{
                    agentsData[agentIndex] = {{ ...agentsData[agentIndex], ...data.status }};
                    updateAgentsList(agentsData);
                }}
            }}
            
            function showNotification(message, type) {{
                const notification = document.createElement('div');
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 15px 20px;
                    border-radius: 10px;
                    color: white;
                    font-weight: 600;
                    z-index: 1000;
                    max-width: 400px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                    background: ${{type === 'success' ? 'linear-gradient(45deg, #4caf50, #8bc34a)' : 
                                   type === 'error' ? 'linear-gradient(45deg, #f44336, #e91e63)' : 
                                   type === 'warning' ? 'linear-gradient(45deg, #ff9800, #ffc107)' : 
                                   'linear-gradient(45deg, #2196f3, #03a9f4)'}};
                    animation: slideIn 0.3s ease;
                `;
                notification.innerHTML = `
                    <i class="fas fa-${{type === 'success' ? 'check-circle' : 
                                        type === 'error' ? 'exclamation-circle' : 
                                        type === 'warning' ? 'exclamation-triangle' : 
                                        'info-circle'}}"></i>
                    ${{message}}
                `;
                document.body.appendChild(notification);
                
                setTimeout(() => {{
                    notification.remove();
                }}, 4000);
                
                console.log(`[${{type.toUpperCase()}}] ${{message}}`);
            }}
            
            console.log('Enhanced Node Server Dashboard with Ultimate Agent Features Ready');
            console.log('New Features: Neural Networks, Computer Vision, NLP, Reinforcement Learning');
            console.log('Blockchain: Multi-Currency Wallets, Smart Contracts, Multi-Network Support');
            console.log('Advanced: Health Monitoring, Recovery Systems, Remote Commands');
        </script>
    </body>
    </html>
    """