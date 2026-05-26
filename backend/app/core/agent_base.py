from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import structlog
from pydantic import BaseModel

from app.core.model_router import ModelRouter, TaskType
from app.core.memory_manager import MemoryManager

logger = structlog.get_logger()


class ReasoningMode(str, Enum):
    """Agent reasoning modes"""
    FAST = "fast"
    DEEP = "deep"
    STRATEGIC = "strategic"
    CREATOR = "creator"
    ARCHITECT = "architect"


class AgentStatus(str, Enum):
    """Agent execution status"""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentMessage(BaseModel):
    """Message structure for agent communication"""
    sender: str
    recipient: str
    content: str
    message_type: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    """Base class for all Lumina agents"""

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        model_router: ModelRouter,
        memory_manager: MemoryManager,
        reasoning_mode: ReasoningMode = ReasoningMode.DEEP,
    ):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.model_router = model_router
        self.memory_manager = memory_manager
        self.reasoning_mode = reasoning_mode
        self.status = AgentStatus.IDLE
        self.tools: Dict[str, Callable] = {}
        self.message_queue: List[AgentMessage] = []
        self.execution_history: List[Dict[str, Any]] = []

        logger.info(
            "Agent initialized",
            agent_id=agent_id,
            name=name,
            reasoning_mode=reasoning_mode,
        )

    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task - must be implemented by subclasses"""
        pass

    async def think(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate response using model router"""
        self.status = AgentStatus.THINKING

        messages = [{"role": "system", "content": self.get_system_prompt()}]

        if context:
            messages.append({
                "role": "user",
                "content": f"Context: {context}\n\nTask: {prompt}"
            })
        else:
            messages.append({"role": "user", "content": prompt})

        try:
            task_type = self.get_task_type()
            response = await self.model_router.complete(
                messages=messages,
                task_type=task_type,
                temperature=self.get_temperature(),
            )

            await self.memory_manager.store_short_term(
                f"agent:{self.agent_id}:last_thought",
                response["content"],
                ttl=3600,
            )

            return response["content"]

        except Exception as e:
            logger.error("Agent thinking failed", agent_id=self.agent_id, error=str(e))
            raise

    async def reflect(self, output: str) -> Dict[str, Any]:
        """Self-critique and quality check"""
        reflection_prompt = f"""
        Analyze this output for quality:

        {output}

        Evaluate:
        1. Accuracy and correctness
        2. Completeness
        3. Logic gaps
        4. Potential hallucinations
        5. Overall quality score (0-100)

        Provide structured feedback.
        """

        reflection = await self.think(reflection_prompt)

        return {
            "original_output": output,
            "reflection": reflection,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def send_message(self, recipient: str, content: str, message_type: str = "task"):
        """Send message to another agent"""
        message = AgentMessage(
            sender=self.agent_id,
            recipient=recipient,
            content=content,
            message_type=message_type,
            timestamp=datetime.utcnow(),
        )
        self.message_queue.append(message)
        logger.debug("Message sent", sender=self.agent_id, recipient=recipient)

    async def receive_messages(self) -> List[AgentMessage]:
        """Receive pending messages"""
        messages = [m for m in self.message_queue if m.recipient == self.agent_id]
        self.message_queue = [m for m in self.message_queue if m.recipient != self.agent_id]
        return messages

    def register_tool(self, name: str, func: Callable):
        """Register a tool for agent use"""
        self.tools[name] = func
        logger.debug("Tool registered", agent_id=self.agent_id, tool=name)

    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a registered tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")

        try:
            result = await self.tools[tool_name](**kwargs)
            logger.debug("Tool executed", agent_id=self.agent_id, tool=tool_name)
            return result
        except Exception as e:
            logger.error("Tool execution failed", tool=tool_name, error=str(e))
            raise

    def get_system_prompt(self) -> str:
        """Get agent system prompt - can be overridden"""
        return f"""You are {self.name}, a specialized AI agent.

Description: {self.description}
Reasoning Mode: {self.reasoning_mode.value}

Execute tasks with precision and intelligence."""

    def get_task_type(self) -> TaskType:
        """Get task type for model routing - can be overridden"""
        return TaskType.REASONING

    def get_temperature(self) -> float:
        """Get temperature for generation - can be overridden"""
        mode_temps = {
            ReasoningMode.FAST: 0.3,
            ReasoningMode.DEEP: 0.7,
            ReasoningMode.STRATEGIC: 0.5,
            ReasoningMode.CREATOR: 0.9,
            ReasoningMode.ARCHITECT: 0.6,
        }
        return mode_temps.get(self.reasoning_mode, 0.7)

    async def log_execution(self, task: Dict[str, Any], result: Dict[str, Any]):
        """Log execution for history"""
        entry = {
            "agent_id": self.agent_id,
            "task": task,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
            "reasoning_mode": self.reasoning_mode.value,
        }
        self.execution_history.append(entry)

        await self.memory_manager.store_episodic(
            session_id=self.agent_id,
            event=entry,
        )
