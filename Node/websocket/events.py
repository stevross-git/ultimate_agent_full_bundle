import sys
import logging
import uuid
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_client import Gauge, Counter, start_http_server
from collections import defaultdict, deque

from config.settings import NODE_ID, NODE_VERSION, NODE_PORT, LOG_DIR, DATABASE_PATH, MANAGER_HOST, MANAGER_PORT
from core.database import EnhancedNodeDatabase
from control.task_manager import TaskControlManager
from control.remote_manager import AdvancedRemoteControlManager
from routes.api_v3 import api_v3
from routes.api_v5_remote import api_v5_remote
from websocket.events import AgentEventNamespace

class EnhancedNodeServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')

        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["1000 per hour", "100 per minute"]
        )

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
            handlers=[
                logging.FileHandler(f"{LOG_DIR}/enhanced_node_server_advanced.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("EnhancedNodeServerAdvanced")

        self.db = EnhancedNodeDatabase(DATABASE_PATH)
        self.agents = {}
        self.agent_status = {}
        self.registered_with_manager = False
        self.running = False

        self.task_control = TaskControlManager(self)
        self.advanced_remote_control = AdvancedRemoteControlManager(self)

        self.performance_history = defaultdict(lambda: deque(maxlen=100))
        self.task_queue = deque()

        self.metrics = {
            'agents_total': Gauge('node_agents_total', 'Total agents connected'),
            'agents_online': Gauge('node_agents_online', 'Online agents'),
            'tasks_running': Gauge('node_tasks_running', 'Tasks currently running'),
            'tasks_completed_total': Counter('node_tasks_completed_total', 'Total tasks completed'),
            'ai_models_total': Gauge('node_ai_models_total', 'Total AI models loaded'),
            'blockchain_balance_total': Gauge('node_blockchain_balance_total', 'Total blockchain balance'),
            'avg_efficiency': Gauge('node_avg_efficiency', 'Average agent efficiency'),
            'commands_total': Counter('node_commands_total', 'Total remote commands sent'),
            'configurations_deployed': Counter('node_configurations_deployed', 'Total configurations deployed'),
            'bulk_operations_total': Counter('node_bulk_operations_total', 'Total bulk operations'),
            'health_checks_total': Counter('node_health_checks_total', 'Total health checks'),
            'scripts_deployed_total': Counter('node_scripts_deployed_total', 'Total scripts deployed')
        }

        self.manager_url = f"http://{MANAGER_HOST}:{MANAGER_PORT}"

        self._register_routes()
        self._register_socketio_namespaces()

        self.logger.info(f"Enhanced Node Server {NODE_ID} v{NODE_VERSION} initialized")
        self.logger.info("✅ Modular architecture enabled")

        self._start_metrics_server()

    def _register_routes(self):
        self.app.register_blueprint(api_v3)
        self.app.register_blueprint(api_v5_remote)

    def _register_socketio_namespaces(self):
        self.socketio.on_namespace(AgentEventNamespace('/agent'))

    def _start_metrics_server(self):
        try:
            start_http_server(8091)
            self.logger.info("Prometheus metrics server started on :8091")
        except Exception as e:
            self.logger.warning(f"Metrics server failed: {e}")
