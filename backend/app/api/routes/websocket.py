from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
import structlog

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

# Active WebSocket connections
active_connections: Dict[str, Set[WebSocket]] = {
    "chat": set(),
    "agents": set(),
    "memory": set(),
}

# Initialize agents
commander = CommanderAgent(model_router, memory_manager)
coding_agent = CodingAgent(model_router, memory_manager)
research_agent = ResearchAgent(model_router, memory_manager)
security_agent = SecurityAgent(model_router, memory_manager)
uiux_agent = UIUXAgent(model_router, memory_manager)
reflection_agent = ReflectionAgent(model_router, memory_manager)
memory_agent = MemoryAgent(model_router, memory_manager)

AGENTS = {
    "commander": commander,
    "coding": coding_agent,
    "research": research_agent,
    "security": security_agent,
    "uiux": uiux_agent,
    "reflection": reflection_agent,
    "memory": memory_agent,
}


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "chat": set(),
            "agents": set(),
            "memory": set(),
        }

    async def connect(self, websocket: WebSocket, channel: str = "chat"):
        """Accept and register a new connection"""
        await websocket.accept()
        self.active_connections[channel].add(websocket)
        logger.info("WebSocket connected", channel=channel)

    def disconnect(self, websocket: WebSocket, channel: str = "chat"):
        """Remove a connection"""
        self.active_connections[channel].discard(websocket)
        logger.info("WebSocket disconnected", channel=channel)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific connection"""
        await websocket.send_json(message)

    async def broadcast(self, message: dict, channel: str = "chat"):
        """Broadcast message to all connections in channel"""
        disconnected = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("Failed to send message", error=str(e))
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.active_connections[channel].discard(connection)


manager = ConnectionManager()


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, "chat")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            message_type = data.get("type", "chat")
            content = data.get("content", "")
            agent_type = data.get("agent_type", "commander")
            session_id = data.get("session_id", "default")

            logger.info(
                "WebSocket message received",
                type=message_type,
                agent_type=agent_type,
            )

            # Send acknowledgment
            await manager.send_personal_message(
                {
                    "type": "ack",
                    "message": "Message received",
                },
                websocket,
            )

            # Process based on message type
            if message_type == "chat":
                # Stream chat response
                await stream_chat_response(
                    websocket,
                    content,
                    agent_type,
                    session_id,
                )

            elif message_type == "agent_execute":
                # Execute agent task with streaming
                await stream_agent_execution(
                    websocket,
                    data.get("task", {}),
                    agent_type,
                    session_id,
                )

            elif message_type == "ping":
                # Respond to ping
                await manager.send_personal_message(
                    {"type": "pong"},
                    websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, "chat")
        logger.info("Client disconnected")

    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        manager.disconnect(websocket, "chat")


async def stream_chat_response(
    websocket: WebSocket,
    content: str,
    agent_type: str,
    session_id: str,
):
    """Stream chat response in chunks"""
    try:
        # Send start event
        await manager.send_personal_message(
            {
                "type": "stream_start",
                "agent_type": agent_type,
            },
            websocket,
        )

        # Get agent
        agent = AGENTS.get(agent_type, commander)

        # Execute agent task
        if agent_type == "commander":
            task = {
                "description": content,
                "context": {},
            }
        else:
            task = {
                "type": "generate",
                "description": content,
                "context": {},
            }

        result = await agent.execute(task)

        # Stream response in chunks
        response_text = str(result)
        chunk_size = 50

        for i in range(0, len(response_text), chunk_size):
            chunk = response_text[i:i + chunk_size]

            await manager.send_personal_message(
                {
                    "type": "stream_chunk",
                    "content": chunk,
                },
                websocket,
            )

            # Small delay for streaming effect
            await asyncio.sleep(0.05)

        # Send completion event
        await manager.send_personal_message(
            {
                "type": "stream_end",
                "result": result,
            },
            websocket,
        )

        # Store in memory
        await memory_manager.store_episodic(
            session_id=session_id,
            event={
                "type": "chat",
                "agent_type": agent_type,
                "content": content,
                "result": result,
            },
        )

    except Exception as e:
        logger.error("Stream error", error=str(e))
        await manager.send_personal_message(
            {
                "type": "error",
                "message": str(e),
            },
            websocket,
        )


async def stream_agent_execution(
    websocket: WebSocket,
    task: dict,
    agent_type: str,
    session_id: str,
):
    """Stream agent execution with status updates"""
    try:
        # Send start event
        await manager.send_personal_message(
            {
                "type": "execution_start",
                "agent_type": agent_type,
                "task": task,
            },
            websocket,
        )

        # Get agent
        agent = AGENTS.get(agent_type, commander)

        # Send thinking status
        await manager.send_personal_message(
            {
                "type": "status",
                "status": "thinking",
                "message": f"{agent.name} is processing your request...",
            },
            websocket,
        )

        # Execute task
        result = await agent.execute(task)

        # Send completion
        await manager.send_personal_message(
            {
                "type": "execution_complete",
                "result": result,
            },
            websocket,
        )

        # Store in memory
        await memory_manager.store_episodic(
            session_id=session_id,
            event={
                "type": "agent_execution",
                "agent_type": agent_type,
                "task": task,
                "result": result,
            },
        )

    except Exception as e:
        logger.error("Execution error", error=str(e))
        await manager.send_personal_message(
            {
                "type": "error",
                "message": str(e),
            },
            websocket,
        )


@router.websocket("/ws/agents")
async def websocket_agents(websocket: WebSocket):
    """WebSocket endpoint for agent status updates"""
    await manager.connect(websocket, "agents")

    try:
        while True:
            # Send agent status updates
            agent_status = {
                "type": "agent_status",
                "agents": {
                    agent_id: {
                        "status": agent.status.value,
                        "executions": len(agent.execution_history),
                    }
                    for agent_id, agent in AGENTS.items()
                },
            }

            await manager.send_personal_message(agent_status, websocket)

            # Wait before next update
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        manager.disconnect(websocket, "agents")


@router.websocket("/ws/memory")
async def websocket_memory(websocket: WebSocket):
    """WebSocket endpoint for memory updates"""
    await manager.connect(websocket, "memory")

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "subscribe":
                session_id = data.get("session_id", "default")

                # Send memory updates
                events = await memory_manager.get_episodic(session_id, limit=10)

                await manager.send_personal_message(
                    {
                        "type": "memory_update",
                        "session_id": session_id,
                        "events": events,
                    },
                    websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, "memory")
