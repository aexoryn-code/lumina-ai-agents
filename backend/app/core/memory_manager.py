from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timedelta
import json
import structlog
import redis.asyncio as redis
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


class MemoryType(str, Enum):
    """Memory types"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class MemoryManager:
    """Persistent memory management system"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.qdrant_client: Optional[QdrantClient] = None
        self.collection_name = "lumina_memory"

    async def initialize(self):
        """Initialize memory connections"""
        try:
            # Initialize Redis with connection pooling
            self.redis_client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,  # Connection pool size
            )
            await self.redis_client.ping()
            logger.info("Redis connected with connection pooling")

            self.qdrant_client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
            )

            collections = self.qdrant_client.get_collections().collections
            if not any(c.name == self.collection_name for c in collections):
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                )
                logger.info("Qdrant collection created", collection=self.collection_name)

        except Exception as e:
            logger.error("Memory initialization failed", error=str(e))
            raise

    async def store_short_term(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
    ) -> bool:
        """Store short-term memory in Redis"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            await self.redis_client.setex(f"st:{key}", ttl, value)
            logger.debug("Short-term memory stored", key=key)
            return True
        except Exception as e:
            logger.error("Failed to store short-term memory", key=key, error=str(e))
            return False

    async def get_short_term(self, key: str) -> Optional[Any]:
        """Retrieve short-term memory"""
        try:
            value = await self.redis_client.get(f"st:{key}")
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error("Failed to get short-term memory", key=key, error=str(e))
            return None

    async def store_semantic(
        self,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store semantic memory in Qdrant"""
        try:
            point_id = hash(content + str(datetime.utcnow()))
            point = PointStruct(
                id=abs(point_id),
                vector=embedding,
                payload={
                    "content": content,
                    "timestamp": datetime.utcnow().isoformat(),
                    **(metadata or {}),
                },
            )
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )
            logger.debug("Semantic memory stored", point_id=point_id)
            return str(point_id)
        except Exception as e:
            logger.error("Failed to store semantic memory", error=str(e))
            raise

    async def search_semantic(
        self,
        query_embedding: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Search semantic memory with optimized payload extraction"""
        try:
            results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
            )
            # Optimized result transformation
            return [
                {
                    "id": r.id,
                    "score": r.score,
                    "content": r.payload.get("content", ""),
                    "metadata": {k: v for k, v in r.payload.items() if k not in ("content", "timestamp")},
                    "timestamp": r.payload.get("timestamp"),
                }
                for r in results
            ]
        except Exception as e:
            logger.error("Failed to search semantic memory", error=str(e))
            return []

    async def store_episodic(
        self,
        session_id: str,
        event: Dict[str, Any],
    ) -> bool:
        """Store episodic memory"""
        try:
            key = f"ep:{session_id}"
            events = await self.redis_client.lrange(key, 0, -1)
            event["timestamp"] = datetime.utcnow().isoformat()
            await self.redis_client.rpush(key, json.dumps(event))
            await self.redis_client.expire(key, 86400 * 7)
            logger.debug("Episodic memory stored", session_id=session_id)
            return True
        except Exception as e:
            logger.error("Failed to store episodic memory", error=str(e))
            return False

    async def get_episodic(
        self,
        session_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Retrieve episodic memory"""
        try:
            key = f"ep:{session_id}"
            events = await self.redis_client.lrange(key, -limit, -1)
            return [json.loads(e) for e in events]
        except Exception as e:
            logger.error("Failed to get episodic memory", error=str(e))
            return []

    async def cleanup_old_memories(self, days: int = 30):
        """Cleanup old memories"""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            cutoff_timestamp = cutoff.isoformat()
            logger.info("Memory cleanup started", cutoff=cutoff_timestamp)
            
            # Cleanup old episodic memories from Redis
            # Scan for all episodic memory keys
            cursor = 0
            deleted_count = 0
            
            while True:
                cursor, keys = await self.redis_client.scan(cursor, match="ep:*", count=100)
                for key in keys:
                    # Get the last event to check timestamp
                    events = await self.redis_client.lrange(key, -1, -1)
                    if events:
                        try:
                            last_event = json.loads(events[0])
                            event_time = datetime.fromisoformat(last_event.get("timestamp", ""))
                            if event_time < cutoff:
                                await self.redis_client.delete(key)
                                deleted_count += 1
                        except (json.JSONDecodeError, ValueError):
                            # Skip invalid entries
                            pass
                
                if cursor == 0:
                    break
            
            logger.info("Memory cleanup completed", deleted_episodic=deleted_count)
            
        except Exception as e:
            logger.error("Memory cleanup failed", error=str(e))

    async def close(self):
        """Close connections"""
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Memory connections closed")


memory_manager = MemoryManager()
