#!/usr/bin/env python3
"""
ultimate_agent/utils/__init__.py
Common utilities and helper functions for the agent
"""

import os
import sys
import time
import json
import hashlib
import platform
import subprocess
import threading
import queue
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable
from pathlib import Path
import logging


class AgentUtils:
    """Collection of utility functions for the agent"""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get comprehensive system information"""
        import psutil
        
        try:
            # Basic system info
            system_info = {
                'platform': {
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'machine': platform.machine(),
                    'processor': platform.processor(),
                    'python_version': platform.python_version(),
                    'python_implementation': platform.python_implementation()
                },
                'hardware': {
                    'cpu_cores_physical': psutil.cpu_count(logical=False),
                    'cpu_cores_logical': psutil.cpu_count(logical=True),
                    'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                    'disk_total_gb': round(psutil.disk_usage('/').total / (1024**3), 2),
                    'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
                },
                'network': {
                    'hostname': platform.node(),
                    'interfaces': len(psutil.net_if_addrs())
                }
            }
            
            # CPU frequency if available
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    system_info['hardware']['cpu_frequency_mhz'] = {
                        'current': cpu_freq.current,
                        'min': cpu_freq.min,
                        'max': cpu_freq.max
                    }
            except:
                pass
            
            # GPU information
            gpu_info = AgentUtils.get_gpu_info()
            if gpu_info:
                system_info['gpu'] = gpu_info
            
            return system_info
            
        except Exception as e:
            return {'error': f'Failed to get system info: {e}'}
    
    @staticmethod
    def get_gpu_info() -> Optional[Dict[str, Any]]:
        """Get GPU information if available"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            
            if gpus:
                gpu_info = []
                for gpu in gpus:
                    gpu_info.append({
                        'id': gpu.id,
                        'name': gpu.name,
                        'driver': gpu.driver,
                        'memory_total_mb': gpu.memoryTotal,
                        'memory_free_mb': gpu.memoryFree,
                        'memory_used_mb': gpu.memoryUsed,
                        'memory_util_percent': gpu.memoryUtil * 100,
                        'gpu_util_percent': gpu.load * 100,
                        'temperature': gpu.temperature
                    })
                
                return {
                    'available': True,
                    'count': len(gpus),
                    'gpus': gpu_info
                }
        except ImportError:
            pass
        except Exception as e:
            return {'available': False, 'error': str(e)}
        
        return {'available': False}
    
    @staticmethod
    def generate_unique_id(prefix: str = "", length: int = 8) -> str:
        """Generate a unique identifier"""
        import uuid
        import secrets
        
        if prefix:
            return f"{prefix}_{secrets.token_hex(length//2)}"
        else:
            return secrets.token_hex(length//2)
    
    @staticmethod
    def hash_data(data: Union[str, bytes, Dict[str, Any]], algorithm: str = 'sha256') -> str:
        """Hash data using specified algorithm"""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        elif isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm == 'sha256':
            return hashlib.sha256(data).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(data).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(data).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    @staticmethod
    def safe_json_load(filepath: str, default: Any = None) -> Any:
        """Safely load JSON file with fallback"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return default
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON decode error in {filepath}: {e}")
            return default
        except Exception as e:
            print(f"⚠️ Error loading {filepath}: {e}")
            return default
    
    @staticmethod
    def safe_json_save(data: Any, filepath: str, indent: int = 2) -> bool:
        """Safely save data to JSON file"""
        try:
            # Create directory if it doesn't exist
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file first
            temp_filepath = f"{filepath}.tmp"
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, default=str)
            
            # Atomic move
            if os.path.exists(filepath):
                backup_filepath = f"{filepath}.backup"
                os.rename(filepath, backup_filepath)
            
            os.rename(temp_filepath, filepath)
            
            # Clean up backup
            backup_filepath = f"{filepath}.backup"
            if os.path.exists(backup_filepath):
                os.remove(backup_filepath)
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving {filepath}: {e}")
            
            # Clean up temp file
            temp_filepath = f"{filepath}.tmp"
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except:
                    pass
            
            return False
    
    @staticmethod
    def format_bytes(bytes_value: Union[int, float]) -> str:
        """Format bytes into human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds into human readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}h"
        else:
            days = seconds / 86400
            return f"{days:.1f}d"
    
    @staticmethod
    def get_available_port(start_port: int = 8000, max_attempts: int = 100) -> Optional[int]:
        """Find an available port starting from start_port"""
        import socket
        
        for port in range(start_port, start_port + max_attempts):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                
                if result != 0:  # Port is available
                    return port
            except Exception:
                continue
        
        return None
    
    @staticmethod
    def run_command(command: Union[str, List[str]], timeout: int = 30, capture_output: bool = True) -> Dict[str, Any]:
        """Run system command with timeout"""
        try:
            if isinstance(command, str):
                command = command.split()
            
            result = subprocess.run(
                command,
                timeout=timeout,
                capture_output=capture_output,
                text=True
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout if capture_output else None,
                'stderr': result.stderr if capture_output else None,
                'command': ' '.join(command)
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Command timeout',
                'timeout': timeout,
                'command': ' '.join(command)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': ' '.join(command)
            }
    
    @staticmethod
    def check_dependencies() -> Dict[str, Any]:
        """Check if required dependencies are available"""
        dependencies = {
            'required': [
                'requests', 'flask', 'flask_cors', 'flask_socketio',
                'numpy', 'psutil', 'sqlalchemy'
            ],
            'optional': [
                'torch', 'pandas', 'GPUtil', 'cryptography'
            ]
        }
        
        results = {
            'all_required_available': True,
            'required': {},
            'optional': {},
            'missing_required': [],
            'missing_optional': []
        }
        
        # Check required dependencies
        for dep in dependencies['required']:
            try:
                __import__(dep)
                results['required'][dep] = {'available': True}
            except ImportError as e:
                results['required'][dep] = {'available': False, 'error': str(e)}
                results['missing_required'].append(dep)
                results['all_required_available'] = False
        
        # Check optional dependencies
        for dep in dependencies['optional']:
            try:
                __import__(dep)
                results['optional'][dep] = {'available': True}
            except ImportError as e:
                results['optional'][dep] = {'available': False, 'error': str(e)}
                results['missing_optional'].append(dep)
        
        return results
    
    @staticmethod
    def create_directory_structure(base_path: str, structure: Dict[str, Any]) -> bool:
        """Create directory structure from nested dictionary"""
        try:
            base_path = Path(base_path)
            
            def create_recursive(current_path: Path, struct: Dict[str, Any]):
                for name, content in struct.items():
                    new_path = current_path / name
                    
                    if isinstance(content, dict):
                        # It's a directory
                        new_path.mkdir(exist_ok=True)
                        create_recursive(new_path, content)
                    else:
                        # It's a file
                        new_path.parent.mkdir(parents=True, exist_ok=True)
                        if content:  # Write content if provided
                            with open(new_path, 'w', encoding='utf-8') as f:
                                f.write(str(content))
                        else:
                            # Create empty file
                            new_path.touch()
            
            create_recursive(base_path, structure)
            return True
            
        except Exception as e:
            print(f"❌ Error creating directory structure: {e}")
            return False


class AsyncTaskRunner:
    """Utility for running async tasks with thread pool"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.task_queue = queue.Queue()
        self.results = {}
        self.workers = []
        self.running = False
    
    def start(self):
        """Start the task runner"""
        if self.running:
            return
        
        self.running = True
        
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                daemon=True,
                name=f"AsyncWorker-{i}"
            )
            worker.start()
            self.workers.append(worker)
        
        print(f"🚀 Async task runner started with {self.max_workers} workers")
    
    def stop(self):
        """Stop the task runner"""
        self.running = False
        
        # Add stop signals for all workers
        for _ in range(self.max_workers):
            self.task_queue.put(None)
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5)
        
        self.workers.clear()
        print("🛑 Async task runner stopped")
    
    def submit_task(self, task_id: str, func: Callable, *args, **kwargs) -> str:
        """Submit a task for async execution"""
        if not self.running:
            self.start()
        
        task = {
            'task_id': task_id,
            'function': func,
            'args': args,
            'kwargs': kwargs,
            'submitted_at': time.time()
        }
        
        self.task_queue.put(task)
        self.results[task_id] = {'status': 'queued', 'submitted_at': time.time()}
        
        return task_id
    
    def get_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get result of a submitted task"""
        return self.results.get(task_id)
    
    def _worker_loop(self):
        """Worker thread loop"""
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                
                if task is None:  # Stop signal
                    break
                
                task_id = task['task_id']
                
                # Update status
                self.results[task_id] = {
                    'status': 'running',
                    'started_at': time.time()
                }
                
                try:
                    # Execute task
                    result = task['function'](*task['args'], **task['kwargs'])
                    
                    # Store result
                    self.results[task_id] = {
                        'status': 'completed',
                        'result': result,
                        'completed_at': time.time(),
                        'duration': time.time() - self.results[task_id]['started_at']
                    }
                    
                except Exception as e:
                    # Store error
                    self.results[task_id] = {
                        'status': 'failed',
                        'error': str(e),
                        'failed_at': time.time()
                    }
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Worker error: {e}")


class PerformanceProfiler:
    """Simple performance profiling utility"""
    
    def __init__(self):
        self.profiles = {}
        self.current_profile = None
    
    def start_profile(self, profile_name: str):
        """Start profiling a section"""
        self.current_profile = profile_name
        self.profiles[profile_name] = {
            'start_time': time.time(),
            'end_time': None,
            'duration': None,
            'memory_start': self._get_memory_usage()
        }
    
    def end_profile(self, profile_name: str = None):
        """End profiling a section"""
        if profile_name is None:
            profile_name = self.current_profile
        
        if profile_name and profile_name in self.profiles:
            profile = self.profiles[profile_name]
            profile['end_time'] = time.time()
            profile['duration'] = profile['end_time'] - profile['start_time']
            profile['memory_end'] = self._get_memory_usage()
            profile['memory_delta'] = profile['memory_end'] - profile['memory_start']
            
            if profile_name == self.current_profile:
                self.current_profile = None
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except:
            return 0.0
    
    def get_profile_results(self) -> Dict[str, Any]:
        """Get all profile results"""
        return self.profiles.copy()
    
    def print_profile_summary(self):
        """Print a summary of all profiles"""
        print("\n📊 Performance Profile Summary:")
        print("-" * 50)
        
        for name, profile in self.profiles.items():
            if profile.get('duration') is not None:
                duration = AgentUtils.format_duration(profile['duration'])
                memory_delta = profile.get('memory_delta', 0)
                print(f"  {name}: {duration} (Δmem: {memory_delta:+.1f}MB)")
            else:
                print(f"  {name}: [RUNNING]")


class ConfigValidator:
    """Utility for validating configuration"""
    
    @staticmethod
    def validate_config_section(config: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration section against schema"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required fields
        required_fields = schema.get('required', [])
        for field in required_fields:
            if field not in config:
                results['errors'].append(f"Missing required field: {field}")
                results['valid'] = False
        
        # Check field types and values
        field_schemas = schema.get('fields', {})
        for field, field_schema in field_schemas.items():
            if field not in config:
                continue
            
            value = config[field]
            expected_type = field_schema.get('type')
            
            # Type checking
            if expected_type:
                if expected_type == 'int' and not isinstance(value, int):
                    results['errors'].append(f"Field {field} must be integer, got {type(value).__name__}")
                    results['valid'] = False
                elif expected_type == 'float' and not isinstance(value, (int, float)):
                    results['errors'].append(f"Field {field} must be number, got {type(value).__name__}")
                    results['valid'] = False
                elif expected_type == 'str' and not isinstance(value, str):
                    results['errors'].append(f"Field {field} must be string, got {type(value).__name__}")
                    results['valid'] = False
                elif expected_type == 'bool' and not isinstance(value, bool):
                    results['errors'].append(f"Field {field} must be boolean, got {type(value).__name__}")
                    results['valid'] = False
            
            # Range checking
            min_value = field_schema.get('min')
            max_value = field_schema.get('max')
            
            if min_value is not None and isinstance(value, (int, float)) and value < min_value:
                results['errors'].append(f"Field {field} must be >= {min_value}, got {value}")
                results['valid'] = False
            
            if max_value is not None and isinstance(value, (int, float)) and value > max_value:
                results['errors'].append(f"Field {field} must be <= {max_value}, got {value}")
                results['valid'] = False
            
            # Allowed values
            allowed_values = field_schema.get('allowed')
            if allowed_values and value not in allowed_values:
                results['errors'].append(f"Field {field} must be one of {allowed_values}, got {value}")
                results['valid'] = False
        
        return results


class ColoredLogger:
    """Utility for colored logging output"""
    
    COLORS = {
        'HEADER': '\033[95m',
        'OKBLUE': '\033[94m',
        'OKCYAN': '\033[96m',
        'OKGREEN': '\033[92m',
        'WARNING': '\033[93m',
        'FAIL': '\033[91m',
        'ENDC': '\033[0m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m'
    }
    
    @classmethod
    def info(cls, message: str):
        """Log info message"""
        print(f"{cls.COLORS['OKBLUE']}ℹ️  {message}{cls.COLORS['ENDC']}")
    
    @classmethod
    def success(cls, message: str):
        """Log success message"""
        print(f"{cls.COLORS['OKGREEN']}✅ {message}{cls.COLORS['ENDC']}")
    
    @classmethod
    def warning(cls, message: str):
        """Log warning message"""
        print(f"{cls.COLORS['WARNING']}⚠️  {message}{cls.COLORS['ENDC']}")
    
    @classmethod
    def error(cls, message: str):
        """Log error message"""
        print(f"{cls.COLORS['FAIL']}❌ {message}{cls.COLORS['ENDC']}")
    
    @classmethod
    def header(cls, message: str):
        """Log header message"""
        print(f"{cls.COLORS['HEADER']}{cls.COLORS['BOLD']}🚀 {message}{cls.COLORS['ENDC']}")


# Export utility classes and functions
__all__ = [
    'AgentUtils',
    'AsyncTaskRunner', 
    'PerformanceProfiler',
    'ConfigValidator',
    'ColoredLogger'
]
