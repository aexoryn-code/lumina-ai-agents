# 🪐 Lumina AI Agents

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Next.js Version](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)

An enterprise-grade, distributed AI Operating System powered by multi-agent orchestration, adaptive reasoning pathways, and an intelligent multi-model routing engine.

---

## 🌟 Key Capabilities

### 🤖 Multi-Agent Orchestration
Deploys specialized, autonomous agents tailored for complex domains including software engineering, deep research, dynamic UI/UX generation, and comprehensive security auditing.

### 🧠 Adaptive Reasoning Paths
Dynamically scales reasoning budgets and cognitive patterns using cognitive profiles: **Fast**, **Deep**, **Strategic**, **Creator**, and **Architect**.

### 🔌 Multi-Model Routing Engine
Intelligently routes prompts to the optimal LLM (OpenAI, Claude, Gemini, DeepSeek) based on task complexity, cost constraints, and performance profiles.

### 💾 Unified Memory Architecture
Equipped with a tiered memory system combining short-term working memory, episodic history recall, long-term semantic context, and cross-session vector-based persistence.

### ⚡ Token Optimization & Compression
Achieves a **40-70% reduction in token consumption** via intelligent semantic compression, prompt caching, and contextual pruning.

### 🔍 Self-Correction & Reflection Engine
Integrates autonomous critique-and-refinement loops to verify generated code, factual accuracy, and alignment with target constraints before final output.

### 📊 Real-Time Operations Dashboard
Provides a state-of-the-art telemetry interface to monitor agent status, real-time thought chains, memory usage, and token performance metrics.

---

## 🛠️ System Architecture

### Repository Structure

```
lumina-agents/
├── backend/          # FastAPI High-Performance Backend
│   ├── app/
│   │   ├── api/      # REST API & WebSocket Endpoints
│   │   ├── core/     # Memory Systems, Router & Engine Core
│   │   ├── agents/   # Autonomous Agent Definitions
│   │   ├── models/   # SQLAlchemy & Database Schema Models
│   │   └── schemas/  # Pydantic Request/Response Validators
├── frontend/         # Next.js 15 Telemetry & Control Dashboard
│   ├── app/          # App Router & Server Components
│   ├── components/   # Modular React Components & Motion UI
│   └── lib/          # State Management (Zustand) & API Clients
└── docker/           # Production-ready Docker orchestrations
```

---

## 🚀 Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Core** | FastAPI • Python 3.12+ • LangGraph • LiteLLM |
| **Data Stores** | PostgreSQL • Redis (Caching & Sessions) • Qdrant (Vector DB) |
| **Frontend UI** | Next.js 15 (React) • TypeScript • TailwindCSS • Framer Motion • Zustand |
| **DevOps** | Docker • Docker Compose • Alembic (Migrations) |

---

## 🏁 Quick Start Guide

### Prerequisites

Ensure you have the following system dependencies installed:
- [Docker & Docker Compose](https://www.docker.com/products/docker-desktop/)
- [Node.js v20+](https://nodejs.org/)
- [Python v3.12+](https://www.python.org/)

### Setup and Installation

Follow these steps to spin up your local development environment:

#### 1. Repository Setup & Environment
Clone the repository and prepare the configuration files:
```bash
git clone https://github.com/aexoryn-code/lumina-ai-agents.git
cd lumina-agents
cp .env.example .env
```

#### 2. Launch Infrastructure Services
Start the persistent storage, database, vector index, and caching servers:
```bash
docker-compose up -d
```

#### 3. Install Project Dependencies
Initialize packages for both the backend engine and the telemetry dashboard:

**Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend Setup:**
```bash
cd ../frontend
npm install
```

#### 4. Run Relational Migrations
Upgrade the database schema to the latest head:
```bash
cd ../backend
alembic upgrade head
```

#### 5. Run Development Servers
Launch both services to start interacting with Lumina AI:


**Backend Service:**
```bash
cd backend
uvicorn app.main:app --reload
```
*The backend API will be available at [http://localhost:8000](http://localhost:8000)*

**Frontend Dashboard:**
```bash
cd frontend
npm run dev
```
*The frontend dashboard will be available at [http://localhost:3000](http://localhost:3000)*

---

## 📖 Additional Resources

- **API Examples**: Refer to [API_EXAMPLES.md](file:///e:/Lumina%20Agents/API_EXAMPLES.md) for detailed payload formats and integration patterns.
- **Deployment Guide**: Read [DEPLOYMENT.md](file:///e:/Lumina%20Agents/DEPLOYMENT.md) for production hosting and orchestration patterns.
- **System Documentation**: Explore `/docs` for detailed guides on creating custom agents and tailoring memory adapters.

---

## 🛡️ License

This project is licensed under the [MIT License](file:///e:/Lumina%20Agents/LICENSE).
