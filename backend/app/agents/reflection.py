from typing import Dict, List, Any, Optional
import structlog
from app.core.agent_base import BaseAgent, ReasoningMode, AgentStatus
from app.core.model_router import TaskType

logger = structlog.get_logger()


class ReflectionAgent(BaseAgent):
    """Specialized agent for self-critique, quality assessment, and output verification"""

    def __init__(self, model_router, memory_manager):
        super().__init__(
            agent_id="reflection",
            name="Reflection Agent",
            description="Expert in self-critique, quality assessment, and output verification",
            model_router=model_router,
            memory_manager=memory_manager,
            reasoning_mode=ReasoningMode.DEEP,
        )
        self.quality_criteria = [
            "accuracy",
            "completeness",
            "clarity",
            "logic",
            "consistency",
        ]

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute reflection task"""
        self.status = AgentStatus.EXECUTING

        try:
            task_type = task.get("type", "critique")
            description = task.get("description", "")
            context = task.get("context", {})

            if task_type == "critique":
                result = await self.critique_output(description, context)
            elif task_type == "verify":
                result = await self.verify_quality(description, context)
            elif task_type == "improve":
                result = await self.suggest_improvements(description, context)
            elif task_type == "score":
                result = await self.score_output(description, context)
            else:
                result = await self.critique_output(description, context)

            await self.log_execution(task, result)
            self.status = AgentStatus.COMPLETED

            return result

        except Exception as e:
            logger.error("Reflection agent execution failed", error=str(e))
            self.status = AgentStatus.FAILED
            raise

    async def critique_output(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Provide detailed critique of output"""

        output = context.get("output", "")
        criteria = context.get("criteria", self.quality_criteria)

        prompt = f"""
        Perform a detailed critique of this output:

        Output:
        {output}

        Context: {description}

        Evaluate based on:
        {', '.join(criteria)}

        For each criterion, provide:
        1. Score (0-10)
        2. Strengths
        3. Weaknesses
        4. Specific issues found
        5. Recommendations for improvement

        Be thorough, specific, and constructive.
        """

        critique = await self.think(prompt, context)

        return {
            "status": "success",
            "critique": critique,
            "criteria": criteria,
            "output_analyzed": output[:200] + "..." if len(output) > 200 else output,
        }

    async def verify_quality(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Verify output quality and detect issues"""

        output = context.get("output", "")
        requirements = context.get("requirements", [])

        prompt = f"""
        Verify the quality of this output:

        Output:
        {output}

        Requirements: {requirements}
        Context: {description}

        Check for:
        1. Hallucinations or false information
        2. Logic errors or inconsistencies
        3. Missing required elements
        4. Incomplete implementations
        5. Security vulnerabilities
        6. Performance issues
        7. Code quality problems (if applicable)

        For each issue found:
        - Severity: Critical/High/Medium/Low
        - Location: Where in the output
        - Description: What's wrong
        - Impact: Why it matters
        - Fix: How to resolve it

        Provide a pass/fail verdict with justification.
        """

        verification = await self.think(prompt, context)

        return {
            "status": "success",
            "verification": verification,
            "requirements_checked": requirements,
        }

    async def suggest_improvements(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Suggest specific improvements"""

        output = context.get("output", "")
        goals = context.get("goals", [])

        prompt = f"""
        Suggest improvements for this output:

        Output:
        {output}

        Goals: {goals}
        Context: {description}

        Provide:
        1. Priority improvements (must-have)
        2. Recommended improvements (should-have)
        3. Optional enhancements (nice-to-have)

        For each improvement:
        - What to change
        - Why it's important
        - How to implement it
        - Expected benefit

        Be specific and actionable.
        """

        improvements = await self.think(prompt, context)

        return {
            "status": "success",
            "improvements": improvements,
            "goals": goals,
        }

    async def score_output(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Score output quality with detailed breakdown"""

        output = context.get("output", "")
        criteria = context.get("criteria", self.quality_criteria)

        prompt = f"""
        Score this output on a scale of 0-100:

        Output:
        {output}

        Context: {description}

        Provide scores for:
        {', '.join(criteria)}

        For each criterion:
        - Score (0-10)
        - Justification
        - Key factors

        Then provide:
        - Overall score (0-100)
        - Overall assessment
        - Key strengths
        - Key weaknesses
        - Confidence level in assessment

        Be objective and detailed.
        """

        scoring = await self.think(prompt, context)

        return {
            "status": "success",
            "scoring": scoring,
            "criteria": criteria,
        }

    async def reflect_on_agent_output(
        self,
        agent_name: str,
        agent_output: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Reflect on another agent's output"""

        prompt = f"""
        Reflect on the output from {agent_name}:

        Output:
        {agent_output}

        Analyze:
        1. Did the agent fulfill its purpose?
        2. Is the output accurate and complete?
        3. Are there any errors or issues?
        4. What could be improved?
        5. Should this output be accepted or revised?

        Provide:
        - Verdict: Accept/Revise/Reject
        - Confidence: 0-100%
        - Issues found (if any)
        - Recommendations (if needed)
        """

        reflection = await self.think(prompt)

        return {
            "status": "success",
            "agent_name": agent_name,
            "reflection": reflection,
            "original_output": agent_output,
        }

    def get_system_prompt(self) -> str:
        """Get reflection agent system prompt"""
        return f"""You are the Reflection Agent, an expert in quality assessment and critique.

Quality Criteria: {', '.join(self.quality_criteria)}

Your expertise:
- Critical analysis
- Quality assessment
- Error detection
- Logic verification
- Hallucination detection
- Output validation
- Constructive feedback

Principles:
- Be thorough and specific
- Identify both strengths and weaknesses
- Provide actionable recommendations
- Be objective and fair
- Focus on improvement
- Detect subtle issues
- Verify factual accuracy"""

    def get_task_type(self) -> TaskType:
        """Get task type for model routing"""
        return TaskType.REASONING
