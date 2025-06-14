# Ultimate Agent API Documentation

This project currently exposes only a minimal HTTP API implemented with
FastAPI. Every endpoint expects a JSON Web Token (JWT) in the
`Authorization` header.

**Base URL**: `http://localhost:8080`

## Authentication

- `POST /auth/token` – issue a JWT for an agent
- `POST /auth/revoke` – revoke a previously issued token

## Task Interface

- `POST /task` – submit a task to the agent
- `POST /command` – send a control command

The extensive API outlined in previous revisions of this document is not
implemented here. Only the endpoints listed above are available.

