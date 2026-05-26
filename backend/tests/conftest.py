"""
Pytest configuration and shared fixtures for Lumina Agents tests.

This module provides reusable fixtures for testing all components of the system.
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.config import Settings, get_settings
from app.core.model_router import ModelRouter, TaskType
from app.core.memory_manager import MemoryManager
from app.core.agent_base import BaseAgent, ReasoningMode


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def test_settings() -> Settings:
    """Provide test settings with safe defaults."""
    return Settings(
        APP_ENV="testing",
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5432,
        POSTGRES_DB="lumina_test",
        POSTGRES_USER="test_user",
        POSTGRES_PASSWORD="test_pass",
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
        QDRANT_HOST="localhost",
        QDRANT_PORT=6333,
        OPENAI_API_KEY="test-key",
        ANTHROPIC_API_KEY="test-key",
        GOOGLE_API_KEY="test-key",
        DEEPSEEK_API_KEY="test-key",
    )


@pytest.fixture
def override_settings(test_settings):
    """Override app settings with test settings."""
    app.dependency_overrides[get_settings] = lambda: test_settings
    yield test_settings
    app.dependency_overrides.clear()


# ============================================================================
# HTTP Client Fixtures
# ============================================================================

@pytest.fixture
def client(override_settings) -> Generator[TestClient, None, None]:
    """Provide synchronous test client for FastAPI."""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def async_client(override_settings) -> AsyncGenerator[AsyncClient, None]:
    """Provide async test client for FastAPI."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ============================================================================
# Redis Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_redis():
    """Provide mocked Redis client."""
    redis_mock = AsyncMock()
    redis_mock.ping = AsyncMock(return_value=True)
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.setex = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.lrange = AsyncMock(return_value=[])
    redis_mock.rpush = AsyncMock(return_value=1)
    redis_mock.expire = AsyncMock(return_value=True)
    redis_mock.close = AsyncMock()
    return redis_mock


# ============================================================================
# Qdrant Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_qdrant():
    """Provide mocked Qdrant client."""
    qdrant_mock = MagicMock()
    
    # Mock collections
    collections_mock = MagicMock()
    collections_mock.collections = []
    qdrant_mock.get_collections.return_value = collections_mock
    
    # Mock operations
    qdrant_mock.create_collection.return_value = None
    qdrant_mock.upsert.return_value = None
    qdrant_mock.search.return_value = []
    
    return qdrant_mock


# ============================================================================
# Model Router Fixtures
# ============================================================================

@pytest.fixture
def model_router():
    """Provide ModelRouter instance."""
    return ModelRouter()


@pytest.fixture
def mock_model_router():
    """Provide mocked ModelRouter."""
    router_mock = AsyncMock(spec=ModelRouter)
    router_mock.select_model.return_value = "gpt-4o"
    router_mock.complete.return_value = {
        "model": "gpt-4o",
        "content": "Test response",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
        "finish_reason": "stop",
    }
    router_mock.get_stats.return_value = {
        "total_requests": 0,
        "total_cost": 0.0,
        "by_model": {},
    }
    return router_mock


# ============================================================================
# Memory Manager Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def memory_manager(mock_redis, mock_qdrant):
    """Provide MemoryManager instance with mocked dependencies."""
    manager = MemoryManager()
    manager.redis_client = mock_redis
    manager.qdrant_client = mock_qdrant
    return manager


@pytest.fixture
def mock_memory_manager():
    """Provide mocked MemoryManager."""
    manager_mock = AsyncMock(spec=MemoryManager)
    manager_mock.initialize.return_value = None
    manager_mock.store_short_term.return_value = True
    manager_mock.get_short_term.return_value = None
    manager_mock.store_semantic.return_value = "test-id"
    manager_mock.search_semantic.return_value = []
    manager_mock.store_episodic.return_value = True
    manager_mock.get_episodic.return_value = []
    manager_mock.close.return_value = None
    return manager_mock


# ============================================================================
# Agent Fixtures
# ============================================================================

class TestAgent(BaseAgent):
    """Concrete test agent implementation."""
    
    async def execute(self, task):
        """Execute test task."""
        return {"status": "completed", "result": "test result"}


@pytest_asyncio.fixture
async def test_agent(mock_model_router, mock_memory_manager):
    """Provide test agent instance."""
    agent = TestAgent(
        agent_id="test-agent-001",
        name="Test Agent",
        description="Agent for testing",
        model_router=mock_model_router,
        memory_manager=mock_memory_manager,
        reasoning_mode=ReasoningMode.FAST,
    )
    return agent


# ============================================================================
# LiteLLM Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_litellm_completion():
    """Mock LiteLLM completion response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test AI response"
    mock_response.choices[0].finish_reason = "stop"
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    mock_response.usage.total_tokens = 30
    return mock_response


@pytest.fixture
def patch_litellm(mock_litellm_completion):
    """Patch LiteLLM acompletion function."""
    with patch("app.core.model_router.acompletion", return_value=mock_litellm_completion):
        yield


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def db_session():
    """Provide database session for testing."""
    # TODO: Implement actual database session when needed
    # For now, return a mock
    session_mock = AsyncMock()
    yield session_mock
    await session_mock.close()


# ============================================================================
# Helper Functions
# ============================================================================

def assert_valid_response(response, expected_status=200):
    """Assert response is valid with expected status."""
    assert response.status_code == expected_status
    return response.json()


def create_test_messages(content: str):
    """Create test message format for LLM."""
    return [
        {"role": "system", "content": "You are a test assistant."},
        {"role": "user", "content": content},
    ]


# ============================================================================
# Event Loop Configuration
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
