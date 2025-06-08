from flask import request, jsonify
from flask import Blueprint

api_v3 = Blueprint('api_v3', __name__)

@api_v3.route('/api/v3/agents/register', methods=['POST'])
@api_v3.route('/api/v4/agents/register', methods=['POST'])
@api_v3.route('/api/agents/register', methods=['POST'])
def register_agent():
    data = request.get_json()
    return jsonify({
        "status": "ok",
        "message": "Agent registered (placeholder response)"
    })

@api_v3.route('/api/v3/agents/heartbeat', methods=['POST'])
@api_v3.route('/api/v4/agents/heartbeat', methods=['POST'])
@api_v3.route('/api/agents/heartbeat', methods=['POST'])
def agent_heartbeat():
    data = request.get_json()
    return jsonify({
        "status": "ok",
        "message": "Heartbeat received (placeholder response)"
    })
