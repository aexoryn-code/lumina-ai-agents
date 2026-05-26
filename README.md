# Lumina AI Agents

Enterprise-grade AI Operating System with multi-agent orchestration, adaptive reasoning, and multi-model support.

## Features

- **Multi-Agent Orchestration**: Specialized agents for coding, research, UI/UX, security, and more
- **Adaptive Reasoning**: Dynamic reasoning modes (Fast, Deep, Strategic, Creator, Architect)
- **Multi-Model Router**: Intelligent routing across OpenAI, Claude, Gemini, DeepSeek, and more
- **Persistent Memory**: Short-term, long-term, episodic, and semantic memory systems
- **Token Optimization**: 40-70% token reduction through semantic compression
- **Reflection Engine**: Self-critique and quality verification
- **Real-time Dashboard**: Futuristic UI with live agent monitoring

## Tech Stack

**Backend:**
- FastAPI
- Python 3.12
- PostgreSQL
- Redis
- Qdrant Vector DB
- LangGraph
- LiteLLM

**Frontend:**
- Next.js 15
- React
- TypeScript
- TailwindCSS
- Framer Motion
- Zustand

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.12+

### Installation

1. Clone and setup:
```bash
git clone <repo-url>
cd lumina-agents
cp .env.example .env
```

2. Start services:
```bash
docker-compose up -d
```

3. Install dependencies:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

4. Run migrations:
```bash
cd backend
alembic upgrade head
```

5. Start development:
```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

## Architecture

```
lumina-agents/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Core systems
│   │   ├── agents/   # Agent implementations
│   │   ├── models/   # Database models
│   │   └── schemas/  # Pydantic schemas
├── frontend/         # Next.js frontend
│   ├── app/          # App router
│   ├── components/   # React components
│   └── lib/          # Utilities
└── docker/           # Docker configs
```

## Documentation

See `/docs` for detailed documentation.

## License

MIT
