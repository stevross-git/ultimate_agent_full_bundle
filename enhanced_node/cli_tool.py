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
import requests
import json
from datetime import datetime, timedelta
from tabulate import tabulate

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


def add_version_commands(cli_parser):
    """Add version control commands to CLI parser"""
    
    # Version control main command
    version_parser = cli_parser.add_subparser('version', help='Version control operations')
    version_subparsers = version_parser.add_subparsers(dest='version_command', help='Version control commands')
    
    # Agent version commands
    agents_parser = version_subparsers.add_parser('agents', help='Agent version management')
    agents_subparsers = agents_parser.add_subparsers(dest='agents_command', help='Agent commands')
    
    # List agent versions
    list_parser = agents_subparsers.add_parser('list', help='List agent versions')
    list_parser.add_argument('--channel', help='Filter by update channel')
    list_parser.add_argument('--platform', help='Filter by platform')
    
    # Get agent version details
    details_parser = agents_subparsers.add_parser('details', help='Get agent version details')
    details_parser.add_argument('agent_id', help='Agent ID')
    
    # Agent version history
    history_parser = agents_subparsers.add_parser('history', help='Get agent version history')
    history_parser.add_argument('agent_id', help='Agent ID')
    history_parser.add_argument('--limit', type=int, default=10, help='Number of records to show')
    
    # Update commands
    update_parser = version_subparsers.add_parser('update', help='Update management')
    update_subparsers = update_parser.add_subparsers(dest='update_command', help='Update commands')
    
    # Check for updates
    check_parser = update_subparsers.add_parser('check', help='Check for available updates')
    
    # List available updates
    available_parser = update_subparsers.add_parser('available', help='List available updates')
    available_parser.add_argument('--channel', help='Filter by channel')
    
    # Schedule update
    schedule_parser = update_subparsers.add_parser('schedule', help='Schedule agent update')
    schedule_parser.add_argument('agent_id', help='Agent ID')
    schedule_parser.add_argument('package_id', help='Update package ID')
    schedule_parser.add_argument('--strategy', default='rolling', help='Update strategy')
    schedule_parser.add_argument('--time', help='Scheduled time (ISO format)')
    
    # List active updates
    active_parser = update_subparsers.add_parser('active', help='List active updates')
    active_parser.add_argument('--agent', help='Filter by agent ID')
    active_parser.add_argument('--status', help='Filter by status')
    
    # Cancel update
    cancel_parser = update_subparsers.add_parser('cancel', help='Cancel scheduled update')
    cancel_parser.add_argument('update_id', help='Update ID')
    
    # Bulk update
    bulk_parser = update_subparsers.add_parser('bulk', help='Bulk update agents')
    bulk_parser.add_argument('package_id', help='Update package ID')
    bulk_parser.add_argument('--agents', nargs='+', help='Specific agent IDs')
    bulk_parser.add_argument('--all-online', action='store_true', help='Update all online agents')
    bulk_parser.add_argument('--channel', help='Update agents on specific channel')
    bulk_parser.add_argument('--strategy', default='rolling', help='Update strategy')
    bulk_parser.add_argument('--delay', type=int, default=5, help='Delay between updates (minutes)')
    
    # Rollback commands
    rollback_parser = version_subparsers.add_parser('rollback', help='Rollback management')
    rollback_subparsers = rollback_parser.add_subparsers(dest='rollback_command', help='Rollback commands')
    
    # Initiate rollback
    initiate_parser = rollback_subparsers.add_parser('initiate', help='Initiate agent rollback')
    initiate_parser.add_argument('agent_id', help='Agent ID')
    initiate_parser.add_argument('--to-version', help='Target version')
    initiate_parser.add_argument('--reason', default='Manual CLI rollback', help='Rollback reason')
    
    # Rollback history
    rollback_history_parser = rollback_subparsers.add_parser('history', help='Rollback history')
    rollback_history_parser.add_argument('--agent', help='Filter by agent ID')
    rollback_history_parser.add_argument('--limit', type=int, default=20, help='Number of records')
    
    # Bulk rollback
    bulk_rollback_parser = rollback_subparsers.add_parser('bulk', help='Bulk rollback agents')
    bulk_rollback_parser.add_argument('--agents', nargs='+', help='Specific agent IDs')
    bulk_rollback_parser.add_argument('--hours', type=int, default=24, help='Rollback agents updated in last X hours')
    bulk_rollback_parser.add_argument('--to-version', help='Target version')
    
    # Statistics and monitoring
    stats_parser = version_subparsers.add_parser('stats', help='Version control statistics')
    
    # Configuration
    config_parser = version_subparsers.add_parser('config', help='Version control configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_command', help='Config commands')
    
    # Show config
    show_config_parser = config_subparsers.add_parser('show', help='Show current configuration')
    
    # Update config
    update_config_parser = config_subparsers.add_parser('update', help='Update configuration')
    update_config_parser.add_argument('--auto-update', choices=['true', 'false'], help='Enable/disable auto updates')
    update_config_parser.add_argument('--maintenance-start', help='Maintenance window start time (HH:MM)')
    update_config_parser.add_argument('--maintenance-end', help='Maintenance window end time (HH:MM)')
    
    # Emergency operations
    emergency_parser = version_subparsers.add_parser('emergency', help='Emergency operations')
    emergency_subparsers = emergency_parser.add_subparsers(dest='emergency_command', help='Emergency commands')
    
    # Stop all updates
    stop_parser = emergency_subparsers.add_parser('stop-updates', help='Emergency stop all updates')
    
    # Emergency rollback
    emergency_rollback_parser = emergency_subparsers.add_parser('rollback-all', help='Emergency rollback all recent updates')
    emergency_rollback_parser.add_argument('--hours', type=int, default=24, help='Hours back to consider')


class VersionControlCLI:
    """Version Control CLI Commands"""
    
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        
    def handle_version_command(self, args):
        """Handle version control commands"""
        try:
            if args.version_command == 'agents':
                return self.handle_agents_command(args)
            elif args.version_command == 'update':
                return self.handle_update_command(args)
            elif args.version_command == 'rollback':
                return self.handle_rollback_command(args)
            elif args.version_command == 'stats':
                return self.show_statistics()
            elif args.version_command == 'config':
                return self.handle_config_command(args)
            elif args.version_command == 'emergency':
                return self.handle_emergency_command(args)
            else:
                print("Unknown version command. Use --help for available commands.")
                return False
        except Exception as e:
            print(f"Error executing version command: {e}")
            return False
    
    def handle_agents_command(self, args):
        """Handle agent version commands"""
        if args.agents_command == 'list':
            return self.list_agent_versions(args.channel, args.platform)
        elif args.agents_command == 'details':
            return self.get_agent_version_details(args.agent_id)
        elif args.agents_command == 'history':
            return self.get_agent_version_history(args.agent_id, args.limit)
        else:
            print("Unknown agents command. Use --help for available commands.")
            return False
    
    def handle_update_command(self, args):
        """Handle update commands"""
        if args.update_command == 'check':
            return self.check_for_updates()
        elif args.update_command == 'available':
            return self.list_available_updates(args.channel)
        elif args.update_command == 'schedule':
            return self.schedule_update(args.agent_id, args.package_id, args.strategy, args.time)
        elif args.update_command == 'active':
            return self.list_active_updates(args.agent, args.status)
        elif args.update_command == 'cancel':
            return self.cancel_update(args.update_id)
        elif args.update_command == 'bulk':
            return self.bulk_update(args.package_id, args.agents, args.all_online, args.channel, args.strategy, args.delay)
        else:
            print("Unknown update command. Use --help for available commands.")
            return False
    
    def handle_rollback_command(self, args):
        """Handle rollback commands"""
        if args.rollback_command == 'initiate':
            return self.initiate_rollback(args.agent_id, args.to_version, args.reason)
        elif args.rollback_command == 'history':
            return self.get_rollback_history(args.agent, args.limit)
        elif args.rollback_command == 'bulk':
            return self.bulk_rollback(args.agents, args.hours, args.to_version)
        else:
            print("Unknown rollback command. Use --help for available commands.")
            return False
    
    def handle_config_command(self, args):
        """Handle configuration commands"""
        if args.config_command == 'show':
            return self.show_config()
        elif args.config_command == 'update':
            return self.update_config(args)
        else:
            print("Unknown config command. Use --help for available commands.")
            return False
    
    def handle_emergency_command(self, args):
        """Handle emergency commands"""
        if args.emergency_command == 'stop-updates':
            return self.emergency_stop_updates()
        elif args.emergency_command == 'rollback-all':
            return self.emergency_rollback_all(args.hours)
        else:
            print("Unknown emergency command. Use --help for available commands.")
            return False
    
    # Agent version commands
    def list_agent_versions(self, channel=None, platform=None):
        """List agent versions"""
        try:
            response = requests.get(f'{self.base_url}/api/v6/version/agents')
            if response.status_code == 200:
                data = response.json()
                agent_versions = data['agent_versions']
                
                # Filter if specified
                if channel or platform:
                    filtered_agents = {}
                    for agent_id, version in agent_versions.items():
                        if channel and version.get('update_channel') != channel:
                            continue
                        if platform and version.get('platform') != platform:
                            continue
                        filtered_agents[agent_id] = version
                    agent_versions = filtered_agents
                
                if not agent_versions:
                    print("No agents found matching criteria.")
                    return True
                
                # Format for display
                table_data = []
                for agent_id, version in agent_versions.items():
                    table_data.append([
                        agent_id,
                        version.get('version', 'Unknown'),
                        version.get('build_number', 'N/A'),
                        version.get('update_channel', 'Unknown'),
                        version.get('platform', 'Unknown'),
                        version.get('last_seen', 'Never')[:19] if version.get('last_seen') else 'Never'
                    ])
                
                headers = ['Agent ID', 'Version', 'Build', 'Channel', 'Platform', 'Last Seen']
                print(tabulate(table_data, headers=headers, tablefmt='grid'))
                print(f"\nTotal agents: {len(agent_versions)}")
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to list agent versions: {e}")
            return False
    
    def get_agent_version_details(self, agent_id):
        """Get detailed version information for an agent"""
        try:
            response = requests.get(f'{self.base_url}/api/v6/version/agents/{agent_id}/version')
            if response.status_code == 200:
                data = response.json()
                version = data['agent_version']
                
                print(f"\n=== Agent Version Details: {agent_id} ===")
                print(f"Version: {version.get('version', 'Unknown')}")
                print(f"Build Number: {version.get('build_number', 'N/A')}")
                print(f"Commit Hash: {version.get('commit_hash', 'N/A')}")
                print(f"Build Date: {version.get('build_date', 'N/A')}")
                print(f"Update Channel: {version.get('update_channel', 'Unknown')}")
                print(f"Platform: {version.get('platform', 'Unknown')}")
                print(f"Architecture: {version.get('architecture', 'Unknown')}")
                print(f"Last Seen: {version.get('last_seen', 'Never')}")
                
                if version.get('capabilities'):
                    print(f"Capabilities: {', '.join(version['capabilities'])}")
                
                if version.get('features'):
                    print(f"Features: {', '.join(version['features'])}")
                
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to get agent version details: {e}")
            return False
    
    def get_agent_version_history(self, agent_id, limit):
        """Get version history for an agent"""
        try:
            response = requests.get(f'{self.base_url}/api/v6/version/agents/{agent_id}/history?limit={limit}')
            if response.status_code == 200:
                data = response.json()
                
                print(f"\n=== Version History: {agent_id} ===")
                
                # Version history
                version_history = data['version_history']
                if version_history:
                    print("\nVersion History:")
                    table_data = []
                    for vh in version_history:
                        table_data.append([
                            vh['version'],
                            vh['build_number'],
                            vh['created_at'][:19],
                            vh['update_channel'],
                            vh['platform']
                        ])
                    headers = ['Version', 'Build', 'Date', 'Channel', 'Platform']
                    print(tabulate(table_data, headers=headers, tablefmt='grid'))
                
                # Update history
                update_history = data['update_history']
                if update_history:
                    print("\nUpdate History:")
                    table_data = []
                    for uh in update_history:
                        table_data.append([
                            uh['update_id'][:12] + '...',
                            uh['from_version'],
                            uh['to_version'],
                            uh['status'],
                            uh['update_type'],
                            uh['completed_at'][:19] if uh['completed_at'] else 'N/A'
                        ])
                    headers = ['Update ID', 'From', 'To', 'Status', 'Type', 'Completed']
                    print(tabulate(table_data, headers=headers, tablefmt='grid'))
                
                # Rollback history
                rollback_history = data['rollback_history']
                if rollback_history:
                    print("\nRollback History:")
                    table_data = []
                    for rh in rollback_history:
                        table_data.append([
                            rh['rollback_id'][:12] + '...',
                            rh['from_version'],
                            rh['to_version'],
                            rh['rollback_type'],
                            rh['status'],
                            rh['completed_at'][:19] if rh['completed_at'] else 'N/A'
                        ])
                    headers = ['Rollback ID', 'From', 'To', 'Type', 'Status', 'Completed']
                    print(tabulate(table_data, headers=headers, tablefmt='grid'))
                
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to get agent version history: {e}")
            return False
    
    # Update commands
    def check_for_updates(self):
        """Check for available updates"""
        try:
            response = requests.post(f'{self.base_url}/api/v6/version/updates/check')
            if response.status_code == 200:
                print("✅ Update check initiated successfully")
                print("ℹ️  Check available updates in a few moments")
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to check for updates: {e}")
            return False
    
    def list_available_updates(self, channel=None):
        """List available updates"""
        try:
            url = f'{self.base_url}/api/v6/version/updates/available'
            if channel:
                url += f'?channel={channel}'
            
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                updates = data['available_updates']
                
                if not updates:
                    print("No available updates found.")
                    return True
                
                table_data = []
                for update in updates:
                    table_data.append([
                        update['package_id'][:16] + '...',
                        update['version'],
                        update['channel'],
                        update['update_type'],
                        '⚠️ CRITICAL' if update['critical'] else 'Normal',
                        f"{update['size_bytes'] / 1024 / 1024:.1f} MB",
                        update['release_date'][:10]
                    ])
                
                headers = ['Package ID', 'Version', 'Channel', 'Type', 'Priority', 'Size', 'Release Date']
                print(tabulate(table_data, headers=headers, tablefmt='grid'))
                print(f"\nTotal available updates: {len(updates)}")
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to list available updates: {e}")
            return False
    
    def schedule_update(self, agent_id, package_id, strategy, scheduled_time):
        """Schedule an agent update"""
        try:
            payload = {
                'agent_id': agent_id,
                'package_id': package_id,
                'strategy': strategy
            }
            
            if scheduled_time:
                payload['scheduled_time'] = scheduled_time
            
            response = requests.post(f'{self.base_url}/api/v6/version/updates/schedule', json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Update scheduled successfully")
                print(f"Update ID: {data['update_id']}")
                print(f"Agent: {data['agent_id']}")
                print(f"Package: {data['package_id']}")
                print(f"Scheduled for: {data['scheduled_time']}")
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to schedule update: {e}")
            return False
    
    def list_active_updates(self, agent_filter=None, status_filter=None):
        """List active updates"""
        try:
            url = f'{self.base_url}/api/v6/version/updates/active'
            params = []
            if agent_filter:
                params.append(f'agent_id={agent_filter}')
            if status_filter:
                params.append(f'status={status_filter}')
            
            if params:
                url += '?' + '&'.join(params)
            
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                updates = data['active_updates']
                
                if not updates:
                    print("No active updates found.")
                    return True
                
                table_data = []
                for update in updates:
                    table_data.append([
                        update['update_id'][:12] + '...',
                        update['agent_id'],
                        update['from_version'],
                        update['to_version'],
                        update['status'],
                        f"{update['progress']}%",
                        update['update_type'],
                        update['scheduled_time'][:19] if update.get('scheduled_time') else 'N/A'
                    ])
                
                headers = ['Update ID', 'Agent', 'From', 'To', 'Status', 'Progress', 'Type', 'Scheduled']
                print(tabulate(table_data, headers=headers, tablefmt='grid'))
                print(f"\nTotal active updates: {len(updates)}")
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to list active updates: {e}")
            return False
    
    def cancel_update(self, update_id):
        """Cancel a scheduled update"""
        try:
            response = requests.post(f'{self.base_url}/api/v6/version/updates/{update_id}/cancel')
            if response.status_code == 200:
                print(f"✅ Update {update_id} cancelled successfully")
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to cancel update: {e}")
            return False
    
    def bulk_update(self, package_id, agents, all_online, channel, strategy, delay):
        """Perform bulk update"""
        try:
            # Build agent list
            if all_online:
                # Get all online agents
                response = requests.get(f'{self.base_url}/api/v3/agents')
                if response.status_code == 200:
                    agents_data = response.json()
                    agent_ids = [agent['id'] for agent in agents_data['agents'] if agent['status'] == 'online']
                    if channel:
                        # Filter by channel - would need to get version info
                        pass
                else:
                    print("Failed to get agent list")
                    return False
            elif agents:
                agent_ids = agents
            else:
                print("No agents specified. Use --agents or --all-online")
                return False
            
            payload = {
                'agent_ids': agent_ids,
                'package_id': package_id,
                'strategy': strategy,
                'delay_minutes': delay
            }
            
            response = requests.post(f'{self.base_url}/api/v6/version/bulk/update', json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Bulk update scheduled successfully")
                print(f"Total agents: {data['total_scheduled']}")
                print(f"Strategy: {strategy}")
                print(f"Delay between updates: {delay} minutes")
                
                if data['scheduled_updates']:
                    print("\nScheduled Updates:")
                    for update in data['scheduled_updates'][:10]:  # Show first 10
                        print(f"  - {update['agent_id']}: {update['scheduled_time']}")
                    
                    if len(data['scheduled_updates']) > 10:
                        print(f"  ... and {len(data['scheduled_updates']) - 10} more")
                
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to perform bulk update: {e}")
            return False
    
    # Rollback commands
    def initiate_rollback(self, agent_id, to_version, reason):
        """Initiate agent rollback"""
        try:
            payload = {
                'agent_id': agent_id,
                'reason': reason
            }
            
            if to_version:
                payload['to_version'] = to_version
            
            response = requests.post(f'{self.base_url}/api/v6/version/rollback/initiate', json=payload)
            if response.status_code == 200:
                print(f"✅ Rollback initiated for agent {agent_id}")
                if to_version:
                    print(f"Target version: {to_version}")
                print(f"Reason: {reason}")
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to initiate rollback: {e}")
            return False
    
    def get_rollback_history(self, agent_filter, limit):
        """Get rollback history"""
        try:
            url = f'{self.base_url}/api/v6/version/rollback/history?limit={limit}'
            if agent_filter:
                url += f'&agent_id={agent_filter}'
            
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                rollbacks = data['rollback_history']
                
                if not rollbacks:
                    print("No rollback history found.")
                    return True
                
                table_data = []
                for rollback in rollbacks:
                    table_data.append([
                        rollback['rollback_id'][:12] + '...',
                        rollback['agent_id'],
                        rollback['from_version'],
                        rollback['to_version'],
                        rollback['rollback_type'],
                        rollback['status'],
                        rollback['completed_at'][:19] if rollback.get('completed_at') else 'N/A'
                    ])
                
                headers = ['Rollback ID', 'Agent', 'From', 'To', 'Type', 'Status', 'Completed']
                print(tabulate(table_data, headers=headers, tablefmt='grid'))
                print(f"\nTotal rollbacks: {len(rollbacks)}")
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to get rollback history: {e}")
            return False
    
    def bulk_rollback(self, agents, hours, to_version):
        """Perform bulk rollback"""
        try:
            payload = {
                'hours': hours
            }
            
            if agents:
                payload['agent_ids'] = agents
            
            if to_version:
                payload['to_version'] = to_version
            
            response = requests.post(f'{self.base_url}/api/v6/version/bulk/rollback', json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Bulk rollback initiated")
                print(f"Total agents: {data['total_agents']}")
                print(f"Successful rollbacks: {data['successful_rollbacks']}")
                print(f"Time window: {hours} hours")
                
                if data['rollback_results']:
                    print("\nRollback Results:")
                    for result in data['rollback_results'][:10]:  # Show first 10
                        status = "✅" if result['success'] else "❌"
                        print(f"  {status} {result['agent_id']}")
                    
                    if len(data['rollback_results']) > 10:
                        print(f"  ... and {len(data['rollback_results']) - 10} more")
                
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to perform bulk rollback: {e}")
            return False
    
    # Statistics and configuration
    def show_statistics(self):
        """Show version control statistics"""
        try:
            response = requests.get(f'{self.base_url}/api/v6/version/statistics')
            if response.status_code == 200:
                data = response.json()
                stats = data['statistics']
                
                print("\n=== Version Control Statistics ===")
                print(f"Total Agents: {stats.get('total_agents', 0)}")
                print(f"Active Updates: {stats.get('active_updates', 0)}")
                print(f"Completed Updates: {stats.get('completed_updates', 0)}")
                print(f"Failed Updates: {stats.get('failed_updates', 0)}")
                print(f"Update Success Rate: {stats.get('update_success_rate', 0) * 100:.1f}%")
                print(f"Available Updates: {stats.get('available_updates', 0)}")
                print(f"Total Rollbacks: {stats.get('total_rollbacks', 0)}")
                print(f"Rollback Success Rate: {stats.get('rollback_success_rate', 0) * 100:.1f}%")
                print(f"Auto Update Enabled: {stats.get('auto_update_enabled', False)}")
                
                if stats.get('version_distribution'):
                    print("\nVersion Distribution:")
                    for version, count in stats['version_distribution'].items():
                        print(f"  {version}: {count} agents")
                
                if stats.get('channel_distribution'):
                    print("\nChannel Distribution:")
                    for channel, count in stats['channel_distribution'].items():
                        print(f"  {channel}: {count} agents")
                
                print(f"\nServices Status:")
                print(f"  Update Checker: {'Running' if stats.get('update_checker_running') else 'Stopped'}")
                print(f"  Rollback Monitor: {'Running' if stats.get('rollback_monitor_running') else 'Stopped'}")
                
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to get statistics: {e}")
            return False
    
    def show_config(self):
        """Show version control configuration"""
        try:
            response = requests.get(f'{self.base_url}/api/v6/version/config')
            if response.status_code == 200:
                data = response.json()
                config = data['configuration']
                
                print("\n=== Version Control Configuration ===")
                print(f"Update Server URL: {config['update_server_url']}")
                print(f"Update Channels: {', '.join(config['update_channels'])}")
                print(f"Auto Update Enabled: {config['auto_update_enabled']}")
                print(f"Maintenance Window: {config['maintenance_window']['start']} - {config['maintenance_window']['end']}")
                
                print("\nUpdate Policies:")
                for policy_type, policy in config['update_policies'].items():
                    print(f"  {policy_type}:")
                    print(f"    Auto Apply: {policy['auto_apply']}")
                    print(f"    Delay Hours: {policy['delay_hours']}")
                
                print("\nServices:")
                for service, status in config['services_running'].items():
                    print(f"  {service}: {'Running' if status else 'Stopped'}")
                
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to get configuration: {e}")
            return False
    
    def update_config(self, args):
        """Update version control configuration"""
        try:
            payload = {}
            
            if args.auto_update:
                payload['auto_update_enabled'] = args.auto_update == 'true'
            
            if args.maintenance_start or args.maintenance_end:
                maintenance_window = {}
                if args.maintenance_start:
                    maintenance_window['start'] = args.maintenance_start
                if args.maintenance_end:
                    maintenance_window['end'] = args.maintenance_end
                payload['maintenance_window'] = maintenance_window
            
            if not payload:
                print("No configuration changes specified.")
                return True
            
            response = requests.put(f'{self.base_url}/api/v6/version/config', json=payload)
            if response.status_code == 200:
                print("✅ Configuration updated successfully")
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to update configuration: {e}")
            return False
    
    # Emergency operations
    def emergency_stop_updates(self):
        """Emergency stop all updates"""
        try:
            confirm = input("⚠️  Are you sure you want to stop ALL active updates? This cannot be undone. [y/N]: ")
            if confirm.lower() != 'y':
                print("Operation cancelled.")
                return True
            
            response = requests.post(f'{self.base_url}/api/v6/version/emergency/stop-all-updates')
            if response.status_code == 200:
                data = response.json()
                print(f"🛑 Emergency stop completed")
                print(f"Stopped updates: {data['total_stopped']}")
                
                if data['stopped_updates']:
                    print("Stopped Update IDs:")
                    for update_id in data['stopped_updates'][:10]:
                        print(f"  - {update_id}")
                    
                    if len(data['stopped_updates']) > 10:
                        print(f"  ... and {len(data['stopped_updates']) - 10} more")
                
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to emergency stop updates: {e}")
            return False
    
    def emergency_rollback_all(self, hours):
        """Emergency rollback all recent updates"""
        try:
            confirm = input(f"⚠️  Are you sure you want to rollback ALL agents updated in the last {hours} hours? [y/N]: ")
            if confirm.lower() != 'y':
                print("Operation cancelled.")
                return True
            
            payload = {'hours': hours}
            
            response = requests.post(f'{self.base_url}/api/v6/version/emergency/rollback-all', json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"🛑 Emergency rollback completed")
                print(f"Total agents: {data['total_agents']}")
                print(f"Successful rollbacks: {data['successful_rollbacks']}")
                print(f"Time window: {hours} hours")
                
                if data['rollback_results']:
                    print("\nRollback Results:")
                    for result in data['rollback_results'][:10]:
                        status = "✅" if result['success'] else "❌"
                        print(f"  {status} {result['agent_id']}")
                    
                    if len(data['rollback_results']) > 10:
                        print(f"  ... and {len(data['rollback_results']) - 10} more")
                
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Failed to emergency rollback: {e}")
            return False


# Example usage in main CLI
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Node Server CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add version control commands
    add_version_commands(subparsers)
    
    args = parser.parse_args()
    
    if args.command == 'version':
        cli = VersionControlCLI()
        success = cli.handle_version_command(args)
        exit(0 if success else 1)
    else:
        parser.print_help()



