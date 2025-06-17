# AI Module Overview

This directory contains the modular AI subsystems used by the Ultimate Agent. Each subpackage focuses on a specific aspect of model management, training and inference.

## Folders

- **`backends/`** – Advanced Ollama integration used for distributed inference and streaming. Provides connection pooling, load balancing and model lifecycle management.
- **`chat/`** – Conversation manager powering the chat interface. Handles sessions, context memory and rate limiting.
- **`distributed/`** – Components for running models across multiple nodes. Includes a distributed attention protocol and a coordinator for model shards.
- **`inference/`** – Minimal inference engine used for tests and as a fallback.
- **`local_models/`** – Local AI manager with hardware detection and quantized model support.
- **`models/`** – Base classes for registering models and interacting with the training engine.
- **`swarm/`** – Lightweight swarm coordinator for aggregating results from multiple nodes.
- **`training/`** – Advanced training engine with support for federated and privacy‑preserving learning.

## Usage

Import the required classes from each package depending on your deployment scenario. For example, the conversation manager relies on an `AIModelManager` instance and can be used from the dashboard API:

```python
from ultimate_agent.ai.chat import ConversationManager
manager = ConversationManager(ai_manager, config_manager)
```

See the main repository [README](../..//README.md) for environment setup and broader system architecture.
