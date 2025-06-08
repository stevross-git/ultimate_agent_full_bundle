#!/usr/bin/env python3
"""
Enhanced Node Server CLI Management Tool
Comprehensive command-line interface for server management
"""

import click
import json
import requests
import time
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import yaml

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import NODE_PORT, METRICS_PORT, NODE_ID, NODE_VERSION


class EnhancedNodeCLI:
    """Enhanced Node Server CLI Manager"""
    
    def __init__(self, host: str = "localhost", port: int = NODE_PORT):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to server"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            click.echo(f"❌ Request failed: {e}", err=True)
            sys.exit(1)
    
    def get_node_stats(self) -> Dict[str, Any]:
        """Get node statistics"""
        return self.request('GET', '/api/v3/node/stats')
    
    def get_agents(self) -> Dict[str, Any]:
        """Get all agents"""
        return self.request('GET', '/api/v3/agents')
    
    def get_agent_details(self, agent_id: str) -> Dict[str, Any]:
        """Get specific agent details"""
        return self.request('GET', f'/api/v3/agents/{agent_id}')
    
    def send_command(self, agent_id: str, command_type: str, parameters: Dict = None) -> Dict[str, Any]:
        """Send command to agent"""
        data = {
            'command_type': command_type,
            'parameters': parameters or {}
        }
        return self.request('POST', f'/api/v5/remote/agents/{agent_id}/command', json=data)
    
    def create_bulk_operation(self, operation_type: str, target_agents: List[str], parameters: Dict = None) -> Dict[str, Any]:
        """Create bulk operation"""
        data = {
            'operation_type': operation_type,
            'target_agents': target_agents,
            'parameters': parameters or {}
        }
        return self.request('POST', '/api/v5/remote/bulk-operation', json=data)
    
    def schedule_command(self, agent_id: str, command_type: str, scheduled_time: str, parameters: Dict = None) -> Dict[str, Any]:
        """Schedule command"""
        data = {
            'agent_id': agent_id,
            'command_type': command_type,
            'scheduled_time': scheduled_time,
            'parameters': parameters or {}
        }
        return self.request('POST', '/api/v5/remote/schedule-command', json=data)
    
    def deploy_script(self, script_name: str, script_content: str, target_agents: List[str], script_type: str = "python") -> Dict[str, Any]:
        """Deploy script to agents"""
        data = {
            'script_name': script_name,
            'script_content': script_content,
            'script_type': script_type,
            'target_agents': target_agents
        }
        return self.request('POST', '/api/v5/remote/deploy-script', json=data)


# CLI Context
@click.group()
@click.option('--host', default='localhost', help='Server host')
@click.option('--port', default=NODE_PORT, help='Server port')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def cli(ctx, host, port, output_format):
    """Enhanced Node Server CLI Management Tool"""
    ctx.ensure_object(dict)
    ctx.obj['client'] = EnhancedNodeCLI(host, port)
    ctx.obj['format'] = output_format


def format_output(data: Any, format_type: str) -> str:
    """Format output based on format type"""
    if format_type == 'json':
        return json.dumps(data, indent=2, default=str)
    elif format_type == 'yaml':
        return yaml.dump(data, default_flow_style=False)
    else:
        return str(data)


def print_table(headers: List[str], rows: List[List[str]], title: str = None):
    """Print formatted table"""
    if title:
        click.echo(f"\n📊 {title}")
        click.echo("=" * (len(title) + 4))
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print header
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    click.echo(header_line)
    click.echo("-" * len(header_line))
    
    # Print rows
    for row in rows:
        row_line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        click.echo(row_line)
    
    click.echo()


# Node Management Commands
@cli.group()
def node():
    """Node management commands"""
    pass


@node.command()
@click.pass_context
def status(ctx):
    """Get node status and statistics"""
    client = ctx.obj['client']
    format_type = ctx.obj['format']
    
    try:
        stats = client.get_node_stats()
        
        if format_type == 'table':
            click.echo(f"\n🚀 Enhanced Node Server Status")
            click.echo(f"Node ID: {stats['node_id']}")
            click.echo(f"Version: {stats['node_version']}")
            click.echo(f"Timestamp: {stats['timestamp']}")
            click.echo()
            
            # Basic stats
            basic_stats = [
                ["Metric", "Value"],
                ["Total Agents", stats['total_agents']],
                ["Online Agents", stats['online_agents']],
                ["Offline Agents", stats['offline_agents']],
                ["Tasks Running", stats['total_tasks_running']],
                ["Tasks Completed", stats['total_tasks_completed']],
                ["Success Rate", f"{stats['success_rate']}%"],
                ["Health Score", f"{stats['health_score']:.1f}%"]
            ]
            
            print_table(basic_stats[0], basic_stats[1:], "Node Statistics")
            
            # Performance stats
            perf_stats = [
                ["Metric", "Value"],
                ["Avg CPU", f"{stats['avg_cpu_percent']:.1f}%"],
                ["Avg Memory", f"{stats['avg_memory_percent']:.1f}%"],
                ["Avg GPU", f"{stats['avg_gpu_percent']:.1f}%"],
                ["Efficiency", f"{stats['avg_efficiency_score']:.1f}%"],
                ["AI Models", stats['total_ai_models']],
                ["Blockchain Balance", f"{stats['total_blockchain_balance']:.3f} ETH"]
            ]
            
            print_table(perf_stats[0], perf_stats[1:], "Performance Metrics")
            
        else:
            click.echo(format_output(stats, format_type))
            
    except Exception as e:
        click.echo(f"❌ Failed to get node status: {e}", err=True)


@node.command()
@click.pass_context
def health(ctx):
    """Check node health"""
    client = ctx.obj['client']
    
    try:
        stats = client.get_node_stats()
        health_score = stats['health_score']
        
        if health_score >= 90:
            status = "🟢 Excellent"
        elif health_score >= 70:
            status = "🟡 Good"
        elif health_score >= 50:
            status = "🟠 Warning"
        else:
            status = "🔴 Critical"
        
        click.echo(f"Node Health: {status} ({health_score:.1f}%)")
        click.echo(f"Online Agents: {stats['online_agents']}/{stats['total_agents']}")
        click.echo(f"Task Success Rate: {stats['success_rate']:.1f}%")
        
    except Exception as e:
        click.echo(f"❌ Failed to check health: {e}", err=True)


# Agent Management Commands
@cli.group()
def agents():
    """Agent management commands"""
    pass


@agents.command()
@click.pass_context
def list(ctx):
    """List all agents"""
    client = ctx.obj['client']
    format_type = ctx.obj['format']
    
    try:
        data = client.get_agents()
        agents = data['agents']
        
        if format_type == 'table':
            if not agents:
                click.echo("No agents registered")
                return
            
            headers = ["Agent ID", "Name", "Status", "CPU%", "Memory%", "Tasks", "Efficiency%"]
            rows = []
            
            for agent in agents:
                status_icon = "🟢" if agent.get('status') == 'online' else "🔴"
                rows.append([
                    agent.get('id', 'N/A')[:20] + ('...' if len(agent.get('id', '')) > 20 else ''),
                    agent.get('name', 'N/A')[:15] + ('...' if len(agent.get('name', '')) > 15 else ''),
                    f"{status_icon} {agent.get('status', 'unknown')}",
                    f"{agent.get('cpu_percent', 0):.1f}",
                    f"{agent.get('memory_percent', 0):.1f}",
                    str(agent.get('tasks_running', 0)),
                    f"{agent.get('efficiency_score', 0):.1f}"
                ])
            
            print_table(headers, rows, f"Agents ({len(agents)} total)")
            
        else:
            click.echo(format_output(agents, format_type))
            
    except Exception as e:
        click.echo(f"❌ Failed to list agents: {e}", err=True)


@agents.command()
@click.argument('agent_id')
@click.pass_context
def details(ctx, agent_id):
    """Get detailed agent information"""
    client = ctx.obj['client']
    format_type = ctx.obj['format']
    
    try:
        data = client.get_agent_details(agent_id)
        
        if format_type == 'table':
            agent_info = data['agent_info']
            current_status = data['current_status']
            
            click.echo(f"\n🤖 Agent Details: {agent_id}")
            click.echo("=" * 50)
            click.echo(f"Name: {agent_info.get('name', 'N/A')}")
            click.echo(f"Host: {agent_info.get('host', 'N/A')}")
            click.echo(f"Version: {agent_info.get('version', 'N/A')}")
            click.echo(f"Type: {agent_info.get('agent_type', 'N/A')}")
            click.echo(f"Registered: {agent_info.get('registered_at', 'N/A')}")
            
            if current_status:
                click.echo(f"\n📊 Current Status:")
                click.echo(f"Status: {current_status.get('status', 'unknown')}")
                click.echo(f"CPU: {current_status.get('cpu_percent', 0):.1f}%")
                click.echo(f"Memory: {current_status.get('memory_percent', 0):.1f}%")
                click.echo(f"GPU: {current_status.get('gpu_percent', 0):.1f}%")
                click.echo(f"Tasks Running: {current_status.get('tasks_running', 0)}")
                click.echo(f"Tasks Completed: {current_status.get('tasks_completed', 0)}")
                click.echo(f"Efficiency: {current_status.get('efficiency_score', 0):.1f}%")
            
            if agent_info.get('capabilities'):
                click.echo(f"\n🛠️ Capabilities: {', '.join(agent_info['capabilities'])}")
            
            if agent_info.get('ai_models'):
                click.echo(f"🧠 AI Models: {', '.join(agent_info['ai_models'])}")
                
        else:
            click.echo(format_output(data, format_type))
            
    except Exception as e:
        click.echo(f"❌ Failed to get agent details: {e}", err=True)


# Remote Control Commands
@cli.group()
def remote():
    """Remote control commands"""
    pass


@remote.command()
@click.argument('agent_id')
@click.argument('command_type')
@click.option('--params', help='Command parameters as JSON string')
@click.pass_context
def command(ctx, agent_id, command_type, params):
    """Send command to agent"""
    client = ctx.obj['client']
    
    try:
        parameters = json.loads(params) if params else {}
        result = client.send_command(agent_id, command_type, parameters)
        
        if result.get('success'):
            click.echo(f"✅ Command '{command_type}' sent to agent {agent_id}")
            click.echo(f"Command ID: {result.get('command_id')}")
        else:
            click.echo(f"❌ Failed to send command: {result.get('error')}")
            
    except json.JSONDecodeError:
        click.echo("❌ Invalid JSON in parameters", err=True)
    except Exception as e:
        click.echo(f"❌ Failed to send command: {e}", err=True)


@remote.command('update')
@click.argument('agent_id')
@click.option('--repo', 'repo_path', default='.', help='Path to git repo on agent')
@click.option('--restart', is_flag=True, help='Restart agent after update')
@click.pass_context
def update_agent(ctx, agent_id, repo_path, restart):
    """Update single agent via remote command"""
    client = ctx.obj['client']

    try:
        parameters = {"repo_path": repo_path, "restart": restart}
        result = client.send_command(agent_id, 'update_agent', parameters)

        if result.get('success'):
            click.echo(f"✅ Update command sent to agent {agent_id}")
            click.echo(f"Command ID: {result.get('command_id')}")
        else:
            click.echo(f"❌ Failed to send update command: {result.get('error')}")

    except Exception as e:
        click.echo(f"❌ Failed to send update command: {e}", err=True)


@remote.command()
@click.argument('operation_type')
@click.option('--agents', help='Comma-separated list of agent IDs')
@click.option('--all-online', is_flag=True, help='Target all online agents')
@click.option('--params', help='Operation parameters as JSON string')
@click.pass_context
def bulk(ctx, operation_type, agents, all_online, params):
    """Execute bulk operation"""
    client = ctx.obj['client']
    
    try:
        if all_online:
            # Get all online agents
            data = client.get_agents()
            target_agents = [a['id'] for a in data['agents'] if a.get('status') == 'online']
        elif agents:
            target_agents = [a.strip() for a in agents.split(',')]
        else:
            click.echo("❌ Must specify either --agents or --all-online", err=True)
            return
        
        if not target_agents:
            click.echo("❌ No target agents specified", err=True)
            return
        
        parameters = json.loads(params) if params else {}
        result = client.create_bulk_operation(operation_type, target_agents, parameters)
        
        if result.get('success'):
            click.echo(f"✅ Bulk operation '{operation_type}' created for {len(target_agents)} agents")
            click.echo(f"Operation ID: {result.get('operation_id')}")
        else:
            click.echo(f"❌ Failed to create bulk operation: {result.get('error')}")
            
    except json.JSONDecodeError:
        click.echo("❌ Invalid JSON in parameters", err=True)
    except Exception as e:
        click.echo(f"❌ Failed to create bulk operation: {e}", err=True)


@remote.command('update-all')
@click.option('--agents', help='Comma-separated list of agent IDs')
@click.option('--all-online', is_flag=True, help='Target all online agents')
@click.option('--repo', 'repo_path', default='.', help='Path to git repo on agents')
@click.option('--restart', is_flag=True, help='Restart agents after update')
@click.pass_context
def update_all(ctx, agents, all_online, repo_path, restart):
    """Update multiple agents via bulk operation"""
    client = ctx.obj['client']

    try:
        if all_online:
            data = client.get_agents()
            target_agents = [a['id'] for a in data['agents'] if a.get('status') == 'online']
        elif agents:
            target_agents = [a.strip() for a in agents.split(',')]
        else:
            click.echo("❌ Must specify either --agents or --all-online", err=True)
            return

        if not target_agents:
            click.echo("❌ No target agents specified", err=True)
            return

        parameters = {"repo_path": repo_path, "restart": restart}
        result = client.create_bulk_operation('update_agent', target_agents, parameters)

        if result.get('success'):
            click.echo(f"✅ Update command sent to {len(target_agents)} agents")
            click.echo(f"Operation ID: {result.get('operation_id')}")
        else:
            click.echo(f"❌ Failed to create bulk update: {result.get('error')}")

    except Exception as e:
        click.echo(f"❌ Failed to create bulk update: {e}", err=True)


@remote.command()
@click.argument('agent_id')
@click.argument('command_type')
@click.argument('scheduled_time')
@click.option('--params', help='Command parameters as JSON string')
@click.pass_context
def schedule(ctx, agent_id, command_type, scheduled_time, params):
    """Schedule command execution"""
    client = ctx.obj['client']
    
    try:
        # Parse scheduled time
        if scheduled_time.startswith('+'):
            # Relative time (e.g., +1h, +30m)
            import re
            match = re.match(r'\+(\d+)([hm])', scheduled_time)
            if match:
                amount, unit = match.groups()
                delta = timedelta(hours=int(amount)) if unit == 'h' else timedelta(minutes=int(amount))
                target_time = (datetime.now() + delta).isoformat() + 'Z'
            else:
                click.echo("❌ Invalid relative time format. Use +Nh or +Nm", err=True)
                return
        else:
            # Absolute time
            target_time = scheduled_time
        
        parameters = json.loads(params) if params else {}
        result = client.schedule_command(agent_id, command_type, target_time, parameters)
        
        if result.get('success'):
            click.echo(f"✅ Command '{command_type}' scheduled for agent {agent_id}")
            click.echo(f"Scheduled Command ID: {result.get('scheduled_command_id')}")
            click.echo(f"Execution time: {target_time}")
        else:
            click.echo(f"❌ Failed to schedule command: {result.get('error')}")
            
    except json.JSONDecodeError:
        click.echo("❌ Invalid JSON in parameters", err=True)
    except Exception as e:
        click.echo(f"❌ Failed to schedule command: {e}", err=True)


# Script Management Commands
@cli.group()
def scripts():
    """Script management commands"""
    pass


@scripts.command()
@click.argument('script_name')
@click.argument('script_file', type=click.File('r'))
@click.option('--agents', help='Comma-separated list of agent IDs')
@click.option('--all-online', is_flag=True, help='Deploy to all online agents')
@click.option('--type', 'script_type', default='python', help='Script type')
@click.pass_context
def deploy(ctx, script_name, script_file, agents, all_online, script_type):
    """Deploy script to agents"""
    client = ctx.obj['client']
    
    try:
        script_content = script_file.read()
        
        if all_online:
            # Get all online agents
            data = client.get_agents()
            target_agents = [a['id'] for a in data['agents'] if a.get('status') == 'online']
        elif agents:
            target_agents = [a.strip() for a in agents.split(',')]
        else:
            click.echo("❌ Must specify either --agents or --all-online", err=True)
            return
        
        if not target_agents:
            click.echo("❌ No target agents specified", err=True)
            return
        
        result = client.deploy_script(script_name, script_content, target_agents, script_type)
        
        if result.get('success'):
            click.echo(f"✅ Script '{script_name}' deployed to {len(target_agents)} agents")
            click.echo(f"Script ID: {result.get('script_id')}")
            
            # Show deployment results
            deployment_results = result.get('deployment_results', {})
            for agent_id, status in deployment_results.items():
                status_icon = "✅" if status == "deployed" else "❌"
                click.echo(f"  {status_icon} {agent_id}: {status}")
        else:
            click.echo(f"❌ Failed to deploy script: {result.get('error')}")
            
    except Exception as e:
        click.echo(f"❌ Failed to deploy script: {e}", err=True)


# Monitoring Commands
@cli.group()
def monitor():
    """Monitoring commands"""
    pass


@monitor.command()
@click.option('--interval', default=5, help='Update interval in seconds')
@click.option('--count', default=0, help='Number of updates (0 = infinite)')
@click.pass_context
def live(ctx, interval, count):
    """Live monitoring of node status"""
    client = ctx.obj['client']
    
    try:
        updates = 0
        while count == 0 or updates < count:
            # Clear screen
            click.clear()
            
            # Get current stats
            stats = client.get_node_stats()
            agents_data = client.get_agents()
            
            # Display header
            click.echo(f"🚀 Enhanced Node Server - Live Monitor")
            click.echo(f"Node: {stats['node_id']} | Version: {stats['node_version']}")
            click.echo(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            click.echo("=" * 60)
            
            # Quick stats
            click.echo(f"Agents: {stats['online_agents']}/{stats['total_agents']} online")
            click.echo(f"Tasks: {stats['total_tasks_running']} running, {stats['total_tasks_completed']} completed")
            click.echo(f"Health: {stats['health_score']:.1f}% | Success Rate: {stats['success_rate']:.1f}%")
            click.echo()
            
            # Agent status table
            agents = agents_data['agents']
            if agents:
                headers = ["Agent", "Status", "CPU", "Memory", "Tasks", "Efficiency"]
                rows = []
                
                for agent in agents[:10]:  # Show top 10
                    status_icon = "🟢" if agent.get('status') == 'online' else "🔴"
                    rows.append([
                        agent.get('id', 'N/A')[:15],
                        f"{status_icon}",
                        f"{agent.get('cpu_percent', 0):.1f}%",
                        f"{agent.get('memory_percent', 0):.1f}%",
                        str(agent.get('tasks_running', 0)),
                        f"{agent.get('efficiency_score', 0):.1f}%"
                    ])
                
                print_table(headers, rows)
            
            click.echo(f"Press Ctrl+C to exit | Update #{updates + 1}")
            
            if count > 0 and updates >= count - 1:
                break
            
            time.sleep(interval)
            updates += 1
            
    except KeyboardInterrupt:
        click.echo("\n👋 Monitoring stopped")
    except Exception as e:
        click.echo(f"❌ Monitoring failed: {e}", err=True)


# Utility Commands
@cli.group()
def utils():
    """Utility commands"""
    pass


@utils.command()
@click.pass_context
def test_connection(ctx):
    """Test connection to server"""
    client = ctx.obj['client']
    
    try:
        start_time = time.time()
        stats = client.get_node_stats()
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        click.echo(f"✅ Connection successful!")
        click.echo(f"Server: {client.base_url}")
        click.echo(f"Node ID: {stats['node_id']}")
        click.echo(f"Version: {stats['node_version']}")
        click.echo(f"Response time: {response_time:.1f}ms")
        
    except Exception as e:
        click.echo(f"❌ Connection failed: {e}", err=True)


@utils.command()
@click.option('--output', type=click.File('w'), help='Output file')
@click.pass_context
def export_config(ctx, output):
    """Export current configuration"""
    client = ctx.obj['client']
    
    try:
        stats = client.get_node_stats()
        agents_data = client.get_agents()
        
        config = {
            'node': {
                'id': stats['node_id'],
                'version': stats['node_version'],
                'export_time': datetime.now().isoformat()
            },
            'agents': agents_data['agents'],
            'statistics': stats
        }
        
        output_text = yaml.dump(config, default_flow_style=False)
        
        if output:
            output.write(output_text)
            click.echo(f"✅ Configuration exported to {output.name}")
        else:
            click.echo(output_text)
            
    except Exception as e:
        click.echo(f"❌ Export failed: {e}", err=True)


if __name__ == '__main__':
    cli()
