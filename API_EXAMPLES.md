# Lumina AI Agents - API Examples

Complete guide to using the Lumina AI Agents API.

**Base URL:** `http://localhost:8000`

---

## Authentication

Currently no authentication required for local development.

---

## Chat API

### Basic Chat

Send a message and get a response:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "session_id": "user123"
  }'
```

Response:
```json
{
  "status": "success",
  "response": "Hello! I'm doing well...",
  "model": "claude-3-sonnet",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### Chat with Specific Agent

```bash
curl -X POST http://localhost:8000/api/chat/agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "coding",
    "task": {
      "type": "generate",
      "description": "Create a Python function to calculate fibonacci",
      "context": {
        "language": "python"
      }
    },
    "session_id": "user123"
  }'
```

### Get Chat History

```bash
curl http://localhost:8000/api/chat/history/user123?limit=50
```

---

## Agents API

### List All Agents

```bash
curl http://localhost:8000/api/agents
```

Response:
```json
{
  "status": "success",
  "agents": [
    {
      "id": "commander",
      "name": "Commander Agent",
      "description": "Master orchestrator...",
      "status": "idle",
      "reasoning_mode": "strategic"
    },
    {
      "id": "coding",
      "name": "Coding Agent",
      "description": "Expert in software development...",
      "status": "idle",
      "reasoning_mode": "deep"
    }
  ],
  "count": 5
}
```

### Get Agent Details

```bash
curl http://localhost:8000/api/agents/coding
```

### Execute Agent Task

**Coding Agent - Generate Code:**

```bash
curl -X POST http://localhost:8000/api/agents/coding/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "type": "generate",
      "description": "Create a REST API endpoint for user authentication",
      "context": {
        "language": "python",
        "framework": "FastAPI",
        "requirements": ["JWT tokens", "password hashing", "email validation"]
      }
    }
  }'
```

**Research Agent - Conduct Research:**

```bash
curl -X POST http://localhost:8000/api/agents/research/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "type": "research",
      "description": "Research best practices for API rate limiting",
      "context": {
        "topic": "API rate limiting strategies",
        "depth": "comprehensive"
      }
    }
  }'
```

**Security Agent - Security Audit:**

```bash
curl -X POST http://localhost:8000/api/agents/security/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "type": "audit",
      "description": "Audit this authentication code for vulnerabilities",
      "context": {
        "code": "def login(username, password): ...",
        "scope": "full"
      }
    }
  }'
```

**UI/UX Agent - Design Review:**

```bash
curl -X POST http://localhost:8000/api/agents/uiux/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "type": "review",
      "description": "Review the dashboard design for usability",
      "context": {
        "design": "Dashboard with sidebar navigation...",
        "platform": "web"
      }
    }
  }'
```

**Commander Agent - Complex Task:**

```bash
curl -X POST http://localhost:8000/api/agents/commander/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "description": "Build a user authentication system with secure password storage and JWT tokens",
      "context": {
        "requirements": [
          "FastAPI backend",
          "PostgreSQL database",
          "JWT authentication",
          "Password hashing with bcrypt",
          "Email validation"
        ]
      }
    }
  }'
```

### Get Agent Execution History

```bash
curl http://localhost:8000/api/agents/coding/history?limit=10
```

### Get Agent Statistics

```bash
curl http://localhost:8000/api/agents/stats
```

---

## Memory API

### Store Short-Term Memory

```bash
curl -X POST http://localhost:8000/api/memory/short-term \
  -H "Content-Type: application/json" \
  -d '{
    "key": "user_preference",
    "value": {"theme": "dark", "language": "en"},
    "ttl": 3600
  }'
```

### Get Short-Term Memory

```bash
curl http://localhost:8000/api/memory/short-term/user_preference
```

### Store Semantic Memory

```bash
curl -X POST http://localhost:8000/api/memory/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "content": "FastAPI is a modern Python web framework",
    "embedding": [0.1, 0.2, 0.3, ...],
    "metadata": {
      "category": "programming",
      "language": "python"
    }
  }'
```

### Search Semantic Memory

```bash
curl -X POST http://localhost:8000/api/memory/semantic/search \
  -H "Content-Type: application/json" \
  -d '{
    "query_embedding": [0.1, 0.2, 0.3, ...],
    "limit": 5,
    "score_threshold": 0.7
  }'
```

### Store Episodic Memory

```bash
curl -X POST http://localhost:8000/api/memory/episodic \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123",
    "event": {
      "type": "task_completed",
      "description": "Generated authentication code",
      "result": "success"
    }
  }'
```

### Get Episodic Memory

```bash
curl http://localhost:8000/api/memory/episodic/user123?limit=100
```

---

## Python SDK Examples

### Basic Chat

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "messages": [
            {"role": "user", "content": "Hello!"}
        ],
        "session_id": "user123"
    }
)

print(response.json()["response"])
```

### Execute Coding Agent

```python
import requests

response = requests.post(
    "http://localhost:8000/api/agents/coding/execute",
    json={
        "task": {
            "type": "generate",
            "description": "Create a function to validate email addresses",
            "context": {
                "language": "python"
            }
        }
    }
)

result = response.json()
print(result["result"]["code"])
```

---

## JavaScript/TypeScript Examples

### Basic Chat

```typescript
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    messages: [
      { role: 'user', content: 'Hello!' }
    ],
    session_id: 'user123'
  })
});

const data = await response.json();
console.log(data.response);
```

### Execute Agent

```typescript
const response = await fetch('http://localhost:8000/api/agents/coding/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    task: {
      type: 'generate',
      description: 'Create a React component for a login form',
      context: {
        language: 'typescript',
        framework: 'React'
      }
    }
  })
});

const data = await response.json();
console.log(data.result);
```

---

## Common Patterns

### Multi-Step Workflow

```python
# Step 1: Research
research = requests.post(
    "http://localhost:8000/api/agents/research/execute",
    json={
        "task": {
            "type": "research",
            "description": "Research authentication best practices"
        }
    }
).json()

# Step 2: Generate code based on research
code = requests.post(
    "http://localhost:8000/api/agents/coding/execute",
    json={
        "task": {
            "type": "generate",
            "description": "Implement authentication based on research",
            "context": {
                "research_findings": research["result"]
            }
        }
    }
).json()

# Step 3: Security audit
audit = requests.post(
    "http://localhost:8000/api/agents/security/execute",
    json={
        "task": {
            "type": "audit",
            "description": "Audit the authentication code",
            "context": {
                "code": code["result"]["code"]
            }
        }
    }
).json()
```

---

## Error Handling

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "path": "/api/endpoint"
  }
}
```

Common error codes:
- `VALIDATION_ERROR` - Invalid request data
- `AGENT_EXECUTION_ERROR` - Agent failed to execute task
- `MODEL_ROUTER_ERROR` - Model routing failed
- `MEMORY_ERROR` - Memory operation failed
- `INTERNAL_ERROR` - Unexpected server error

---

## Rate Limits

Currently no rate limits for local development.

---

## WebSocket Support

Coming soon for real-time streaming responses.

---

For more information, visit the interactive API docs at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
