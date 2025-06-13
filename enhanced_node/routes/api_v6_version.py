#!/usr/bin/env python3
"""
API v6 Version Control Routes - Enhanced Node Server
Advanced version control and update management
FIXED: Removed circular import
"""

from flask import request, jsonify
from datetime import datetime, timedelta
import uuid
from ..utils.serialization import serialize_for_json


def register_api_v6_routes(server):
    """Register all API v6 version control routes"""
    
    # Agent Version Management
    @server.app.route('/api/v6/version/agents/<agent_id>/register', methods=['POST'])
    def register_agent_version(agent_id):
        """Register agent version information"""
        try:
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            version_data = request.get_json()
            if not version_data:
                return jsonify({"error": "Version data required"}), 400
            
            agent_version = server.version_control.register_agent_version(agent_id, version_data)
            
            if agent_version:
                return jsonify({
                    "success": True,
                    "agent_id": agent_id,
                    "version": agent_version.version,
                    "build_number": agent_version.build_number,
                    "update_channel": agent_version.update_channel,
                    "message": "Agent version registered successfully"
                })
            else:
                return jsonify({"error": "Failed to register agent version"}), 500
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v6/version/agents/<agent_id>/version', methods=['GET'])
    def get_agent_version(agent_id):
        """Get current version information for an agent"""
        try:
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            agent_version = server.version_control.get_agent_version(agent_id)
            
            if agent_version:
                return jsonify({
                    "success": True,
                    "agent_version": serialize_for_json(agent_version)
                })
            else:
                return jsonify({"error": "No version information found for agent"}), 404
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v6/version/agents', methods=['GET'])
    def get_all_agent_versions():
        """Get version information for all agents"""
        try:
            agent_versions = server.version_control.get_all_agent_versions()
            
            return jsonify({
                "success": True,
                "agent_versions": {
                    agent_id: serialize_for_json(version) 
                    for agent_id, version in agent_versions.items()
                },
                "total_agents": len(agent_versions)
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Update Management
    @server.app.route('/api/v6/version/updates/check', methods=['POST'])
    def check_for_updates():
        """Manually trigger update check"""
        try:
            server.version_control.check_for_updates()
            
            return jsonify({
                "success": True,
                "message": "Update check initiated",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v6/version/updates/available', methods=['GET'])
    def get_available_updates():
        """Get available updates"""
        try:
            channel = request.args.get('channel')
            
            available_updates = []
            for version, update_package in server.version_control.available_updates.items():
                if not channel or update_package.channel == channel:
                    available_updates.append(serialize_for_json(update_package))
            
            return jsonify({
                "success": True,
                "available_updates": available_updates,
                "total_updates": len(available_updates)
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v6/version/updates/schedule', methods=['POST'])
    def schedule_agent_update():
        """Schedule an update for an agent"""
        try:
            data = request.get_json()
            agent_id = data.get('agent_id')
            package_id = data.get('package_id')
            scheduled_time_str = data.get('scheduled_time')
            strategy = data.get('strategy', 'rolling')
            
            if not all([agent_id, package_id]):
                return jsonify({"error": "agent_id and package_id required"}), 400
            
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            if package_id not in server.version_control.update_packages:
                return jsonify({"error": "Update package not found"}), 404
            
            # Parse scheduled time
            if scheduled_time_str:
                try:
                    scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({"error": "Invalid scheduled_time format"}), 400
            else:
                scheduled_time = datetime.now()
            
            update_package = server.version_control.update_packages[package_id]
            
            # Create manual update
            agent_update = server.version_control.schedule_agent_update(agent_id, update_package)
            if agent_update:
                agent_update.scheduled_time = scheduled_time
                agent_update.strategy = strategy
                agent_update.initiated_by = "manual"
                
                server.version_control.update_agent_update_in_db(agent_update)
                
                return jsonify({
                    "success": True,
                    "update_id": agent_update.id,
                    "agent_id": agent_id,
                    "package_id": package_id,
                    "scheduled_time": scheduled_time.isoformat(),
                    "message": "Update scheduled successfully"
                })
            else:
                return jsonify({"error": "Failed to schedule update"}), 500
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v6/version/updates/active', methods=['GET'])
    def get_active_updates():
        """Get active updates"""
        try:
            agent_id = request.args.get('agent_id')
            status = request.args.get('status')
            
            active_updates = []
            for update in server.version_control.active_updates.values():
                if agent_id and update.agent_id != agent_id:
                    continue
                if status and update.status != status:
                    continue
                
                active_updates.append(serialize_for_json(update))
            
            return jsonify({
                "success": True,
                "active_updates": active_updates,
                "total_updates": len(active_updates)
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v6/version/updates/<update_id>', methods=['GET'])
    def get_update_status(update_id):
        """Get status of specific update"""
        try:
            if update_id not in server.version_control.active_updates:
                return jsonify({"error": "Update not found"}), 404
            
            update = server.version_control.active_updates[update_id]
            
            return jsonify({
                "success": True,
                "update": serialize_for_json(update)
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v6/version/updates/<update_id>/cancel', methods=['POST'])
    def cancel_update(update_id):
        """Cancel a scheduled update"""
        try:
            if update_id not in server.version_control.active_updates:
                return jsonify({"error": "Update not found"}), 404
            
            update = server.version_control.active_updates[update_id]
            
            if update.status not in ["scheduled", "downloading"]:
                return jsonify({"error": "Cannot cancel update in current status"}), 400
            
            update.status = "cancelled"
            update.completed_at = datetime.now()
            server.version_control.update_agent_update_in_db(update)
            
            return jsonify({
                "success": True,
                "update_id": update_id,
                "message": "Update cancelled successfully"
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Rollback Management
    @server.app.route('/api/v6/version/rollback/initiate', methods=['POST'])
    def initiate_rollback():
        """Initiate manual rollback for an agent"""
        try:
            data = request.get_json()
            agent_id = data.get('agent_id')
            to_version = data.get('to_version')
            reason = data.get('reason', 'Manual rollback')
            
            if not agent_id:
                return jsonify({"error": "agent_id required"}), 400
            
            if agent_id not in server.agents:
                return jsonify({"error": "Agent not found"}), 404
            
            success = server.version_control.initiate_manual_rollback(agent_id, to_version)
            
            if success:
                return jsonify({
                    "success": True,
                    "agent_id": agent_id,
                    "message": "Rollback initiated successfully"
                })
            else:
                return jsonify({"error": "Failed to initiate rollback"}), 500
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v6/version/rollback/history', methods=['GET'])
    def get_rollback_history():
        """Get rollback history"""
        try:
            agent_id = request.args.get('agent_id')
            limit = request.args.get('limit', 20, type=int)
            
            if agent_id:
                if agent_id not in server.agents:
                    return jsonify({"error": "Agent not found"}), 404
                
                rollback_history = server.version_control.rollback_history.get(agent_id, [])
            else:
                # Get all rollback history
                rollback_history = []
                for agent_rollbacks in server.version_control.rollback_history.values():
                    rollback_history.extend(agent_rollbacks)
                
                # Sort by timestamp
                rollback_history.sort(key=lambda x: x.started_at or datetime.min, reverse=True)
            
            # Limit results
            rollback_history = rollback_history[:limit]
            
            return jsonify({
                "success": True,
                "rollback_history": [serialize_for_json(rollback) for rollback in rollback_history],
                "total_rollbacks": len(rollback_history)
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Statistics and Reporting
    @server.app.route('/api/v6/version/statistics', methods=['GET'])
    def get_version_statistics():
        """Get comprehensive version control statistics"""
        try:
            stats = server.version_control.get_version_statistics()
            
            return jsonify({
                "success": True,
                "statistics": stats,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Health and Monitoring
    @server.app.route('/api/v6/version/health', methods=['GET'])
    def get_version_control_health():
        """Get version control system health"""
        try:
            health_data = {
                "overall_health": "healthy",
                "services": {
                    "update_checker": {
                        "status": "running" if server.version_control.update_checker_running else "stopped",
                        "last_check": "2024-01-01T00:00:00Z"
                    },
                    "rollback_monitor": {
                        "status": "running" if server.version_control.rollback_monitor_running else "stopped",
                        "last_check": "2024-01-01T00:00:00Z"
                    }
                },
                "statistics": server.version_control.get_version_statistics(),
                "issues": [],
                "recommendations": []
            }
            
            return jsonify({
                "success": True,
                "health": health_data,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Emergency Operations
    @server.app.route('/api/v6/version/emergency/stop-all-updates', methods=['POST'])
    def emergency_stop_all_updates():
        """Emergency stop all active updates"""
        try:
            stopped_updates = []
            
            for update in server.version_control.active_updates.values():
                if update.status in ["scheduled", "downloading", "installing"]:
                    update.status = "cancelled"
                    update.completed_at = datetime.now()
                    update.error_message = "Emergency stop initiated"
                    
                    server.version_control.update_agent_update_in_db(update)
                    stopped_updates.append(update.id)
            
            # Broadcast emergency stop
            server.socketio.emit('emergency_update_stop', {
                'stopped_updates': stopped_updates,
                'timestamp': datetime.now().isoformat()
            }, room='dashboard')
            
            return jsonify({
                "success": True,
                "stopped_updates": stopped_updates,
                "total_stopped": len(stopped_updates),
                "message": "Emergency stop completed for all active updates"
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @server.app.route('/api/v6/version/emergency/rollback-all', methods=['POST'])
    def emergency_rollback_all():
        """Emergency rollback all recently updated agents"""
        try:
            data = request.get_json()
            hours = data.get('hours', 24)  # Default to last 24 hours
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_updates = []
            
            # Find agents updated in the last X hours
            for update in server.version_control.active_updates.values():
                if (update.status == "completed" and 
                    update.completed_at and 
                    update.completed_at >= cutoff_time):
                    recent_updates.append(update)
            
            rollback_results = []
            
            for update in recent_updates:
                try:
                    success = server.version_control.initiate_manual_rollback(
                        update.agent_id,
                        update.from_version
                    )
                    rollback_results.append({
                        "agent_id": update.agent_id,
                        "update_id": update.id,
                        "success": success
                    })
                except Exception as e:
                    rollback_results.append({
                        "agent_id": update.agent_id,
                        "update_id": update.id,
                        "success": False,
                        "error": str(e)
                    })
            
            successful_rollbacks = len([r for r in rollback_results if r["success"]])
            
            return jsonify({
                "success": True,
                "rollback_results": rollback_results,
                "total_agents": len(recent_updates),
                "successful_rollbacks": successful_rollbacks,
                "hours_back": hours,
                "message": f"Emergency rollback initiated for {successful_rollbacks}/{len(recent_updates)} recently updated agents"
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
