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
        "strengths": [TaskType.CODING, TaskType.CREATIVITY, TaskType.REASONING],
        "context_window": 128000,
        "cost_per_1k_input": 0.005,
        "cost_per_1k_output": 0.015,
    },
    "gpt-4o-mini": {
        "provider": ModelProvider.OPENAI,
        "strengths": [TaskType.FAST, TaskType.COST_SENSITIVE],
        "context_window": 128000,
        "cost_per_1k_input": 0.00015,
        "cost_per_1k_output": 0.0006,
    },
    "claude-3-5-sonnet": {
        "provider": ModelProvider.ANTHROPIC,
        "strengths": [TaskType.CODING, TaskType.REASONING, TaskType.LONG_CONTEXT, TaskType.CRITICAL],
        "context_window": 200000,
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.015,
    },
    "claude-3-opus": {
        "provider": ModelProvider.ANTHROPIC,
        "strengths": [TaskType.REASONING, TaskType.LONG_CONTEXT, TaskType.CRITICAL],
        "context_window": 200000,
        "cost_per_1k_input": 0.015,
        "cost_per_1k_output": 0.075,
    },
    "claude-3-sonnet": {
        "provider": ModelProvider.ANTHROPIC,
        "strengths": [TaskType.CODING, TaskType.REASONING],
        "context_window": 200000,
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.015,
    },
    "gemini-2.0-flash": {
        "provider": ModelProvider.GOOGLE,
        "strengths": [TaskType.LONG_CONTEXT, TaskType.FAST, TaskType.COST_SENSITIVE],
        "context_window": 1000000,
        "cost_per_1k_input": 0.000075,
        "cost_per_1k_output": 0.0003,
    },
    "deepseek-chat": {
        "provider": ModelProvider.DEEPSEEK,
        "strengths": [TaskType.CODING, TaskType.REASONING, TaskType.COST_SENSITIVE],
        "context_window": 64000,
        "cost_per_1k_input": 0.00014,
        "cost_per_1k_output": 0.00028,
    },
}

FALLBACK_MAPPING = {
    "claude-3-opus": "gpt-4o",
    "claude-3-5-sonnet": "gpt-4o",
    "gpt-4o": "claude-3-5-sonnet",
    "gpt-4o-mini": "gemini-2.0-flash",
    "gemini-2.0-flash": "gpt-4o-mini",
    "deepseek-chat": "gpt-4o-mini",
    "claude-3-sonnet": "claude-3-5-sonnet",
}


class ModelRouter:
    """Intelligent multi-model router with automatic fallback and cost tracking"""

    def __init__(self):
        self.models = MODEL_CONFIGS
        self.usage_stats: Dict[str, Dict[str, Any]] = {
            model: {
                "requests": 0,
                "failures": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0,
            }
            for model in self.models
        }

    def _record_stats(self, model: str, success: bool, input_tokens: int = 0, output_tokens: int = 0) -> None:
        stats = self.usage_stats.setdefault(model, {
            "requests": 0,
            "failures": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost": 0.0,
        })
        stats["requests"] += 1
        if not success:
            stats["failures"] += 1
            return

        stats["input_tokens"] += input_tokens
        stats["output_tokens"] += output_tokens

        config = self.models.get(model)
        if config:
            cost_input = config.get("cost_per_1k_input", config.get("cost_per_1k_tokens", 0.0))
            cost_output = config.get("cost_per_1k_output", config.get("cost_per_1k_tokens", 0.0))
            stats["cost"] += (input_tokens / 1000 * cost_input) + (output_tokens / 1000 * cost_output)
        else:
            stats["cost"] += (input_tokens + output_tokens) / 1000 * 0.002

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

        def get_model_cost(cfg: Dict[str, Any]) -> float:
            return float(cfg.get("cost_per_1k_input", cfg.get("cost_per_1k_tokens", 0.0)))

        if priority == "cost":
            candidates.sort(key=lambda x: get_model_cost(x[1]))
        elif priority == "quality":
            candidates.sort(key=lambda x: get_model_cost(x[1]), reverse=True)
        elif priority == "balanced":
            candidates.sort(key=lambda x: (
                get_model_cost(x[1]) * 0.5,
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
        """Complete a chat request with automatic model routing and fallback"""

        if not model:
            context_length = sum(len(m.get("content", "")) for m in messages)
            model = self.select_model(task_type, context_length)

        primary_model = model
        fallback_model = FALLBACK_MAPPING.get(primary_model)

        try:
            return await self._completion_attempt(
                model=primary_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        except Exception as e:
            logger.warning(
                "Primary model completion failed, attempting fallback",
                model=primary_model,
                fallback=fallback_model,
                error=str(e)
            )
            self._record_stats(primary_model, success=False)

            if not fallback_model:
                raise

            try:
                return await self._completion_attempt(
                    model=fallback_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            except Exception as fe:
                logger.error(
                    "Fallback model completion failed",
                    model=fallback_model,
                    error=str(fe)
                )
                self._record_stats(fallback_model, success=False)
                raise

    async def _completion_attempt(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> Dict[str, Any]:
        response = await acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        input_tokens = 0
        output_tokens = 0
        if hasattr(response, 'usage') and response.usage:
            usage = response.usage
            if isinstance(usage, dict):
                input_tokens = usage.get("prompt_tokens", 0)
                output_tokens = usage.get("completion_tokens", 0)
            else:
                input_tokens = getattr(usage, "prompt_tokens", 0)
                output_tokens = getattr(usage, "completion_tokens", 0)

        self._record_stats(
            model=model,
            success=True,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )

        logger.info(
            "Completion successful",
            model=model,
            tokens=input_tokens + output_tokens,
        )

        # Build clean dict representation for usage
        usage_dict = None
        if hasattr(response, 'usage') and response.usage:
            if hasattr(response.usage, 'dict'):
                usage_dict = response.usage.dict()
            elif isinstance(response.usage, dict):
                usage_dict = response.usage
            else:
                usage_dict = {
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                }

        return {
            "model": model,
            "content": response.choices[0].message.content,
            "usage": usage_dict,
            "finish_reason": response.choices[0].finish_reason,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        total_requests = sum(stats.get("requests", 0) for stats in self.usage_stats.values())
        total_cost = sum(stats.get("cost", 0.0) for stats in self.usage_stats.values())
        return {
            "total_requests": total_requests,
            "total_cost": total_cost,
            "by_model": self.usage_stats,
        }


router = ModelRouter()

