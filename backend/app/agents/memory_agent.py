from typing import Dict, List, Any, Optional
import structlog
from app.core.agent_base import BaseAgent, ReasoningMode, AgentStatus
from app.core.model_router import TaskType

logger = structlog.get_logger()


class MemoryAgent(BaseAgent):
    """Specialized agent for memory operations, retrieval, and context management"""

    def __init__(self, model_router, memory_manager):
        super().__init__(
            agent_id="memory",
            name="Memory Agent",
            description="Expert in memory operations, retrieval, and context management",
            model_router=model_router,
            memory_manager=memory_manager,
            reasoning_mode=ReasoningMode.FAST,
        )

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute memory task"""
        self.status = AgentStatus.EXECUTING

        try:
            task_type = task.get("type", "retrieve")
            description = task.get("description", "")
            context = task.get("context", {})

            if task_type == "retrieve":
                result = await self.retrieve_memory(description, context)
            elif task_type == "store":
                result = await self.store_memory(description, context)
            elif task_type == "search":
                result = await self.search_memory(description, context)
            elif task_type == "summarize":
                result = await self.summarize_memory(description, context)
            elif task_type == "analyze":
                result = await self.analyze_context(description, context)
            else:
                result = await self.retrieve_memory(description, context)

            await self.log_execution(task, result)
            self.status = AgentStatus.COMPLETED

            return result

        except Exception as e:
            logger.error("Memory agent execution failed", error=str(e))
            self.status = AgentStatus.FAILED
            raise

    async def retrieve_memory(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Retrieve relevant memories"""

        session_id = context.get("session_id", "default")
        memory_type = context.get("memory_type", "episodic")
        limit = context.get("limit", 10)

        if memory_type == "episodic":
            memories = await self.memory_manager.get_episodic(session_id, limit)
        elif memory_type == "short_term":
            key = context.get("key", "")
            memory = await self.memory_manager.get_short_term(key)
            memories = [memory] if memory else []
        else:
            memories = []

        return {
            "status": "success",
            "memories": memories,
            "memory_type": memory_type,
            "count": len(memories),
        }

    async def store_memory(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Store information in memory"""

        session_id = context.get("session_id", "default")
        memory_type = context.get("memory_type", "episodic")
        content = context.get("content", description)

        if memory_type == "episodic":
            success = await self.memory_manager.store_episodic(
                session_id=session_id,
                event={
                    "type": "user_input",
                    "content": content,
                    "description": description,
                },
            )
        elif memory_type == "short_term":
            key = context.get("key", "temp")
            ttl = context.get("ttl", 3600)
            success = await self.memory_manager.store_short_term(key, content, ttl)
        else:
            success = False

        return {
            "status": "success" if success else "failed",
            "memory_type": memory_type,
            "stored": success,
        }

    async def search_memory(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Search memories for relevant information"""

        session_id = context.get("session_id", "default")
        query = context.get("query", description)
        limit = context.get("limit", 5)

        # Get recent memories
        memories = await self.memory_manager.get_episodic(session_id, limit=50)

        # Use AI to find relevant memories
        search_prompt = f"""
        Search through these memories for information relevant to: {query}

        Memories:
        {memories}

        Provide:
        1. Most relevant memories (ranked by relevance)
        2. Key information found
        3. Connections between memories
        4. Summary of findings

        Be specific and cite memory indices.
        """

        search_results = await self.think(search_prompt, context)

        return {
            "status": "success",
            "query": query,
            "search_results": search_results,
            "memories_searched": len(memories),
        }

    async def summarize_memory(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Summarize memory history"""

        session_id = context.get("session_id", "default")
        limit = context.get("limit", 100)

        memories = await self.memory_manager.get_episodic(session_id, limit)

        summary_prompt = f"""
        Summarize this memory history:

        Memories:
        {memories}

        Context: {description}

        Provide:
        1. Overview of activities
        2. Key events and milestones
        3. Patterns and trends
        4. Important information to remember
        5. Context for future interactions

        Be concise but comprehensive.
        """

        summary = await self.think(summary_prompt, context)

        return {
            "status": "success",
            "summary": summary,
            "memories_summarized": len(memories),
            "session_id": session_id,
        }

    async def analyze_context(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze current context and memory state"""

        session_id = context.get("session_id", "default")
        current_task = context.get("current_task", "")

        # Get recent memories
        memories = await self.memory_manager.get_episodic(session_id, limit=20)

        analysis_prompt = f"""
        Analyze the current context:

        Current Task: {current_task}
        Description: {description}

        Recent Memories:
        {memories}

        Provide:
        1. Relevant context from memory
        2. User preferences and patterns
        3. Previous related tasks
        4. Important information to consider
        5. Recommendations for current task

        Help inform the current task with historical context.
        """

        analysis = await self.think(analysis_prompt, context)

        return {
            "status": "success",
            "analysis": analysis,
            "memories_analyzed": len(memories),
        }

    async def get_relevant_context(
        self,
        task_description: str,
        session_id: str = "default",
    ) -> Dict[str, Any]:
        """Get relevant context for a task"""

        memories = await self.memory_manager.get_episodic(session_id, limit=30)

        context_prompt = f"""
        Extract relevant context for this task:

        Task: {task_description}

        Available Memories:
        {memories}

        Provide:
        1. Directly relevant information
        2. Related past tasks
        3. User preferences
        4. Important constraints or requirements
        5. Suggested approach based on history

        Be specific and actionable.
        """

        relevant_context = await self.think(context_prompt)

        return {
            "status": "success",
            "relevant_context": relevant_context,
            "task": task_description,
        }

    def get_system_prompt(self) -> str:
        """Get memory agent system prompt"""
        return """You are the Memory Agent, an expert in memory operations and context management.

Your expertise:
- Memory retrieval and storage
- Context analysis
- Pattern recognition
- Information synthesis
- Relevance assessment
- Memory summarization
- Context-aware recommendations

Principles:
- Prioritize relevant information
- Maintain context continuity
- Identify patterns and connections
- Provide actionable insights
- Respect memory boundaries
- Optimize for retrieval
- Support other agents with context"""

    def get_task_type(self) -> TaskType:
        """Get task type for model routing"""
        return TaskType.FAST
