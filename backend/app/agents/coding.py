from typing import Dict, List, Any, Optional
import structlog
from app.core.agent_base import BaseAgent, ReasoningMode, AgentStatus
from app.core.model_router import TaskType

logger = structlog.get_logger()


class CodingAgent(BaseAgent):
    """Specialized agent for software development tasks"""

    def __init__(self, model_router, memory_manager):
        super().__init__(
            agent_id="coding",
            name="Coding Agent",
            description="Expert in software development, debugging, and code optimization",
            model_router=model_router,
            memory_manager=memory_manager,
            reasoning_mode=ReasoningMode.DEEP,
        )
        self.supported_languages = [
            "python", "typescript", "javascript", "rust", "go",
            "java", "cpp", "csharp", "php", "ruby", "swift", "kotlin"
        ]

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coding task"""
        self.status = AgentStatus.EXECUTING

        try:
            task_type = task.get("type", "generate")
            description = task.get("description", "")
            context = task.get("context", {})

            if task_type == "generate":
                result = await self.generate_code(description, context)
            elif task_type == "debug":
                result = await self.debug_code(description, context)
            elif task_type == "refactor":
                result = await self.refactor_code(description, context)
            elif task_type == "review":
                result = await self.review_code(description, context)
            else:
                result = await self.generate_code(description, context)

            if context.get("enable_reflection", True):
                reflection = await self.reflect(str(result))
                result["reflection"] = reflection

            await self.log_execution(task, result)
            self.status = AgentStatus.COMPLETED

            return result

        except Exception as e:
            logger.error("Coding agent execution failed", error=str(e))
            self.status = AgentStatus.FAILED
            raise

    async def generate_code(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate code based on description"""

        language = context.get("language", "python")
        framework = context.get("framework", "")
        requirements = context.get("requirements", [])

        prompt = f"""
        Generate production-grade code for:

        Description: {description}
        Language: {language}
        Framework: {framework if framework else "standard library"}
        Requirements: {requirements}

        Provide:
        1. Clean, well-structured code
        2. Type hints/annotations
        3. Error handling
        4. Brief inline comments for complex logic
        5. Modular design

        Code:
        """

        code = await self.think(prompt, context)

        return {
            "status": "success",
            "code": code,
            "language": language,
            "framework": framework,
        }

    async def debug_code(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Debug code and identify issues"""

        code = context.get("code", "")
        error = context.get("error", "")

        prompt = f"""
        Debug this code:

        Code:
        {code}

        Error/Issue: {error}
        Description: {description}

        Provide:
        1. Root cause analysis
        2. Fixed code
        3. Explanation of the fix
        4. Prevention tips
        """

        analysis = await self.think(prompt, context)

        return {
            "status": "success",
            "analysis": analysis,
            "original_code": code,
        }

    async def refactor_code(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Refactor code for better quality"""

        code = context.get("code", "")
        goals = context.get("goals", ["readability", "performance", "maintainability"])

        prompt = f"""
        Refactor this code:

        Code:
        {code}

        Goals: {goals}
        Description: {description}

        Provide:
        1. Refactored code
        2. Changes made
        3. Benefits of refactoring
        4. Any trade-offs
        """

        refactored = await self.think(prompt, context)

        return {
            "status": "success",
            "refactored_code": refactored,
            "goals": goals,
        }

    async def review_code(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Review code for quality and issues"""

        code = context.get("code", "")

        prompt = f"""
        Review this code:

        Code:
        {code}

        Description: {description}

        Analyze:
        1. Code quality and style
        2. Potential bugs
        3. Security issues
        4. Performance concerns
        5. Best practices adherence
        6. Suggestions for improvement

        Provide structured review.
        """

        review = await self.think(prompt, context)

        return {
            "status": "success",
            "review": review,
        }

    def get_system_prompt(self) -> str:
        """Get coding agent system prompt"""
        return f"""You are the Coding Agent, an expert software engineer.

Supported languages: {', '.join(self.supported_languages)}

Your expertise:
- Writing clean, production-grade code
- Debugging complex issues
- Code optimization and refactoring
- Security best practices
- Modern frameworks and patterns

Principles:
- Write modular, maintainable code
- Include proper error handling
- Follow language-specific best practices
- Prioritize readability and performance
- Consider security implications"""

    def get_task_type(self) -> TaskType:
        """Get task type for model routing"""
        return TaskType.CODING
