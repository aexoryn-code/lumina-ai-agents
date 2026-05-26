from typing import Dict, List, Optional, Any
from enum import Enum
import structlog
from litellm import completion, acompletion
from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


class TaskType(str, Enum):
    """Task types for routing"""
    CODING = "coding"
    CREATIVITY = "creativity"
    REASONING = "reasoning"
    LONG_CONTEXT = "long_context"
    FAST = "fast"
    COST_SENSITIVE = "cost_sensitive"
    CRITICAL = "critical"


class ModelProvider(str, Enum):
    """Supported model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"
    MISTRAL = "mistral"
    GROQ = "groq"


MODEL_CONFIGS = {
    "gpt-4o": {
        "provider": ModelProvider.OPENAI,
        "strengths": [TaskType.CODING, TaskType.CREATIVITY],
        "context_window": 128000,
        "cost_per_1k_tokens": 0.005,
    },
    "claude-3-opus": {
        "provider": ModelProvider.ANTHROPIC,
        "strengths": [TaskType.REASONING, TaskType.LONG_CONTEXT, TaskType.CRITICAL],
        "context_window": 200000,
        "cost_per_1k_tokens": 0.015,
    },
    "claude-3-sonnet": {
        "provider": ModelProvider.ANTHROPIC,
        "strengths": [TaskType.CODING, TaskType.REASONING],
        "context_window": 200000,
        "cost_per_1k_tokens": 0.003,
    },
    "gemini-2.0-flash": {
        "provider": ModelProvider.GOOGLE,
        "strengths": [TaskType.LONG_CONTEXT, TaskType.FAST],
        "context_window": 1000000,
        "cost_per_1k_tokens": 0.001,
    },
    "deepseek-chat": {
        "provider": ModelProvider.DEEPSEEK,
        "strengths": [TaskType.CODING, TaskType.REASONING, TaskType.COST_SENSITIVE],
        "context_window": 64000,
        "cost_per_1k_tokens": 0.0001,
    },
}


class ModelRouter:
    """Intelligent multi-model router"""

    def __init__(self):
        self.models = MODEL_CONFIGS
        self.usage_stats: Dict[str, int] = {}

    def select_model(
        self,
        task_type: TaskType,
        context_length: Optional[int] = None,
        priority: str = "balanced",
    ) -> str:
        """Select optimal model based on task type and constraints"""

        candidates = []

        for model_name, config in self.models.items():
            if task_type in config["strengths"]:
                if context_length and context_length > config["context_window"]:
                    continue
                candidates.append((model_name, config))

        if not candidates:
            candidates = list(self.models.items())

        if priority == "cost":
            candidates.sort(key=lambda x: x[1]["cost_per_1k_tokens"])
        elif priority == "quality":
            candidates.sort(key=lambda x: x[1]["cost_per_1k_tokens"], reverse=True)
        elif priority == "balanced":
            candidates.sort(key=lambda x: (
                x[1]["cost_per_1k_tokens"] * 0.5,
                -x[1]["context_window"] * 0.5
            ))

        selected_model = candidates[0][0]

        logger.info(
            "Model selected",
            model=selected_model,
            task_type=task_type,
            priority=priority,
        )

        return selected_model

    async def complete(
        self,
        messages: List[Dict[str, str]],
        task_type: TaskType = TaskType.REASONING,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> Dict[str, Any]:
        """Complete a chat request with automatic model routing"""

        if not model:
            context_length = sum(len(m.get("content", "")) for m in messages)
            model = self.select_model(task_type, context_length)

        try:
            response = await acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            self.usage_stats[model] = self.usage_stats.get(model, 0) + 1

            logger.info(
                "Completion successful",
                model=model,
                tokens=response.usage.total_tokens if hasattr(response, 'usage') else None,
            )

            return {
                "model": model,
                "content": response.choices[0].message.content,
                "usage": response.usage.dict() if hasattr(response, 'usage') else None,
                "finish_reason": response.choices[0].finish_reason,
            }

        except Exception as e:
            logger.error("Completion failed", model=model, error=str(e))
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "total_requests": sum(self.usage_stats.values()),
            "by_model": self.usage_stats,
        }


router = ModelRouter()
