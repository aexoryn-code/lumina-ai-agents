from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import structlog

from app.core.memory_manager import memory_manager

logger = structlog.get_logger()
router = APIRouter()


@router.post("/memory/short-term")
async def store_short_term_memory(request: Dict[str, Any]):
    """Store short-term memory"""
    try:
        key = request.get("key")
        value = request.get("value")
        ttl = request.get("ttl", 3600)

        if not key or value is None:
            raise HTTPException(status_code=400, detail="Key and value are required")

        success = await memory_manager.store_short_term(key, value, ttl)

        return {
            "status": "success" if success else "failed",
            "key": key,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to store short-term memory", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/short-term/{key}")
async def get_short_term_memory(key: str):
    """Retrieve short-term memory"""
    try:
        value = await memory_manager.get_short_term(key)

        if value is None:
            raise HTTPException(status_code=404, detail=f"Memory not found for key: {key}")

        return {
            "status": "success",
            "key": key,
            "value": value,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get short-term memory", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/semantic")
async def store_semantic_memory(request: Dict[str, Any]):
    """Store semantic memory"""
    try:
        content = request.get("content")
        embedding = request.get("embedding")
        metadata = request.get("metadata", {})

        if not content or not embedding:
            raise HTTPException(status_code=400, detail="Content and embedding are required")

        point_id = await memory_manager.store_semantic(content, embedding, metadata)

        return {
            "status": "success",
            "point_id": point_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to store semantic memory", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/semantic/search")
async def search_semantic_memory(request: Dict[str, Any]):
    """Search semantic memory"""
    try:
        query_embedding = request.get("query_embedding")
        limit = request.get("limit", 5)
        score_threshold = request.get("score_threshold", 0.7)

        if not query_embedding:
            raise HTTPException(status_code=400, detail="Query embedding is required")

        results = await memory_manager.search_semantic(
            query_embedding,
            limit,
            score_threshold,
        )

        return {
            "status": "success",
            "results": results,
            "count": len(results),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to search semantic memory", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/episodic")
async def store_episodic_memory(request: Dict[str, Any]):
    """Store episodic memory"""
    try:
        session_id = request.get("session_id")
        event = request.get("event")

        if not session_id or not event:
            raise HTTPException(status_code=400, detail="Session ID and event are required")

        success = await memory_manager.store_episodic(session_id, event)

        return {
            "status": "success" if success else "failed",
            "session_id": session_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to store episodic memory", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/episodic/{session_id}")
async def get_episodic_memory(session_id: str, limit: int = 100):
    """Retrieve episodic memory"""
    try:
        events = await memory_manager.get_episodic(session_id, limit)

        return {
            "status": "success",
            "session_id": session_id,
            "events": events,
            "count": len(events),
        }

    except Exception as e:
        logger.error("Failed to get episodic memory", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
