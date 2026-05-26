from typing import Dict, List, Any, Optional
import structlog
from app.core.agent_base import BaseAgent, ReasoningMode, AgentStatus
from app.core.model_router import TaskType

logger = structlog.get_logger()


class ResearchAgent(BaseAgent):
    """Specialized agent for information retrieval and analysis"""

    def __init__(self, model_router, memory_manager):
        super().__init__(
            agent_id="research",
            name="Research Agent",
            description="Expert in information retrieval, analysis, and synthesis",
            model_router=model_router,
            memory_manager=memory_manager,
            reasoning_mode=ReasoningMode.DEEP,
        )

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research task"""
        self.status = AgentStatus.EXECUTING

        try:
            task_type = task.get("type", "research")
            description = task.get("description", "")
            context = task.get("context", {})

            if task_type == "research":
                result = await self.conduct_research(description, context)
            elif task_type == "analyze":
                result = await self.analyze_information(description, context)
            elif task_type == "synthesize":
                result = await self.synthesize_findings(description, context)
            else:
                result = await self.conduct_research(description, context)

            if context.get("enable_reflection", True):
                reflection = await self.reflect(str(result))
                result["reflection"] = reflection

            await self.log_execution(task, result)
            self.status = AgentStatus.COMPLETED

            return result

        except Exception as e:
            logger.error("Research agent execution failed", error=str(e))
            self.status = AgentStatus.FAILED
            raise

    async def conduct_research(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Conduct research on a topic"""

        topic = context.get("topic", description)
        depth = context.get("depth", "comprehensive")
        sources = context.get("sources", [])

        prompt = f"""
        Conduct research on:

        Topic: {topic}
        Depth: {depth}
        Available sources: {sources if sources else "general knowledge"}

        Provide:
        1. Overview of the topic
        2. Key findings and insights
        3. Important facts and data
        4. Different perspectives
        5. Relevant examples
        6. Summary and conclusions

        Be thorough and accurate.
        """

        research = await self.think(prompt, context)

        return {
            "status": "success",
            "research": research,
            "topic": topic,
            "depth": depth,
        }

    async def analyze_information(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze information and extract insights"""

        data = context.get("data", "")
        analysis_type = context.get("analysis_type", "general")

        prompt = f"""
        Analyze this information:

        Data:
        {data}

        Analysis type: {analysis_type}
        Description: {description}

        Provide:
        1. Key patterns and trends
        2. Important insights
        3. Relationships and connections
        4. Implications
        5. Recommendations

        Be analytical and thorough.
        """

        analysis = await self.think(prompt, context)

        return {
            "status": "success",
            "analysis": analysis,
            "analysis_type": analysis_type,
        }

    async def synthesize_findings(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Synthesize multiple findings into coherent output"""

        findings = context.get("findings", [])
        synthesis_goal = context.get("goal", "comprehensive summary")

        prompt = f"""
        Synthesize these findings:

        Findings:
        {findings}

        Goal: {synthesis_goal}
        Description: {description}

        Provide:
        1. Integrated summary
        2. Common themes
        3. Contradictions or gaps
        4. Overall conclusions
        5. Actionable insights

        Create a coherent synthesis.
        """

        synthesis = await self.think(prompt, context)

        return {
            "status": "success",
            "synthesis": synthesis,
            "findings_count": len(findings),
        }

    def get_system_prompt(self) -> str:
        """Get research agent system prompt"""
        return """You are the Research Agent, an expert information analyst.

Your expertise:
- Information retrieval and synthesis
- Critical analysis
- Pattern recognition
- Fact verification
- Insight extraction

Principles:
- Be thorough and accurate
- Verify information when possible
- Identify multiple perspectives
- Distinguish facts from opinions
- Provide actionable insights
- Cite sources when available"""

    def get_task_type(self) -> TaskType:
        """Get task type for model routing"""
        return TaskType.REASONING
