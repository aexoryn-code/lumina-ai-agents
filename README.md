# Lumina AI Agents

<div align="center">

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-%2300C7B7.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**An enterprise-grade AI operating system with multi-agent orchestration, intelligent model routing, and persistent memory.**

[Quick Start](#quick-start) •
[Architecture](#architecture) •
[Features](#features) •
[Deployment](#deployment) •
[Contributing](#contributing)

</div>

---

## Overview

Lumina AI Agents is a production-ready platform for building, deploying, and managing autonomous AI agents. It intelligently routes tasks across multiple LLM providers (OpenAI, Anthropic, Google, DeepSeek, Mistral, Groq), maintains persistent memory across sessions, and provides real-time insights through a modern web interface.

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for database services)
- API keys from at least one LLM provider

### Setup

**1. Clone the repository**

```bash
git clone https://github.com/aexoryn-code/lumina-ai-agents.git
cd lumina-ai-agents
```

**2. Start database services**

```bash
docker compose up -d
```

**3. Configure environment**

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

**4. Set up backend**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**5. Set up frontend**

```bash
cd frontend
npm install
npm run dev
```

Visit **http://localhost:3000** to access the dashboard.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Next.js)                      │
│   ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│   │ Dashboard │  │   Chat   │  │  Analytics & Monitoring │
│   └────┬─────┘  └────┬─────┘  └──────────┬───────────┘   │
│        └──────────────┼───────────────────┘               │
└───────────────────────┼───────────────────────────────────┘
                        │ WebSocket / REST
┌───────────────────────┼───────────────────────────────────┐
│            Backend (FastAPI / Python)                      │
│   ┌───────────────────┼───────────────────────────────┐   │
│   │           API Gateway & Model Router                │   │
│   │   ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │   │
│   │   │ Chat API │ │ Agent API│ │  WebSocket Hub    │  │   │
│   │   └────┬─────┘ └────┬─────┘ └────────┬─────────┘  │   │
│   └────────┼─────────────┼────────────────┼────────────┘   │
│            │             │                │                 │
│   ┌────────▼─────────────▼────────────────▼────────────┐   │
│   │               Core Orchestration                    │   │
│   │   ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │   │
│   │   │  Agents   │ │  Memory   │ │  Task Router     │   │   │
│   │   └──────────┘ └──────────┘ └──────────────────┘   │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────┼───────────────────────────────────┐
│                Data Layer                                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────────────┐       │
│   │PostgreSQL│  │  Redis   │  │  Qdrant (Vector)  │       │
│   └──────────┘  └──────────┘  └──────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API Gateway** | FastAPI | REST & WebSocket endpoints |
| **Model Router** | LiteLLM | Intelligent LLM provider routing |
| **Memory Manager** | Redis + Qdrant | Short-term, episodic & semantic memory |
| **Agent System** | LangGraph | Multi-agent orchestration |
| **Frontend** | Next.js + Tailwind | Real-time dashboard & chat |

---

## Features

### 🤖 Multi-Model Orchestration
- Intelligent task routing across 6+ LLM providers
- Automatic fallback on provider failures
- Cost-optimized model selection
- Usage tracking and analytics

### 🧠 Persistent Memory
- **Short-term memory**: Redis-based caching (TTL configurable)
- **Episodic memory**: Session-based event history (7-day retention)
- **Semantic memory**: Vector-based similarity search via Qdrant
- Automatic cleanup of stale memories

### 🔒 Enterprise Security
- Rate limiting on all API endpoints
- Pydantic input validation at every boundary
- Secret-free configuration via environment variables
- Structured logging (no PII in logs)

### ⚡ Real-Time Communication
- WebSocket-based streaming responses
- Live token usage metrics
- Agent execution progress updates
- Performance dashboards

---

## API Reference

### Chat

```bash
POST /api/chat/send
Content-Type: application/json
Authorization: Bearer <your-api-key>

{
  "message": "Write a Python function to sort a list",
  "model": "auto",
  "task_type": "coding"
}
```

### Agents

```bash
POST /api/agents/execute
Content-Type: application/json

{
  "task": "Research latest AI trends",
  "agent_type": "research",
  "max_steps": 10
}
```

### Memory

```bash
POST /api/memory/semantic
Content-Type: application/json

{
  "content": "Important project decision",
  "metadata": {"project": "alpha", "priority": "high"}
}
```

> Full API documentation with examples is available in [API_EXAMPLES.md](API_EXAMPLES.md).

---

## Deployment

### Docker (Recommended)

```bash
docker compose up --build -d
```

### Production Checklist

- [ ] Generate a strong `SECRET_KEY`: `openssl rand -hex 32`
- [ ] Set strong database passwords in `.env`
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS (reverse proxy with Nginx/Caddy)
- [ ] Set up monitoring & alerting
- [ ] Configure rate limits for your traffic volume

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## Testing

```bash
# Backend tests
cd backend
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm run lint
```

---

## Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) before submitting a pull request.

1. Fork the repository
2. Create your feature branch: `git checkout -b feat/my-feature`
3. Commit your changes: `git commit -m 'feat: add new feature'`
4. Push to the branch: `git push origin feat/my-feature`
5. Open a pull request

---

## License

This project is open source under the [MIT License](LICENSE).

---

<div align="center">
Built with ❤️ for the open source community.
</div>
