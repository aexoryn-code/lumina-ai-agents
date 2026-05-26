from typing import Dict, List, Any, Optional
import structlog
from app.core.agent_base import BaseAgent, ReasoningMode, AgentStatus
from app.core.model_router import TaskType

logger = structlog.get_logger()


class UIUXAgent(BaseAgent):
    """Specialized agent for UI/UX design and user experience"""

    def __init__(self, model_router, memory_manager):
        super().__init__(
            agent_id="uiux",
            name="UI/UX Agent",
            description="Expert in interface design, user experience, and visual systems",
            model_router=model_router,
            memory_manager=memory_manager,
            reasoning_mode=ReasoningMode.CREATOR,
        )
        self.design_principles = [
            "accessibility",
            "usability",
            "visual_hierarchy",
            "consistency",
            "feedback",
            "simplicity",
        ]

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute UI/UX task"""
        self.status = AgentStatus.EXECUTING

        try:
            task_type = task.get("type", "design")
            description = task.get("description", "")
            context = task.get("context", {})

            if task_type == "design":
                result = await self.create_design(description, context)
            elif task_type == "review":
                result = await self.review_design(description, context)
            elif task_type == "improve":
                result = await self.improve_ux(description, context)
            elif task_type == "prototype":
                result = await self.create_prototype(description, context)
            else:
                result = await self.create_design(description, context)

            if context.get("enable_reflection", True):
                reflection = await self.reflect(str(result))
                result["reflection"] = reflection

            await self.log_execution(task, result)
            self.status = AgentStatus.COMPLETED

            return result

        except Exception as e:
            logger.error("UI/UX agent execution failed", error=str(e))
            self.status = AgentStatus.FAILED
            raise

    async def create_design(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create UI/UX design"""

        target_platform = context.get("platform", "web")
        design_system = context.get("design_system", "modern")
        user_personas = context.get("user_personas", [])

        prompt = f"""
        Create a UI/UX design for:

        Description: {description}
        Platform: {target_platform}
        Design System: {design_system}
        User Personas: {user_personas}

        Provide:
        1. Layout structure and hierarchy
        2. Component breakdown
        3. Color scheme and typography
        4. Interaction patterns
        5. Accessibility considerations
        6. Responsive design approach
        7. Implementation notes

        Focus on modern, clean, and user-friendly design.
        """

        design = await self.think(prompt, context)

        return {
            "status": "success",
            "design": design,
            "platform": target_platform,
            "design_system": design_system,
        }

    async def review_design(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Review existing design"""

        design_description = context.get("design", "")
        screenshots = context.get("screenshots", [])

        prompt = f"""
        Review this UI/UX design:

        Design: {design_description}
        Screenshots: {screenshots}
        Context: {description}

        Evaluate:
        1. Visual hierarchy and layout
        2. Usability and user flow
        3. Accessibility (WCAG compliance)
        4. Consistency and design patterns
        5. Mobile responsiveness
        6. Performance implications
        7. Areas for improvement

        Provide structured feedback with specific recommendations.
        """

        review = await self.think(prompt, context)

        return {
            "status": "success",
            "review": review,
        }

    async def improve_ux(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Improve user experience"""

        current_ux = context.get("current_ux", "")
        pain_points = context.get("pain_points", [])
        goals = context.get("goals", [])

        prompt = f"""
        Improve the user experience:

        Current UX: {current_ux}
        Pain Points: {pain_points}
        Goals: {goals}
        Description: {description}

        Provide:
        1. UX improvements and solutions
        2. User flow optimizations
        3. Interaction enhancements
        4. Accessibility improvements
        5. Performance optimizations
        6. Implementation priority
        7. Expected impact

        Focus on measurable UX improvements.
        """

        improvements = await self.think(prompt, context)

        return {
            "status": "success",
            "improvements": improvements,
            "pain_points": pain_points,
        }

    async def create_prototype(
        self,
        description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create interactive prototype specification"""

        features = context.get("features", [])
        framework = context.get("framework", "React")

        prompt = f"""
        Create an interactive prototype specification:

        Description: {description}
        Features: {features}
        Framework: {framework}

        Provide:
        1. Component structure
        2. State management approach
        3. Interaction flows
        4. Animation and transitions
        5. Sample code snippets
        6. Styling approach
        7. Testing considerations

        Create a detailed prototype specification.
        """

        prototype = await self.think(prompt, context)

        return {
            "status": "success",
            "prototype": prototype,
            "framework": framework,
        }

    def get_system_prompt(self) -> str:
        """Get UI/UX agent system prompt"""
        return f"""You are the UI/UX Agent, an expert in interface design and user experience.

Design Principles: {', '.join(self.design_principles)}

Your expertise:
- Modern UI/UX design
- User-centered design
- Accessibility (WCAG 2.1)
- Responsive design
- Design systems
- Interaction design
- Visual design
- Prototyping

Principles:
- Prioritize user needs
- Design for accessibility
- Maintain consistency
- Provide clear feedback
- Optimize for performance
- Follow platform conventions
- Create delightful experiences"""

    def get_task_type(self) -> TaskType:
        """Get task type for model routing"""
        return TaskType.CREATIVITY
