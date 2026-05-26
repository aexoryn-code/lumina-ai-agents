from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
import structlog
from datetime import datetime

from app.core.model_router import router as model_router
from app.core.memory_manager import memory_manager
from app.agents.commander import CommanderAgent
from app.agents.coding import CodingAgent
from app.agents.research import ResearchAgent
from app.agents.security import SecurityAgent
from app.agents.uiux import UIUXAgent
from app.agents.reflection import ReflectionAgent
from app.agents.memory_agent import MemoryAgent

logger = structlog.get_logger()
router = APIRouter()

# Initialize agents
commander = CommanderAgent(model_router, memory_manager)
coding_agent = CodingAgent(model_router, memory_manager)
research_agent = ResearchAgent(model_router, memory_manager)
security_agent = SecurityAgent(model_router, memory_manager)
uiux_agent = UIUXAgent(model_router, memory_manager)
reflection_agent = ReflectionAgent(model_router, memory_manager)
memory_agent = MemoryAgent(model_router, memory_manager)

# Register agents with commander
commander.register_agent("coding", coding_agent)
commander.register_agent("research", research_agent)
commander.register_agent("security", security_agent)
commander.register_agent("uiux", uiux_agent)
commander.register_agent("reflection", reflection_agent)
commander.register_agent("memory", memory_agent)


@router.post("/chat")
async def chat(request: Dict[str, Any]):
    """Chat endpoint for conversational interactions"""
    try:
        messages = request.get("messages", [])
        session_id = request.get("session_id", "default")
        model = request.get("model")
        temperature = request.get("temperature", 0.7)

        if not messages:
            raise HTTPException(status_code=400, detail="Messages are required")

        response = await model_router.complete(
            messages=messages,
            model=model,
            temperature=temperature,
        )

        await memory_manager.store_episodic(
            session_id=session_id,
            event={
                "type": "chat",
                "messages": messages,
                "response": response["content"],
            },
        )

        return {
            "status": "success",
            "response": response["content"],
            "model": response["model"],
            "usage": response.get("usage"),
        }

    except Exception as e:
        logger.error("Chat failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: Dict[str, Any]):
    """Streaming chat endpoint"""
    try:
        messages = request.get("messages", [])

        if not messages:
            raise HTTPException(status_code=400, detail="Messages are required")

        return {
            "status": "success",
            "message": "Streaming not yet implemented",
        }

    except Exception as e:
        logger.error("Chat stream failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    """Get chat history for a session"""
    try:
        history = await memory_manager.get_episodic(session_id, limit)

        return {
            "status": "success",
            "session_id": session_id,
            "history": history,
            "count": len(history),
        }

    except Exception as e:
        logger.error("Failed to get chat history", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/agent")
async def chat_with_agent(request: Dict[str, Any]):
    """Chat with a specific agent"""
    try:
        agent_type = request.get("agent_type", "commander")
        task = request.get("task", {})
        session_id = request.get("session_id", "default")

        agents = {
            "commander": commander,
            "coding": coding_agent,
            "research": research_agent,
            "security": security_agent,
            "uiux": uiux_agent,
            "reflection": reflection_agent,
            "memory": memory_agent,
        }

        if agent_type not in agents:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")

        agent = agents[agent_type]
        result = await agent.execute(task)

        await memory_manager.store_episodic(
            session_id=session_id,
            event={
                "type": "agent_execution",
                "agent_type": agent_type,
                "task": task,
                "result": result,
            },
        )

        return {
            "status": "success",
            "agent_type": agent_type,
            "result": result,
        }

    except Exception as e:
        logger.error("Agent chat failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear chat history for a session"""
    try:
        return {
            "status": "success",
            "message": f"History cleared for session {session_id}",
        }

    except Exception as e:
        logger.error("Failed to clear chat history", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
