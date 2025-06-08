#!/usr/bin/env python3
"""
API v3 Routes - Agent Registration and Heartbeat
"""

from flask import request, jsonify
from datetime import datetime
import json

from ..core.database import Agent, AgentHeartbeat
from ..models.agents import EnhancedAgentInfo, EnhancedAgentStatus
from ..utils.serialization import serialize_for_json
from ..config.settings import NODE_ID, NODE_VERSION


def register_api_v3_routes(server):
    """Register all API v3 routes with the server"""
    
    @server.app.route('/')
    def enhanced_dashboard():
        """Serve enhanced node dashboard with advanced remote control"""
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
            """Get enhanced agent information with statistics"""
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

                    agent_data = {**info_json, **status_json}
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
                "blockchain_summary": server.get_blockchain_summary()
            })

        except Exception as e:
            server.logger.error(f"Failed to get agents: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    
    @server.app.route('/api/v3/agents/<agent_id>', methods=['GET'])
    def get_agent_details(agent_id):
        """Get detailed information about a specific agent"""
        try:
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            agent_info = server.agents[agent_id]
            agent_status = server.agent_status.get(agent_id)
            
            # Get recent heartbeats
            recent_heartbeats = server.db.get_recent_heartbeats(agent_id, 10)
            
            # Get performance history
            performance_history = list(server.performance_history.get(agent_id, []))
            
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
                "performance_history": performance_history
            }
            
            return jsonify(result)
            
        except Exception as e:
            server.logger.error(f"Failed to get agent details: {e}")
            return jsonify({"error": str(e)}), 500
    
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
                "advanced_control_enabled": True
            })
        except Exception as e:
            server.logger.error(f"Failed to get legacy stats: {e}")
            return jsonify({"error": str(e)}), 500


def get_enhanced_dashboard_html():
    """Generate enhanced dashboard HTML with advanced remote control"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enhanced Node Server v{NODE_VERSION} - ADVANCED REMOTE CONTROL</title>
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
            .advanced-badge {{
                display: inline-block;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                padding: 8px 20px;
                border-radius: 20px;
                font-size: 0.9rem;
                font-weight: 700;
                margin: 10px 5px;
                position: relative;
                z-index: 1;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ box-shadow: 0 0 5px rgba(255, 107, 107, 0.5); }}
                50% {{ box-shadow: 0 0 20px rgba(78, 205, 196, 0.8); }}
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
            .loading {{
                text-align: center;
                opacity: 0.7;
                padding: 40px;
                font-style: italic;
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
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Enhanced Node Server</h1>
                <div class="advanced-badge">🎮 MODULAR ARCHITECTURE</div>
                <div class="advanced-badge">✅ ALL FEATURES PRESERVED</div>
                <div class="advanced-badge">➕ ADVANCED CONTROL</div>
                <p style="font-size: 1.1rem; margin: 15px 0; position: relative; z-index: 1;">
                    v{NODE_VERSION} - Fully Modularized System
                </p>
                
                <div class="feature-grid">
                    <div class="feature-badge">🧠 AI Orchestration</div>
                    <div class="feature-badge">💰 Blockchain Management</div>
                    <div class="feature-badge">☁️ Cloud Integration</div>
                    <div class="feature-badge">🔒 Security Features</div>
                    <div class="feature-badge">📊 Advanced Analytics</div>
                    <div class="feature-badge">🔌 Plugin Ecosystem</div>
                    <div class="feature-badge">🎯 Task Control</div>
                    <div class="feature-badge">🎮 REMOTE CONTROL</div>
                    <div class="feature-badge">⚙️ CONFIG MGMT</div>
                    <div class="feature-badge">📡 LIVE MONITORING</div>
                    <div class="feature-badge">🚀 BULK OPERATIONS</div>
                    <div class="feature-badge">⏰ SCHEDULING</div>
                    <div class="feature-badge">🔄 AUTO RECOVERY</div>
                    <div class="feature-badge">📋 SCRIPT DEPLOY</div>
                </div>
                
                <p style="position: relative; z-index: 1; opacity: 0.8; font-size: 0.9rem;">
                    Node ID: {NODE_ID} | Modular Architecture | All Features Available
                </p>
            </div>
            
            <div class="stats-grid" id="statsGrid">
                <div class="loading">Loading enhanced statistics...</div>
            </div>
            
            <div style="text-align: center; margin-top: 40px;">
                <button class="control-button" onclick="refreshData()">
                    🔄 Refresh Data
                </button>
            </div>
        </div>
        
        <script>
            let socket;
            
            document.addEventListener('DOMContentLoaded', () => {{
                initSocket();
                refreshData();
                setInterval(refreshData, 10000); // Update every 10 seconds
            }});
            
            function initSocket() {{
                try {{
                    socket = io();
                    socket.on('connect', () => console.log('🚀 Connected to Enhanced Node Server'));
                    socket.on('ultimate_agent_registered', (data) => {{
                        console.log('🤖 Agent registered:', data);
                        refreshData();
                    }});
                    socket.on('ultimate_agent_status_update', (data) => {{
                        console.log('📈 Agent status update:', data);
                        refreshData();
                    }});
                }} catch (e) {{
                    console.log('⚠️ WebSocket not available');
                }}
            }}
            
            async function refreshData() {{
                try {{
                    const response = await fetch('/api/v3/agents');
                    const data = await response.json();
                    
                    updateStats(data.stats);
                    
                }} catch (error) {{
                    console.error('Failed to refresh data:', error);
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
                        <div class="stat-value">${{stats.total_tasks_completed}}</div>
                        <div class="stat-label">Tasks Completed</div>
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
                `;
            }}
            
            console.log('🚀 Enhanced Node Server Dashboard Ready - MODULAR ARCHITECTURE');
            console.log('✅ All existing features preserved');
            console.log('🏗️ Clean modular structure implemented');
        </script>
    </body>
    </html>
    """