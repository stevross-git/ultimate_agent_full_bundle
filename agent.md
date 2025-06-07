# People AI Network (PAIN) Agent

The PAIN agent provides decentralized computation for the People AI Network. It runs as a containerized service and communicates with the network manager via Redis Streams and secure WebSockets.

## Features
- **Distributed Task Execution**: Asynchronous job handling using `asyncio`.
- **Blockchain Incentives**: Earn ERC‑20 tokens for contributing compute resources.
- **Autonomous Governance**: Agents participate in consensus and network upgrades.
- **Secure Communication**: JWT authentication and optional Fernet encryption for agent keys.

## Core Components
1. **Agent Service** – Fetches tasks from Redis queues, executes AI workloads and publishes results.
2. **Manager** – Issues tokens, monitors health and coordinates the network.
3. **API Layer** – Submits tasks and provides system endpoints.

## Supported AI Frameworks
- Federated learning
- Transformer models
- CNN/RNN training
- Custom inference engines

## Running the Agent
```bash
# Install dependencies
pip install -r requirements.txt

# Start the agent
python -m ultimate_agent.main
```

## Repository Structure
See `README.md` for the full modular layout. Key directories include:
- `core/` – Main orchestrator and dependency container
- `ai/` – Training and inference modules
- `blockchain/` – Wallet and contract management
- `tasks/` – Task scheduler and execution logic
- `network/` – Communication protocols

## Roadmap Highlights
- Initial modular agent deployment
- Incentive rewards via smart contracts
- Hosting federated AI models
- Full AI swarm governance
