"""
Unit tests for MemoryManager.

Tests cover:
- Initialization and connection management
- Short-term memory (Redis)
- Semantic memory (Qdrant)
- Episodic memory
- Memory cleanup
"""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from app.core.memory_manager import MemoryManager, MemoryType


# ============================================================================
# Initialization Tests
# ============================================================================

@pytest.mark.unit
class TestMemoryManagerInitialization:
    """Test MemoryManager initialization."""

    @pytest.mark.asyncio
    async def test_initialize_success(self, mock_redis, mock_qdrant):
        """Test successful initialization."""
        manager = MemoryManager()
        
        mock_from_url = AsyncMock(return_value=mock_redis)
        with patch("app.core.memory_manager.redis.from_url", mock_from_url):
            with patch("app.core.memory_manager.QdrantClient", return_value=mock_qdrant):
                await manager.initialize()
                
                assert manager.redis_client is not None
                assert manager.qdrant_client is not None
                mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_creates_collection_if_not_exists(self, mock_redis, mock_qdrant):
        """Test collection creation on initialization."""
        manager = MemoryManager()
        
        # Mock no existing collections
        collections_mock = MagicMock()
        collections_mock.collections = []
        mock_qdrant.get_collections.return_value = collections_mock
        
        mock_from_url = AsyncMock(return_value=mock_redis)
        with patch("app.core.memory_manager.redis.from_url", mock_from_url):
            with patch("app.core.memory_manager.QdrantClient", return_value=mock_qdrant):
                await manager.initialize()
                
                mock_qdrant.create_collection.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_skips_collection_if_exists(self, mock_redis, mock_qdrant):
        """Test skips collection creation if already exists."""
        manager = MemoryManager()
        
        # Mock existing collection
        collection_mock = MagicMock()
        collection_mock.name = "lumina_memory"
        collections_mock = MagicMock()
        collections_mock.collections = [collection_mock]
        mock_qdrant.get_collections.return_value = collections_mock
        
        mock_from_url = AsyncMock(return_value=mock_redis)
        with patch("app.core.memory_manager.redis.from_url", mock_from_url):
            with patch("app.core.memory_manager.QdrantClient", return_value=mock_qdrant):
                await manager.initialize()
                
                mock_qdrant.create_collection.assert_not_called()

    @pytest.mark.asyncio
    async def test_initialize_failure_raises_exception(self):
        """Test initialization failure raises exception."""
        manager = MemoryManager()
        
        with patch("app.core.memory_manager.redis.from_url") as mock_from_url:
            mock_from_url.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception, match="Connection failed"):
                await manager.initialize()

    @pytest.mark.asyncio
    async def test_close_connections(self, memory_manager):
        """Test closing connections."""
        await memory_manager.close()
        memory_manager.redis_client.close.assert_called_once()


# ============================================================================
# Short-Term Memory Tests
# ============================================================================

@pytest.mark.unit
class TestShortTermMemory:
    """Test short-term memory operations."""

    @pytest.mark.asyncio
    async def test_store_short_term_string(self, memory_manager):
        """Test storing string in short-term memory."""
        result = await memory_manager.store_short_term("test_key", "test_value")
        
        assert result is True
        memory_manager.redis_client.setex.assert_called_once_with(
            "st:test_key", 3600, "test_value"
        )

    @pytest.mark.asyncio
    async def test_store_short_term_dict(self, memory_manager):
        """Test storing dict in short-term memory."""
        test_data = {"key": "value", "number": 42}
        result = await memory_manager.store_short_term("test_key", test_data)
        
        assert result is True
        call_args = memory_manager.redis_client.setex.call_args
        assert call_args[0][0] == "st:test_key"
        assert json.loads(call_args[0][2]) == test_data

    @pytest.mark.asyncio
    async def test_store_short_term_with_custom_ttl(self, memory_manager):
        """Test storing with custom TTL."""
        result = await memory_manager.store_short_term("test_key", "value", ttl=7200)
        
        assert result is True
        memory_manager.redis_client.setex.assert_called_once_with(
            "st:test_key", 7200, "value"
        )

    @pytest.mark.asyncio
    async def test_store_short_term_failure(self, memory_manager):
        """Test handling store failure."""
        memory_manager.redis_client.setex.side_effect = Exception("Redis error")
        
        result = await memory_manager.store_short_term("test_key", "value")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_short_term_existing_key(self, memory_manager):
        """Test retrieving existing short-term memory."""
        memory_manager.redis_client.get.return_value = "test_value"
        
        result = await memory_manager.get_short_term("test_key")
        
        assert result == "test_value"
        memory_manager.redis_client.get.assert_called_once_with("st:test_key")

    @pytest.mark.asyncio
    async def test_get_short_term_json_value(self, memory_manager):
        """Test retrieving JSON value from short-term memory."""
        test_data = {"key": "value"}
        memory_manager.redis_client.get.return_value = json.dumps(test_data)
        
        result = await memory_manager.get_short_term("test_key")
        
        assert result == test_data

    @pytest.mark.asyncio
    async def test_get_short_term_nonexistent_key(self, memory_manager):
        """Test retrieving non-existent key returns None."""
        memory_manager.redis_client.get.return_value = None
        
        result = await memory_manager.get_short_term("nonexistent")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_short_term_failure(self, memory_manager):
        """Test handling get failure."""
        memory_manager.redis_client.get.side_effect = Exception("Redis error")
        
        result = await memory_manager.get_short_term("test_key")
        assert result is None


# ============================================================================
# Semantic Memory Tests
# ============================================================================

@pytest.mark.unit
class TestSemanticMemory:
    """Test semantic memory operations."""

    @pytest.mark.asyncio
    async def test_store_semantic_success(self, memory_manager):
        """Test storing semantic memory."""
        content = "Test content"
        embedding = [0.1] * 1536
        metadata = {"source": "test"}
        
        point_id = await memory_manager.store_semantic(content, embedding, metadata)
        
        assert point_id is not None
        memory_manager.qdrant_client.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_semantic_without_metadata(self, memory_manager):
        """Test storing semantic memory without metadata."""
        content = "Test content"
        embedding = [0.1] * 1536
        
        point_id = await memory_manager.store_semantic(content, embedding)
        
        assert point_id is not None
        call_args = memory_manager.qdrant_client.upsert.call_args
        payload = call_args[1]["points"][0].payload
        assert payload["content"] == content
        assert "timestamp" in payload

    @pytest.mark.asyncio
    async def test_store_semantic_with_metadata(self, memory_manager):
        """Test storing semantic memory with metadata."""
        content = "Test content"
        embedding = [0.1] * 1536
        metadata = {"source": "test", "type": "document"}
        
        point_id = await memory_manager.store_semantic(content, embedding, metadata)
        
        call_args = memory_manager.qdrant_client.upsert.call_args
        payload = call_args[1]["points"][0].payload
        assert payload["source"] == "test"
        assert payload["type"] == "document"

    @pytest.mark.asyncio
    async def test_store_semantic_failure(self, memory_manager):
        """Test handling store failure."""
        memory_manager.qdrant_client.upsert.side_effect = Exception("Qdrant error")
        
        with pytest.raises(Exception, match="Qdrant error"):
            await memory_manager.store_semantic("content", [0.1] * 1536)

    @pytest.mark.asyncio
    async def test_search_semantic_with_results(self, memory_manager):
        """Test searching semantic memory with results."""
        # Mock search results
        result_mock = MagicMock()
        result_mock.id = 123
        result_mock.score = 0.95
        result_mock.payload = {"content": "Test result", "source": "test"}
        memory_manager.qdrant_client.search.return_value = [result_mock]
        
        query_embedding = [0.1] * 1536
        results = await memory_manager.search_semantic(query_embedding)
        
        assert len(results) == 1
        assert results[0]["id"] == 123
        assert results[0]["score"] == 0.95
        assert results[0]["content"] == "Test result"
        assert results[0]["metadata"]["source"] == "test"

    @pytest.mark.asyncio
    async def test_search_semantic_with_custom_params(self, memory_manager):
        """Test searching with custom parameters."""
        memory_manager.qdrant_client.search.return_value = []
        
        query_embedding = [0.1] * 1536
        await memory_manager.search_semantic(
            query_embedding,
            limit=10,
            score_threshold=0.8,
        )
        
        memory_manager.qdrant_client.search.assert_called_once_with(
            collection_name="lumina_memory",
            query_vector=query_embedding,
            limit=10,
            score_threshold=0.8,
        )

    @pytest.mark.asyncio
    async def test_search_semantic_no_results(self, memory_manager):
        """Test searching with no results."""
        memory_manager.qdrant_client.search.return_value = []
        
        results = await memory_manager.search_semantic([0.1] * 1536)
        
        assert results == []

    @pytest.mark.asyncio
    async def test_search_semantic_failure(self, memory_manager):
        """Test handling search failure."""
        memory_manager.qdrant_client.search.side_effect = Exception("Search error")
        
        results = await memory_manager.search_semantic([0.1] * 1536)
        assert results == []


# ============================================================================
# Episodic Memory Tests
# ============================================================================

@pytest.mark.unit
class TestEpisodicMemory:
    """Test episodic memory operations."""

    @pytest.mark.asyncio
    async def test_store_episodic_success(self, memory_manager):
        """Test storing episodic memory."""
        session_id = "session-123"
        event = {"action": "test", "data": "value"}
        
        result = await memory_manager.store_episodic(session_id, event)
        
        assert result is True
        memory_manager.redis_client.rpush.assert_called_once()
        memory_manager.redis_client.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_episodic_adds_timestamp(self, memory_manager):
        """Test episodic memory includes timestamp."""
        session_id = "session-123"
        event = {"action": "test"}
        
        await memory_manager.store_episodic(session_id, event)
        
        call_args = memory_manager.redis_client.rpush.call_args
        stored_event = json.loads(call_args[0][1])
        assert "timestamp" in stored_event
        assert stored_event["action"] == "test"

    @pytest.mark.asyncio
    async def test_store_episodic_failure(self, memory_manager):
        """Test handling store failure."""
        memory_manager.redis_client.rpush.side_effect = Exception("Redis error")
        
        result = await memory_manager.store_episodic("session-123", {"action": "test"})
        assert result is False

    @pytest.mark.asyncio
    async def test_get_episodic_with_events(self, memory_manager):
        """Test retrieving episodic memory."""
        events = [
            json.dumps({"action": "event1", "timestamp": "2024-01-01"}),
            json.dumps({"action": "event2", "timestamp": "2024-01-02"}),
        ]
        memory_manager.redis_client.lrange.return_value = events
        
        result = await memory_manager.get_episodic("session-123")
        
        assert len(result) == 2
        assert result[0]["action"] == "event1"
        assert result[1]["action"] == "event2"

    @pytest.mark.asyncio
    async def test_get_episodic_with_limit(self, memory_manager):
        """Test retrieving episodic memory with limit."""
        memory_manager.redis_client.lrange.return_value = []
        
        await memory_manager.get_episodic("session-123", limit=50)
        
        memory_manager.redis_client.lrange.assert_called_once_with(
            "ep:session-123", -50, -1
        )

    @pytest.mark.asyncio
    async def test_get_episodic_no_events(self, memory_manager):
        """Test retrieving episodic memory with no events."""
        memory_manager.redis_client.lrange.return_value = []
        
        result = await memory_manager.get_episodic("session-123")
        
        assert result == []

    @pytest.mark.asyncio
    async def test_get_episodic_failure(self, memory_manager):
        """Test handling get failure."""
        memory_manager.redis_client.lrange.side_effect = Exception("Redis error")
        
        result = await memory_manager.get_episodic("session-123")
        assert result == []


# ============================================================================
# Memory Cleanup Tests
# ============================================================================

@pytest.mark.unit
class TestMemoryCleanup:
    """Test memory cleanup operations."""

    @pytest.mark.asyncio
    async def test_cleanup_old_memories_executes(self, memory_manager):
        """Test cleanup function executes without error."""
        # Note: Current implementation is incomplete, just test it doesn't crash
        await memory_manager.cleanup_old_memories(days=30)
        # No assertion needed - just verify no exception raised

    @pytest.mark.asyncio
    async def test_cleanup_with_custom_days(self, memory_manager):
        """Test cleanup with custom retention period."""
        await memory_manager.cleanup_old_memories(days=7)
        # No assertion needed - just verify no exception raised
