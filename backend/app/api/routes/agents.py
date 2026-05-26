from fastapi import APIRouter, HTTPException
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

AVAILABLE_AGENTS = {
    "commander": commander,
    "coding": coding_agent,
    "research": research_agent,
    "security": security_agent,
    "uiux": uiux_agent,
    "reflection": reflection_agent,
    "memory": memory_agent,
}


@router.get("/agents")
async def list_agents():
    """List all available agents"""
    try:
        agents_info = []

        for agent_id, agent in AVAILABLE_AGENTS.items():
            agents_info.append({
                "id": agent.agent_id,
                "name": agent.name,
                "description": agent.description,
                "status": agent.status.value,
                "reasoning_mode": agent.reasoning_mode.value,
            })

        return {
            "status": "success",
            "agents": agents_info,
            "count": len(agents_info),
        }

    except Exception as e:
        logger.error("Failed to list agents", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details"""
    try:
        if agent_id not in AVAILABLE_AGENTS:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        agent = AVAILABLE_AGENTS[agent_id]

        return {
            "status": "success",
            "agent": {
                "id": agent.agent_id,
                "name": agent.name,
                "description": agent.description,
                "status": agent.status.value,
                "reasoning_mode": agent.reasoning_mode.value,
                "execution_history_count": len(agent.execution_history),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get agent", agent_id=agent_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_id}/execute")
async def execute_agent(agent_id: str, request: Dict[str, Any]):
    """Execute a task with a specific agent"""
    try:
        if agent_id not in AVAILABLE_AGENTS:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        agent = AVAILABLE_AGENTS[agent_id]
        task = request.get("task", {})

        if not task:
            raise HTTPException(status_code=400, detail="Task is required")

        logger.info("Executing agent task", agent_id=agent_id, task=task)

        result = await agent.execute(task)

        return {
            "status": "success",
            "agent_id": agent_id,
            "result": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Agent execution failed", agent_id=agent_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}/history")
async def get_agent_history(agent_id: str, limit: int = 50):
    """Get agent execution history"""
    try:
        if agent_id not in AVAILABLE_AGENTS:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        agent = AVAILABLE_AGENTS[agent_id]
        history = agent.execution_history[-limit:]

        return {
            "status": "success",
            "agent_id": agent_id,
            "history": history,
            "count": len(history),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get agent history", agent_id=agent_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/stats")
async def get_agents_stats():
    """Get statistics for all agents"""
    try:
        stats = {
            "total_agents": len(AVAILABLE_AGENTS),
            "agents": {},
        }

        for agent_id, agent in AVAILABLE_AGENTS.items():
            stats["agents"][agent_id] = {
                "status": agent.status.value,
                "executions": len(agent.execution_history),
                "reasoning_mode": agent.reasoning_mode.value,
            }

        model_stats = model_router.get_stats()
        stats["model_usage"] = model_stats

        return {
            "status": "success",
            "stats": stats,
        }

    except Exception as e:
        logger.error("Failed to get agent stats", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
