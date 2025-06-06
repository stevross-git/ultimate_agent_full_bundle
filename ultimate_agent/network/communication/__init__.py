#!/usr/bin/env python3
"""
ultimate_agent/network/communication/__init__.py
Network communication and node interaction
"""

import time
import requests
import threading
from typing import Dict, Any, Optional
import ssl
import json


class NetworkManager:
    """Manages network communication with nodes and other agents"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.session = requests.Session()
        self.connected_nodes = {}
        self.connection_stats = {
            'successful_requests': 0,
            'failed_requests': 0,
            'total_bytes_sent': 0,
            'total_bytes_received': 0,
            'last_successful_connection': None,
            'last_failed_connection': None
        }
        
        self._setup_session()
        print("🌐 Network manager initialized")
    
    def _setup_session(self):
        """Setup HTTP session with optimal configuration"""
        # Set headers
        self.session.headers.update({
            'User-Agent': 'UltimatePainNetworkAgent-Modular/3.0.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Connection': 'keep-alive'
        })
        
        # Configure timeouts
        self.session.timeout = self.config.getint('NETWORK', 'connection_timeout', fallback=30)
        
        # Configure SSL if enabled
        if self.config.getboolean('NETWORK', 'use_ssl', fallback=True):
            self.session.verify = True
        
        # Configure retries
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=self.config.getint('NETWORK', 'retry_attempts', fallback=3),
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def register_agent(self, agent_id: str, capabilities: Dict[str, Any]) -> bool:
        """Register agent with node server"""
        try:
            # Get node URL from agent
            node_url = getattr(self, '_node_url', None)
            if not node_url:
                return False
            
            registration_data = {
                **capabilities,
                "modular_architecture": True,
                "network_manager_version": "1.0.0",
                "communication_features": ["websocket", "rest", "real_time"],
                "protocol_support": ["http", "https", "websocket"]
            }
            
            # Try multiple API versions
            endpoints = [
                f"{node_url}/api/v4/agents/register",
                f"{node_url}/api/v3/agents/register",
                f"{node_url}/api/agents/register"
            ]
            
            for endpoint in endpoints:
                try:
                    response = self._make_request('POST', endpoint, json=registration_data)
                    
                    if response and response.get("success"):
                        self.connected_nodes[node_url] = {
                            'endpoint': endpoint,
                            'connected_at': time.time(),
                            'last_heartbeat': time.time(),
                            'status': 'connected',
                            'api_version': endpoint.split('/')[-3] if 'v' in endpoint else 'v1'
                        }
                        
                        self.connection_stats['successful_requests'] += 1
                        self.connection_stats['last_successful_connection'] = time.time()
                        
                        print(f"✅ Agent registered with {endpoint}")
                        return True
                    else:
                        print(f"⚠️ Registration failed: {response.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"⚠️ Failed to connect to {endpoint}: {e}")
                    continue
            
            self.connection_stats['failed_requests'] += 1
            self.connection_stats['last_failed_connection'] = time.time()
            return False
            
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def send_heartbeat(self, agent_id: str, status_data: Dict[str, Any]) -> bool:
        """Send heartbeat to connected nodes"""
        if not self.connected_nodes:
            return False
        
        heartbeat_data = {
            **status_data,
            "network_stats": self.get_connection_stats(),
            "communication_quality": self._assess_connection_quality(),
            "modular_heartbeat": True
        }
        
        success_count = 0
        total_nodes = len(self.connected_nodes)
        
        for node_url, node_info in self.connected_nodes.items():
            try:
                # Use the same API version that worked for registration
                api_version = node_info.get('api_version', 'v1')
                if api_version == 'v1':
                    endpoint = f"{node_url}/api/agents/heartbeat"
                else:
                    endpoint = f"{node_url}/api/{api_version}/agents/heartbeat"
                
                response = self._make_request('POST', endpoint, json=heartbeat_data)
                
                if response and response.get("success"):
                    node_info['last_heartbeat'] = time.time()
                    node_info['status'] = 'connected'
                    success_count += 1
                    self.connection_stats['successful_requests'] += 1
                else:
                    node_info['status'] = 'heartbeat_failed'
                    print(f"⚠️ Heartbeat failed for {node_url}: {response.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Heartbeat error for {node_url}: {e}")
                node_info['status'] = 'error'
                self.connection_stats['failed_requests'] += 1
        
        return success_count > 0
    
    def _make_request(self, method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make HTTP request with error handling and stats tracking"""
        try:
            # Calculate request size for stats
            request_data = kwargs.get('json', {})
            request_size = len(json.dumps(request_data)) if request_data else 0
            self.connection_stats['total_bytes_sent'] += request_size
            
            response = self.session.request(method, url, **kwargs)
            
            # Calculate response size for stats
            response_size = len(response.content) if response.content else 0
            self.connection_stats['total_bytes_received'] += response_size
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ HTTP {response.status_code} for {method} {url}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"⏰ Request timeout for {method} {url}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"🔌 Connection error for {method} {url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"🌐 Request error for {method} {url}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error for {method} {url}: {e}")
            return None
    
    def _assess_connection_quality(self) -> str:
        """Assess connection quality based on success rate"""
        total_requests = (self.connection_stats['successful_requests'] + 
                         self.connection_stats['failed_requests'])
        
        if total_requests == 0:
            return "unknown"
        
        success_rate = self.connection_stats['successful_requests'] / total_requests
        
        if success_rate >= 0.95:
            return "excellent"
        elif success_rate >= 0.85:
            return "good"
        elif success_rate >= 0.70:
            return "fair"
        else:
            return "poor"
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get detailed connection statistics"""
        total_requests = (self.connection_stats['successful_requests'] + 
                         self.connection_stats['failed_requests'])
        
        success_rate = 0
        if total_requests > 0:
            success_rate = self.connection_stats['successful_requests'] / total_requests
        
        return {
            **self.connection_stats,
            'total_requests': total_requests,
            'success_rate': success_rate,
            'connection_quality': self._assess_connection_quality(),
            'connected_nodes': len(self.connected_nodes),
            'active_connections': len([n for n in self.connected_nodes.values() 
                                     if n['status'] == 'connected'])
        }
    
    def get_node_info(self, node_url: str) -> Optional[Dict[str, Any]]:
        """Get information about specific node"""
        return self.connected_nodes.get(node_url)
    
    def disconnect_from_node(self, node_url: str) -> bool:
        """Disconnect from specific node"""
        if node_url in self.connected_nodes:
            del self.connected_nodes[node_url]
            print(f"🔌 Disconnected from {node_url}")
            return True
        return False
    
    def test_connection(self, url: str) -> Dict[str, Any]:
        """Test connection to specific URL"""
        start_time = time.time()
        
        try:
            response = self._make_request('GET', f"{url}/api/health")
            end_time = time.time()
            
            return {
                'success': response is not None,
                'response_time_ms': (end_time - start_time) * 1000,
                'status': 'healthy' if response else 'unhealthy',
                'response': response
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'error'
            }
    
    def discover_nodes(self, discovery_urls: list) -> Dict[str, Any]:
        """Discover available nodes from discovery service"""
        discovered_nodes = {}
        
        for discovery_url in discovery_urls:
            try:
                response = self._make_request('GET', f"{discovery_url}/api/nodes")
                
                if response and 'nodes' in response:
                    for node in response['nodes']:
                        node_url = node.get('url')
                        if node_url:
                            # Test connection to node
                            test_result = self.test_connection(node_url)
                            discovered_nodes[node_url] = {
                                **node,
                                'discovered_from': discovery_url,
                                'test_result': test_result,
                                'discovered_at': time.time()
                            }
                            
            except Exception as e:
                print(f"⚠️ Node discovery failed for {discovery_url}: {e}")
        
        return discovered_nodes
    
    def set_node_url(self, node_url: str):
        """Set the primary node URL"""
        self._node_url = node_url.rstrip('/')
    
    def get_status(self) -> Dict[str, Any]:
        """Get network manager status"""
        return {
            'connected_nodes': len(self.connected_nodes),
            'active_connections': len([n for n in self.connected_nodes.values() 
                                     if n['status'] == 'connected']),
            'connection_quality': self._assess_connection_quality(),
            'total_requests': (self.connection_stats['successful_requests'] + 
                              self.connection_stats['failed_requests']),
            'success_rate': self.get_connection_stats()['success_rate'],
            'bytes_transferred': {
                'sent': self.connection_stats['total_bytes_sent'],
                'received': self.connection_stats['total_bytes_received']
            },
            'last_activity': max(
                self.connection_stats.get('last_successful_connection', 0),
                self.connection_stats.get('last_failed_connection', 0)
            ) if any([
                self.connection_stats.get('last_successful_connection'),
                self.connection_stats.get('last_failed_connection')
            ]) else None
        }
    
    def optimize_connections(self) -> Dict[str, Any]:
        """Optimize network connections"""
        optimizations = []
        
        # Remove dead connections
        dead_nodes = []
        current_time = time.time()
        
        for node_url, node_info in self.connected_nodes.items():
            # Consider connection dead if no heartbeat for 5 minutes
            if current_time - node_info.get('last_heartbeat', 0) > 300:
                dead_nodes.append(node_url)
        
        for node_url in dead_nodes:
            self.disconnect_from_node(node_url)
            optimizations.append(f"Removed dead connection: {node_url}")
        
        # Adjust timeouts based on connection quality
        quality = self._assess_connection_quality()
        if quality in ['poor', 'fair']:
            # Increase timeout for poor connections
            new_timeout = min(60, self.session.timeout * 1.5)
            self.session.timeout = new_timeout
            optimizations.append(f"Increased timeout to {new_timeout}s due to {quality} connection quality")
        
        return {
            'optimizations_applied': len(optimizations),
            'optimizations': optimizations,
            'connections_cleaned': len(dead_nodes),
            'connection_quality': quality
        }
    
    def export_network_logs(self, filepath: str) -> bool:
        """Export network activity logs"""
        try:
            log_data = {
                'connection_stats': self.connection_stats,
                'connected_nodes': self.connected_nodes,
                'network_status': self.get_status(),
                'exported_at': time.time()
            }
            
            with open(filepath, 'w') as f:
                json.dump(log_data, f, indent=2, default=str)
            
            print(f"📄 Network logs exported to {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to export network logs: {e}")
            return False
    
    def reset_stats(self):
        """Reset connection statistics"""
        self.connection_stats = {
            'successful_requests': 0,
            'failed_requests': 0,
            'total_bytes_sent': 0,
            'total_bytes_received': 0,
            'last_successful_connection': None,
            'last_failed_connection': None
        }
        print("📊 Network statistics reset")
    
    def close(self):
        """Close network manager and cleanup connections"""
        try:
            self.session.close()
            self.connected_nodes.clear()
            print("🌐 Network manager closed")
        except Exception as e:
            print(f"⚠️ Network manager close warning: {e}")
