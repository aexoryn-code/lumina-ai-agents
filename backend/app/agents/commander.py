from typing import Dict, List, Any, Optional
import structlog
from app.core.agent_base import BaseAgent, ReasoningMode, AgentStatus
from app.core.model_router import TaskType

logger = structlog.get_logger()


class CommanderAgent(BaseAgent):
    """Master orchestrator agent that coordinates other agents"""

    def __init__(self, model_router, memory_manager):
        super().__init__(
            agent_id="commander",
            name="Commander Agent",
            description="Master orchestrator that delegates tasks to specialized agents",
            model_router=model_router,
            memory_manager=memory_manager,
            reasoning_mode=ReasoningMode.STRATEGIC,
        )
        self.active_agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[Dict[str, Any]] = []

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestration task"""
        self.status = AgentStatus.EXECUTING

        try:
            task_description = task.get("description", "")
            context = task.get("context", {})

            plan = await self.create_execution_plan(task_description, context)

            results = await self.execute_plan(plan)

            final_result = await self.synthesize_results(results)

            await self.log_execution(task, final_result)
            self.status = AgentStatus.COMPLETED

            return final_result

        except Exception as e:
            logger.error("Commander execution failed", error=str(e))
            self.status = AgentStatus.FAILED
            raise

    async def create_execution_plan(
        self,
        task_description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create execution plan by breaking down task"""

        planning_prompt = f"""
        Analyze this task and create an execution plan:

        Task: {task_description}
        Context: {context}

        Break down into:
        1. Subtasks (what needs to be done)
        2. Required agents (which specialized agents to use)
        3. Dependencies (task order and relationships)
        4. Success criteria

        Available agents:
        - Coding Agent: Software development, debugging, refactoring
        - Research Agent: Information retrieval, analysis, synthesis
        - UI/UX Agent: Interface design, user experience
        - Security Agent: Vulnerability detection, security analysis

        Provide a structured execution plan.
        """

        plan_text = await self.think(planning_prompt, context)

        plan = {
            "original_task": task_description,
            "plan_text": plan_text,
            "subtasks": self.parse_subtasks(plan_text),
            "timestamp": self.get_timestamp(),
        }

        logger.info("Execution plan created", subtasks=len(plan["subtasks"]))
        return plan

    def parse_subtasks(self, plan_text: str) -> List[Dict[str, Any]]:
        """Parse subtasks from plan text"""
        subtasks = []

        lines = plan_text.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '-')):
                subtasks.append({
                    "id": f"subtask_{i}",
                    "description": line.strip(),
                    "status": "pending",
                })

        return subtasks

    async def execute_plan(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the plan by coordinating agents"""
        results = []

        for subtask in plan["subtasks"]:
            logger.info("Executing subtask", subtask_id=subtask["id"])

            agent_type = self.determine_agent_type(subtask["description"])

            result = await self.delegate_to_agent(agent_type, subtask)

            results.append({
                "subtask": subtask,
                "agent": agent_type,
                "result": result,
            })

        return results

    def determine_agent_type(self, task_description: str) -> str:
        """Determine which agent type to use"""
        task_lower = task_description.lower()

        if any(word in task_lower for word in ["code", "implement", "debug", "refactor"]):
            return "coding"
        elif any(word in task_lower for word in ["research", "find", "analyze", "investigate"]):
            return "research"
        elif any(word in task_lower for word in ["design", "ui", "ux", "interface"]):
            return "uiux"
        elif any(word in task_lower for word in ["security", "vulnerability", "secure"]):
            return "security"
        else:
            return "coding"

    async def delegate_to_agent(
        self,
        agent_type: str,
        subtask: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Delegate task to specialized agent"""

        if agent_type not in self.active_agents:
            logger.warning("Agent not available", agent_type=agent_type)
            return {"status": "skipped", "reason": "Agent not available"}

        agent = self.active_agents[agent_type]

        try:
            result = await agent.execute(subtask)
            return result
        except Exception as e:
            logger.error("Agent delegation failed", agent_type=agent_type, error=str(e))
            return {"status": "failed", "error": str(e)}

    async def synthesize_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize results from all agents"""

        synthesis_prompt = f"""
        Synthesize these results into a coherent final output:

        {results}

        Provide:
        1. Summary of what was accomplished
        2. Key findings or outputs
        3. Any issues or limitations
        4. Next steps if applicable
        """

        synthesis = await self.think(synthesis_prompt)

        return {
            "status": "completed",
            "synthesis": synthesis,
            "detailed_results": results,
            "timestamp": self.get_timestamp(),
        }

    def register_agent(self, agent_type: str, agent: BaseAgent):
        """Register a specialized agent"""
        self.active_agents[agent_type] = agent
        logger.info("Agent registered", agent_type=agent_type)

    def get_system_prompt(self) -> str:
        """Get commander system prompt"""
        return """You are the Commander Agent, the master orchestrator of the Lumina AI system.

Your role:
- Break down complex tasks into manageable subtasks
- Delegate to specialized agents
- Coordinate multi-agent workflows
- Synthesize results into coherent outputs
- Ensure task completion and quality

Think strategically and orchestrate efficiently."""

    def get_task_type(self) -> TaskType:
        """Get task type for model routing"""
        return TaskType.REASONING

    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
