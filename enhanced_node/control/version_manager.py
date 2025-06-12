#!/usr/bin/env python3
"""
Enhanced Node Server - Version Control Manager
Handles agent version tracking, updates, and rollbacks

FILE LOCATION: enhanced_node/control/version_manager.py
DEPENDENCIES: 
  - enhanced_node/models/versions.py
  - enhanced_node/core/database.py (updated with version control models)
  - enhanced_node/utils/logger.py (updated with get_version_logger)
"""

import os
import hashlib
import zipfile
import tempfile
import shutil
import time
import threading
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..models.versions import AgentVersion, AgentUpdate, UpdatePackage, RollbackOperation
from ..core.database import (
    AgentVersionRecord, AgentUpdateRecord, UpdatePackageRecord, 
    RollbackOperationRecord
)
from ..utils.serialization import serialize_for_json
from ..utils.logger import get_version_logger


class VersionControlManager:
    """Advanced version control and update management for agents"""
    
    def __init__(self, node_server):
        self.node_server = node_server
        self.logger = get_version_logger()
        
        # Version tracking
        self.agent_versions = {}  # agent_id -> current version info
        self.available_updates = {}  # version -> update package info
        self.update_packages = {}  # package_id -> UpdatePackage
        self.active_updates = {}  # update_id -> AgentUpdate
        self.rollback_history = {}  # agent_id -> list of rollback operations
        
        # Update management
        self.update_server_url = "https://updates.ultimateagent.network"
        self.update_channels = ["stable", "beta", "alpha", "nightly"]
        self.auto_update_enabled = True
        self.maintenance_window = {"start": "02:00", "end": "04:00"}
        
        # Version policies
        self.update_policies = {
            "critical_security": {"auto_apply": True, "delay_hours": 0},
            "security": {"auto_apply": True, "delay_hours": 2},
            "feature": {"auto_apply": False, "delay_hours": 24},
            "experimental": {"auto_apply": False, "delay_hours": 168}
        }
        
        # Update strategies
        self.update_strategies = {
            "rolling": "Update agents one by one with health checks",
            "canary": "Update 10% of agents first, then proceed",
            "blue_green": "Update to new version, switch traffic",
            "immediate": "Update all agents simultaneously",
            "maintenance_window": "Update only during maintenance window"
        }
        
        # File management
        self.update_storage_dir = Path("updates")
        self.backup_storage_dir = Path("backups")
        self.temp_dir = Path("temp")
        
        # Create directories
        for dir_path in [self.update_storage_dir, self.backup_storage_dir, self.temp_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Services
        self.update_checker_running = False
        self.rollback_monitor_running = False
        
        self.logger.info("VersionControlManager initialized with advanced update capabilities")
    
    def start_version_services(self):
        """Start version control background services"""
        self.start_update_checker()
        self.start_rollback_monitor()
        self.logger.info("Version control services started")
    
    def start_update_checker(self):
        """Start automatic update checking service"""
        def update_checker_loop():
            self.update_checker_running = True
            while self.update_checker_running:
                try:
                    self.check_for_updates()
                    self.process_scheduled_updates()
                    time.sleep(300)  # Check every 5 minutes
                except Exception as e:
                    self.logger.error(f"Update checker error: {e}")
                    time.sleep(900)  # Wait 15 minutes on error
        
        thread = threading.Thread(target=update_checker_loop, daemon=True, name="UpdateChecker")
        thread.start()
        self.logger.info("Update checker service started")
    
    def start_rollback_monitor(self):
        """Start rollback monitoring service"""
        def rollback_monitor_loop():
            self.rollback_monitor_running = True
            while self.rollback_monitor_running:
                try:
                    self.monitor_update_health()
                    self.process_automatic_rollbacks()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    self.logger.error(f"Rollback monitor error: {e}")
                    time.sleep(300)
        
        thread = threading.Thread(target=rollback_monitor_loop, daemon=True, name="RollbackMonitor")
        thread.start()
        self.logger.info("Rollback monitor service started")
    
    # Version Tracking
    def register_agent_version(self, agent_id: str, version_info: Dict[str, Any]):
        """Register agent version information"""
        try:
            # Extract version information
            current_version = version_info.get("version", "unknown")
            build_number = version_info.get("build_number", 0)
            commit_hash = version_info.get("commit_hash", "")
            build_date = version_info.get("build_date")
            
            if isinstance(build_date, str):
                build_date = datetime.fromisoformat(build_date.replace('Z', '+00:00'))
            elif not build_date:
                build_date = datetime.now()
            
            # Create version record
            agent_version = AgentVersion(
                agent_id=agent_id,
                version=current_version,
                build_number=build_number,
                commit_hash=commit_hash,
                build_date=build_date,
                capabilities=version_info.get("capabilities", []),
                dependencies=version_info.get("dependencies", {}),
                features=version_info.get("features", []),
                platform=version_info.get("platform", "unknown"),
                architecture=version_info.get("architecture", "unknown"),
                update_channel=version_info.get("update_channel", "stable"),
                last_seen=datetime.now()
            )
            
            # Store in memory and database
            self.agent_versions[agent_id] = agent_version
            self.store_agent_version_in_db(agent_version)
            
            self.logger.info(f"Registered version {current_version} for agent {agent_id}")
            
            # Check if update is available
            self.check_agent_for_updates(agent_id)
            
            return agent_version
            
        except Exception as e:
            self.logger.error(f"Failed to register agent version for {agent_id}: {e}")
            return None
    
    def get_agent_version(self, agent_id: str) -> Optional[AgentVersion]:
        """Get current version information for an agent"""
        return self.agent_versions.get(agent_id)
    
    def get_all_agent_versions(self) -> Dict[str, AgentVersion]:
        """Get version information for all agents"""
        return self.agent_versions.copy()
    
    # Update Management
    def check_for_updates(self):
        """Check for available updates from update server"""
        try:
            # Check each update channel
            for channel in self.update_channels:
                try:
                    response = requests.get(
                        f"{self.update_server_url}/api/updates",
                        params={"channel": channel, "format": "json"},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        updates = response.json()
                        self.process_available_updates(updates, channel)
                    else:
                        self.logger.warning(f"Update check failed for {channel}: HTTP {response.status_code}")
                        
                except requests.RequestException as e:
                    self.logger.warning(f"Failed to check updates for {channel}: {e}")
            
            self.logger.info("Update check completed")
            
        except Exception as e:
            self.logger.error(f"Update check error: {e}")
    
    def process_available_updates(self, updates: List[Dict], channel: str):
        """Process available updates from update server"""
        for update_info in updates:
            try:
                package_id = update_info["package_id"]
                version = update_info["version"]
                
                # Create update package
                update_package = UpdatePackage(
                    id=package_id,
                    version=version,
                    channel=channel,
                    release_date=datetime.fromisoformat(update_info["release_date"]),
                    update_type=update_info.get("type", "feature"),
                    download_url=update_info["download_url"],
                    checksum=update_info["checksum"],
                    size_bytes=update_info.get("size_bytes", 0),
                    description=update_info.get("description", ""),
                    changelog=update_info.get("changelog", []),
                    requirements=update_info.get("requirements", {}),
                    compatibility=update_info.get("compatibility", {}),
                    rollback_supported=update_info.get("rollback_supported", True),
                    critical=update_info.get("critical", False)
                )
                
                # Store update package
                self.update_packages[package_id] = update_package
                self.available_updates[version] = update_package
                self.store_update_package_in_db(update_package)
                
                self.logger.info(f"Available update: {version} ({channel}) - {update_info.get('type', 'feature')}")
                
                # Check if any agents need this update
                self.evaluate_update_for_agents(update_package)
                
            except Exception as e:
                self.logger.error(f"Failed to process update {update_info.get('version', 'unknown')}: {e}")
    
    def evaluate_update_for_agents(self, update_package: UpdatePackage):
        """Evaluate if agents need this update"""
        for agent_id, agent_version in self.agent_versions.items():
            try:
                # Check if agent needs this update
                if self.should_agent_update(agent_id, agent_version, update_package):
                    self.schedule_agent_update(agent_id, update_package)
                    
            except Exception as e:
                self.logger.error(f"Failed to evaluate update for agent {agent_id}: {e}")
    
    def should_agent_update(self, agent_id: str, agent_version: AgentVersion, 
                           update_package: UpdatePackage) -> bool:
        """Determine if an agent should be updated"""
        try:
            # Check channel compatibility
            if agent_version.update_channel != update_package.channel:
                return False
            
            # Check version comparison
            if not self.is_version_newer(update_package.version, agent_version.version):
                return False
            
            # Check platform compatibility
            platform_compat = update_package.compatibility.get("platforms", [])
            if platform_compat and agent_version.platform not in platform_compat:
                return False
            
            # Check requirements
            if not self.check_requirements(agent_version, update_package.requirements):
                return False
            
            # Check update policy
            policy = self.update_policies.get(update_package.update_type, {})
            if not policy.get("auto_apply", False) and not update_package.critical:
                return False
            
            # Check if already scheduled
            for update in self.active_updates.values():
                if update.agent_id == agent_id and update.status in ["scheduled", "downloading", "installing"]:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking if agent {agent_id} should update: {e}")
            return False
    
    def schedule_agent_update(self, agent_id: str, update_package: UpdatePackage):
        """Schedule an update for an agent"""
        try:
            # Calculate scheduled time based on policy
            policy = self.update_policies.get(update_package.update_type, {})
            delay_hours = policy.get("delay_hours", 24)
            
            if update_package.critical:
                delay_hours = 0  # Critical updates are immediate
            
            scheduled_time = datetime.now() + timedelta(hours=delay_hours)
            
            # Create update record
            agent_update = AgentUpdate(
                id=f"update-{agent_id}-{int(time.time())}",
                agent_id=agent_id,
                package_id=update_package.id,
                from_version=self.agent_versions[agent_id].version,
                to_version=update_package.version,
                update_type=update_package.update_type,
                scheduled_time=scheduled_time,
                status="scheduled",
                strategy="rolling",  # Default strategy
                auto_rollback_enabled=True,
                rollback_threshold_minutes=30
            )
            
            # Store update
            self.active_updates[agent_update.id] = agent_update
            self.store_agent_update_in_db(agent_update)
            
            self.logger.info(f"Scheduled update for agent {agent_id}: {update_package.version} at {scheduled_time}")
            
            # Notify via WebSocket
            self.node_server.socketio.emit('agent_update_scheduled', {
                'agent_id': agent_id,
                'update_id': agent_update.id,
                'from_version': agent_update.from_version,
                'to_version': agent_update.to_version,
                'scheduled_time': scheduled_time.isoformat(),
                'update_type': update_package.update_type,
                'critical': update_package.critical
            }, room='dashboard')
            
            return agent_update
            
        except Exception as e:
            self.logger.error(f"Failed to schedule update for agent {agent_id}: {e}")
            return None
    
    def process_scheduled_updates(self):
        """Process scheduled updates that are due"""
        current_time = datetime.now()
        
        for update in list(self.active_updates.values()):
            if (update.status == "scheduled" and 
                update.scheduled_time <= current_time):
                
                # Check maintenance window for non-critical updates
                if not self.is_in_maintenance_window() and not self.is_critical_update(update):
                    continue
                
                self.execute_agent_update(update)
    
    def execute_agent_update(self, agent_update: AgentUpdate) -> bool:
        """Execute an agent update"""
        try:
            agent_id = agent_update.agent_id
            update_package = self.update_packages[agent_update.package_id]
            
            self.logger.info(f"Starting update for agent {agent_id} to version {agent_update.to_version}")
            
            # Update status
            agent_update.status = "downloading"
            agent_update.started_at = datetime.now()
            self.update_agent_update_in_db(agent_update)
            
            # Notify start
            self.notify_update_progress(agent_update, "downloading", 0)
            
            # Download update package
            if not self.download_update_package(update_package):
                agent_update.status = "failed"
                agent_update.error_message = "Failed to download update package"
                self.update_agent_update_in_db(agent_update)
                return False
            
            # Create backup
            self.notify_update_progress(agent_update, "backing_up", 25)
            backup_path = self.create_agent_backup(agent_id)
            if not backup_path:
                agent_update.status = "failed"
                agent_update.error_message = "Failed to create backup"
                self.update_agent_update_in_db(agent_update)
                return False
            
            agent_update.backup_path = str(backup_path)
            
            # Install update
            self.notify_update_progress(agent_update, "installing", 50)
            if not self.install_agent_update(agent_id, update_package):
                agent_update.status = "failed"
                agent_update.error_message = "Failed to install update"
                self.update_agent_update_in_db(agent_update)
                return False
            
            # Restart agent
            self.notify_update_progress(agent_update, "restarting", 75)
            if not self.restart_agent_for_update(agent_id):
                agent_update.status = "failed"
                agent_update.error_message = "Failed to restart agent"
                self.update_agent_update_in_db(agent_update)
                return False
            
            # Verify update
            self.notify_update_progress(agent_update, "verifying", 90)
            if not self.verify_agent_update(agent_id, agent_update.to_version):
                # Start automatic rollback
                self.initiate_automatic_rollback(agent_update)
                return False
            
            # Complete update
            agent_update.status = "completed"
            agent_update.completed_at = datetime.now()
            agent_update.progress = 100
            self.update_agent_update_in_db(agent_update)
            
            # Update agent version
            if agent_id in self.agent_versions:
                self.agent_versions[agent_id].version = agent_update.to_version
                self.agent_versions[agent_id].last_seen = datetime.now()
            
            self.notify_update_progress(agent_update, "completed", 100)
            
            self.logger.info(f"Update completed successfully for agent {agent_id}")
            
            # Schedule health monitoring
            self.schedule_post_update_monitoring(agent_update)
            
            return True
            
        except Exception as e:
            agent_update.status = "failed"
            agent_update.error_message = str(e)
            agent_update.completed_at = datetime.now()
            self.update_agent_update_in_db(agent_update)
            
            self.logger.error(f"Update failed for agent {agent_id}: {e}")
            return False
    
    def download_update_package(self, update_package: UpdatePackage) -> bool:
        """Download update package from server"""
        try:
            package_path = self.update_storage_dir / f"{update_package.id}.zip"
            
            # Check if already downloaded and verified
            if package_path.exists():
                if self.verify_package_checksum(package_path, update_package.checksum):
                    self.logger.info(f"Update package {update_package.id} already downloaded")
                    return True
                else:
                    package_path.unlink()  # Remove corrupted file
            
            # Download package
            self.logger.info(f"Downloading update package {update_package.id}")
            
            response = requests.get(update_package.download_url, stream=True, timeout=300)
            response.raise_for_status()
            
            with open(package_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify checksum
            if not self.verify_package_checksum(package_path, update_package.checksum):
                package_path.unlink()
                self.logger.error(f"Checksum verification failed for {update_package.id}")
                return False
            
            self.logger.info(f"Update package {update_package.id} downloaded and verified")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download update package {update_package.id}: {e}")
            return False
    
    def install_agent_update(self, agent_id: str, update_package: UpdatePackage) -> bool:
        """Install update on agent via remote command"""
        try:
            package_path = self.update_storage_dir / f"{update_package.id}.zip"
            
            # Read package content
            with open(package_path, 'rb') as f:
                package_data = f.read()
            
            # Create install command
            command = self.node_server.advanced_remote_control.create_agent_command(
                agent_id,
                "install_update",
                {
                    "package_id": update_package.id,
                    "version": update_package.version,
                    "package_data": package_data.hex(),  # Send as hex string
                    "checksum": update_package.checksum,
                    "install_options": {
                        "backup_current": True,
                        "verify_before_restart": True,
                        "rollback_on_failure": True
                    }
                }
            )
            
            # Execute command
            success = self.node_server.advanced_remote_control.execute_command_on_agent(command)
            
            if success:
                self.logger.info(f"Update installation command sent to agent {agent_id}")
                return True
            else:
                self.logger.error(f"Failed to send update installation command to agent {agent_id}")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to install update on agent {agent_id}: {e}")
            return False
    
    def restart_agent_for_update(self, agent_id: str) -> bool:
        """Restart agent after update"""
        try:
            # Create restart command
            command = self.node_server.advanced_remote_control.create_agent_command(
                agent_id,
                "restart_for_update",
                {
                    "delay_seconds": 5,
                    "graceful_shutdown": True,
                    "verify_after_restart": True,
                    "timeout_seconds": 120
                }
            )
            
            # Execute command
            success = self.node_server.advanced_remote_control.execute_command_on_agent(command)
            
            if success:
                self.logger.info(f"Restart command sent to agent {agent_id}")
                # Wait for restart
                time.sleep(30)  # Give agent time to restart
                return True
            else:
                self.logger.error(f"Failed to send restart command to agent {agent_id}")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to restart agent {agent_id}: {e}")
            return False
    
    def verify_agent_update(self, agent_id: str, expected_version: str) -> bool:
        """Verify that agent update was successful"""
        try:
            # Wait for agent to come back online
            max_wait = 120  # 2 minutes
            wait_interval = 5
            waited = 0
            
            while waited < max_wait:
                if agent_id in self.node_server.agent_status:
                    status = self.node_server.agent_status[agent_id]
                    if status.status == "online":
                        break
                
                time.sleep(wait_interval)
                waited += wait_interval
            
            if waited >= max_wait:
                self.logger.error(f"Agent {agent_id} did not come back online after update")
                return False
            
            # Request version verification
            command = self.node_server.advanced_remote_control.create_agent_command(
                agent_id,
                "verify_version",
                {"expected_version": expected_version}
            )
            
            success = self.node_server.advanced_remote_control.execute_command_on_agent(command)
            
            if success:
                # Wait for verification response
                time.sleep(10)
                
                # Check if version matches
                if agent_id in self.agent_versions:
                    current_version = self.agent_versions[agent_id].version
                    if current_version == expected_version:
                        self.logger.info(f"Agent {agent_id} update verification successful")
                        return True
                
                self.logger.error(f"Agent {agent_id} version verification failed")
                return False
            else:
                self.logger.error(f"Failed to send verification command to agent {agent_id}")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to verify update for agent {agent_id}: {e}")
            return False
    
    # Rollback Management
    def initiate_manual_rollback(self, agent_id: str, to_version: str = None) -> bool:
        """Initiate manual rollback for an agent"""
        try:
            # Find the most recent successful update
            recent_update = None
            for update in reversed(list(self.active_updates.values())):
                if (update.agent_id == agent_id and 
                    update.status == "completed" and 
                    update.backup_path):
                    recent_update = update
                    break
            
            if not recent_update:
                self.logger.error(f"No recent update found for rollback of agent {agent_id}")
                return False
            
            # Create rollback operation
            rollback_op = RollbackOperation(
                id=f"rollback-{agent_id}-{int(time.time())}",
                agent_id=agent_id,
                update_id=recent_update.id,
                from_version=recent_update.to_version,
                to_version=to_version or recent_update.from_version,
                rollback_type="manual",
                backup_path=recent_update.backup_path,
                initiated_by="manual",
                reason="Manual rollback requested"
            )
            
            return self.execute_rollback(rollback_op)
            
        except Exception as e:
            self.logger.error(f"Failed to initiate manual rollback for agent {agent_id}: {e}")
            return False
    
    def initiate_automatic_rollback(self, agent_update: AgentUpdate):
        """Initiate automatic rollback for failed update"""
        try:
            if not agent_update.auto_rollback_enabled:
                self.logger.warning(f"Auto-rollback disabled for update {agent_update.id}")
                return
            
            rollback_op = RollbackOperation(
                id=f"rollback-{agent_update.agent_id}-{int(time.time())}",
                agent_id=agent_update.agent_id,
                update_id=agent_update.id,
                from_version=agent_update.to_version,
                to_version=agent_update.from_version,
                rollback_type="automatic",
                backup_path=agent_update.backup_path,
                initiated_by="system",
                reason="Update verification failed"
            )
            
            self.execute_rollback(rollback_op)
            
        except Exception as e:
            self.logger.error(f"Failed to initiate automatic rollback for update {agent_update.id}: {e}")
    
    def execute_rollback(self, rollback_op: RollbackOperation) -> bool:
        """Execute rollback operation"""
        try:
            self.logger.info(f"Starting rollback for agent {rollback_op.agent_id}")
            
            rollback_op.status = "executing"
            rollback_op.started_at = datetime.now()
            
            # Store rollback operation
            if rollback_op.agent_id not in self.rollback_history:
                self.rollback_history[rollback_op.agent_id] = []
            self.rollback_history[rollback_op.agent_id].append(rollback_op)
            self.store_rollback_operation_in_db(rollback_op)
            
            # Notify start
            self.node_server.socketio.emit('agent_rollback_started', {
                'agent_id': rollback_op.agent_id,
                'rollback_id': rollback_op.id,
                'from_version': rollback_op.from_version,
                'to_version': rollback_op.to_version,
                'rollback_type': rollback_op.rollback_type
            }, room='dashboard')
            
            # Execute rollback command
            command = self.node_server.advanced_remote_control.create_agent_command(
                rollback_op.agent_id,
                "execute_rollback",
                {
                    "rollback_id": rollback_op.id,
                    "backup_path": rollback_op.backup_path,
                    "target_version": rollback_op.to_version,
                    "verify_after_rollback": True
                }
            )
            
            success = self.node_server.advanced_remote_control.execute_command_on_agent(command)
            
            if success:
                # Wait for rollback to complete
                time.sleep(60)
                
                # Verify rollback
                if self.verify_agent_update(rollback_op.agent_id, rollback_op.to_version):
                    rollback_op.status = "completed"
                    rollback_op.completed_at = datetime.now()
                    
                    # Update agent version
                    if rollback_op.agent_id in self.agent_versions:
                        self.agent_versions[rollback_op.agent_id].version = rollback_op.to_version
                    
                    self.logger.info(f"Rollback completed successfully for agent {rollback_op.agent_id}")
                    
                    # Notify completion
                    self.node_server.socketio.emit('agent_rollback_completed', {
                        'agent_id': rollback_op.agent_id,
                        'rollback_id': rollback_op.id,
                        'success': True
                    }, room='dashboard')
                    
                    return True
                else:
                    rollback_op.status = "failed"
                    rollback_op.error_message = "Rollback verification failed"
            else:
                rollback_op.status = "failed"
                rollback_op.error_message = "Failed to execute rollback command"
            
            rollback_op.completed_at = datetime.now()
            self.update_rollback_operation_in_db(rollback_op)
            
            self.logger.error(f"Rollback failed for agent {rollback_op.agent_id}")
            return False
            
        except Exception as e:
            rollback_op.status = "failed"
            rollback_op.error_message = str(e)
            rollback_op.completed_at = datetime.now()
            self.update_rollback_operation_in_db(rollback_op)
            
            self.logger.error(f"Rollback execution failed for agent {rollback_op.agent_id}: {e}")
            return False
    
    # Utility Methods
    def is_version_newer(self, version1: str, version2: str) -> bool:
        """Compare versions to determine if version1 is newer than version2"""
        try:
            # Simple version comparison (improve for semantic versioning)
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # Pad to same length
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            return v1_parts > v2_parts
            
        except Exception:
            # Fallback to string comparison
            return version1 > version2
    
    def check_requirements(self, agent_version: AgentVersion, requirements: Dict) -> bool:
        """Check if agent meets update requirements"""
        try:
            # Check minimum version
            min_version = requirements.get("min_version")
            if min_version and not self.is_version_newer(agent_version.version, min_version):
                return False
            
            # Check dependencies
            required_deps = requirements.get("dependencies", {})
            for dep_name, dep_version in required_deps.items():
                agent_dep_version = agent_version.dependencies.get(dep_name)
                if not agent_dep_version or not self.is_version_newer(agent_dep_version, dep_version):
                    return False
            
            # Check features
            required_features = requirements.get("features", [])
            for feature in required_features:
                if feature not in agent_version.features:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking requirements: {e}")
            return False
    
    def verify_package_checksum(self, package_path: Path, expected_checksum: str) -> bool:
        """Verify package checksum"""
        try:
            sha256_hash = hashlib.sha256()
            with open(package_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            actual_checksum = sha256_hash.hexdigest()
            return actual_checksum == expected_checksum
            
        except Exception as e:
            self.logger.error(f"Error verifying checksum: {e}")
            return False
    
    def create_agent_backup(self, agent_id: str) -> Optional[Path]:
        """Create backup of agent before update"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"agent_{agent_id}_{timestamp}.backup"
            backup_path = self.backup_storage_dir / backup_filename
            
            # Request agent to create backup
            command = self.node_server.advanced_remote_control.create_agent_command(
                agent_id,
                "create_backup",
                {
                    "backup_path": str(backup_path),
                    "include_data": True,
                    "include_config": True,
                    "include_logs": False
                }
            )
            
            success = self.node_server.advanced_remote_control.execute_command_on_agent(command)
            
            if success:
                # Wait for backup to complete
                time.sleep(30)
                
                if backup_path.exists():
                    self.logger.info(f"Backup created for agent {agent_id}: {backup_path}")
                    return backup_path
            
            self.logger.error(f"Failed to create backup for agent {agent_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating backup for agent {agent_id}: {e}")
            return None
    
    def is_in_maintenance_window(self) -> bool:
        """Check if current time is in maintenance window"""
        try:
            current_time = datetime.now().time()
            start_time = datetime.strptime(self.maintenance_window["start"], "%H:%M").time()
            end_time = datetime.strptime(self.maintenance_window["end"], "%H:%M").time()
            
            if start_time <= end_time:
                return start_time <= current_time <= end_time
            else:
                # Maintenance window crosses midnight
                return current_time >= start_time or current_time <= end_time
            
        except Exception:
            return False
    
    def is_critical_update(self, agent_update: AgentUpdate) -> bool:
        """Check if update is critical"""
        update_package = self.update_packages.get(agent_update.package_id)
        return update_package and update_package.critical
    
    def notify_update_progress(self, agent_update: AgentUpdate, stage: str, progress: int):
        """Notify update progress via WebSocket"""
        agent_update.progress = progress
        self.update_agent_update_in_db(agent_update)
        
        self.node_server.socketio.emit('agent_update_progress', {
            'agent_id': agent_update.agent_id,
            'update_id': agent_update.id,
            'stage': stage,
            'progress': progress,
            'timestamp': datetime.now().isoformat()
        }, room='dashboard')
    
    def schedule_post_update_monitoring(self, agent_update: AgentUpdate):
        """Schedule post-update health monitoring"""
        if not agent_update.auto_rollback_enabled:
            return
        
        def monitor_post_update():
            time.sleep(agent_update.rollback_threshold_minutes * 60)
            
            # Check agent health
            agent_status = self.node_server.agent_status.get(agent_update.agent_id)
            if not agent_status or agent_status.status != "online":
                self.logger.warning(f"Agent {agent_update.agent_id} unhealthy after update, considering rollback")
                # Could implement automatic rollback here based on health metrics
        
        thread = threading.Thread(target=monitor_post_update, daemon=True)
        thread.start()
    
    def monitor_update_health(self):
        """Monitor health of recently updated agents"""
        current_time = datetime.now()
        
        for update in self.active_updates.values():
            if (update.status == "completed" and 
                update.auto_rollback_enabled and
                update.completed_at and
                (current_time - update.completed_at).total_seconds() < update.rollback_threshold_minutes * 60):
                
                # Check agent health
                agent_status = self.node_server.agent_status.get(update.agent_id)
                if not agent_status or agent_status.status != "online":
                    self.logger.warning(f"Agent {update.agent_id} unhealthy after update, considering automatic rollback")
                    # Implement health-based rollback logic here
    
    def process_automatic_rollbacks(self):
        """Process any pending automatic rollbacks"""
        # Implement automatic rollback processing based on health metrics
        pass
    
    # Statistics and Reporting
    def get_version_statistics(self) -> Dict[str, Any]:
        """Get comprehensive version control statistics"""
        try:
            total_agents = len(self.agent_versions)
            active_updates = len([u for u in self.active_updates.values() if u.status in ["scheduled", "downloading", "installing"]])
            completed_updates = len([u for u in self.active_updates.values() if u.status == "completed"])
            failed_updates = len([u for u in self.active_updates.values() if u.status == "failed"])
            
            # Version distribution
            version_dist = {}
            channel_dist = {}
            for agent_version in self.agent_versions.values():
                version = agent_version.version
                channel = agent_version.update_channel
                
                version_dist[version] = version_dist.get(version, 0) + 1
                channel_dist[channel] = channel_dist.get(channel, 0) + 1
            
            # Rollback statistics
            total_rollbacks = sum(len(rollbacks) for rollbacks in self.rollback_history.values())
            successful_rollbacks = 0
            for rollbacks in self.rollback_history.values():
                successful_rollbacks += len([r for r in rollbacks if r.status == "completed"])
            
            return {
                "total_agents": total_agents,
                "active_updates": active_updates,
                "completed_updates": completed_updates,
                "failed_updates": failed_updates,
                "update_success_rate": completed_updates / max(completed_updates + failed_updates, 1),
                "available_updates": len(self.available_updates),
                "update_packages": len(self.update_packages),
                "total_rollbacks": total_rollbacks,
                "successful_rollbacks": successful_rollbacks,
                "rollback_success_rate": successful_rollbacks / max(total_rollbacks, 1),
                "version_distribution": version_dist,
                "channel_distribution": channel_dist,
                "auto_update_enabled": self.auto_update_enabled,
                "update_checker_running": self.update_checker_running,
                "rollback_monitor_running": self.rollback_monitor_running,
                "maintenance_window": self.maintenance_window
            }
            
        except Exception as e:
            self.logger.error(f"Error getting version statistics: {e}")
            return {}
    
    # Database Operations
    def store_agent_version_in_db(self, agent_version: AgentVersion):
        """Store agent version in database"""
        try:
            db_version = AgentVersionRecord(
                agent_id=agent_version.agent_id,
                version=agent_version.version,
                build_number=agent_version.build_number,
                commit_hash=agent_version.commit_hash,
                build_date=agent_version.build_date,
                capabilities=agent_version.capabilities,
                dependencies=agent_version.dependencies,
                features=agent_version.features,
                platform=agent_version.platform,
                architecture=agent_version.architecture,
                update_channel=agent_version.update_channel,
                last_seen=agent_version.last_seen
            )
            
            self.node_server.db.session.merge(db_version)
            self.node_server.db.session.commit()
        except Exception as e:
            self.logger.error(f"Failed to store agent version: {e}")
    
    def store_update_package_in_db(self, update_package: UpdatePackage):
        """Store update package in database"""
        try:
            db_package = UpdatePackageRecord(
                id=update_package.id,
                version=update_package.version,
                channel=update_package.channel,
                release_date=update_package.release_date,
                update_type=update_package.update_type,
                download_url=update_package.download_url,
                checksum=update_package.checksum,
                size_bytes=update_package.size_bytes,
                description=update_package.description,
                changelog=update_package.changelog,
                requirements=update_package.requirements,
                compatibility=update_package.compatibility,
                rollback_supported=update_package.rollback_supported,
                critical=update_package.critical
            )
            
            self.node_server.db.session.merge(db_package)
            self.node_server.db.session.commit()
        except Exception as e:
            self.logger.error(f"Failed to store update package: {e}")
    
    def store_agent_update_in_db(self, agent_update: AgentUpdate):
        """Store agent update in database"""
        try:
            db_update = AgentUpdateRecord(
                id=agent_update.id,
                agent_id=agent_update.agent_id,
                package_id=agent_update.package_id,
                from_version=agent_update.from_version,
                to_version=agent_update.to_version,
                update_type=agent_update.update_type,
                scheduled_time=agent_update.scheduled_time,
                started_at=agent_update.started_at,
                completed_at=agent_update.completed_at,
                status=agent_update.status,
                progress=agent_update.progress,
                strategy=agent_update.strategy,
                backup_path=agent_update.backup_path,
                error_message=agent_update.error_message,
                auto_rollback_enabled=agent_update.auto_rollback_enabled,
                rollback_threshold_minutes=agent_update.rollback_threshold_minutes
            )
            
            self.node_server.db.session.merge(db_update)
            self.node_server.db.session.commit()
        except Exception as e:
            self.logger.error(f"Failed to store agent update: {e}")
    
    def update_agent_update_in_db(self, agent_update: AgentUpdate):
        """Update agent update in database"""
        self.store_agent_update_in_db(agent_update)
    
    def store_rollback_operation_in_db(self, rollback_op: RollbackOperation):
        """Store rollback operation in database"""
        try:
            db_rollback = RollbackOperationRecord(
                id=rollback_op.id,
                agent_id=rollback_op.agent_id,
                update_id=rollback_op.update_id,
                from_version=rollback_op.from_version,
                to_version=rollback_op.to_version,
                rollback_type=rollback_op.rollback_type,
                backup_path=rollback_op.backup_path,
                initiated_by=rollback_op.initiated_by,
                reason=rollback_op.reason,
                started_at=rollback_op.started_at,
                completed_at=rollback_op.completed_at,
                status=rollback_op.status,
                error_message=rollback_op.error_message
            )
            
            self.node_server.db.session.merge(db_rollback)
            self.node_server.db.session.commit()
        except Exception as e:
            self.logger.error(f"Failed to store rollback operation: {e}")
    
    def update_rollback_operation_in_db(self, rollback_op: RollbackOperation):
        """Update rollback operation in database"""
        self.store_rollback_operation_in_db(rollback_op)