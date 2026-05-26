"""
Unit tests for ModelRouter.

Tests cover:
- Model selection logic
- Fallback mechanisms
- Usage statistics tracking
- Cost calculations
- Completion with mocking
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.model_router import (
    ModelRouter,
    TaskType,
    ModelProvider,
    MODEL_CONFIGS,
    FALLBACK_MAPPING,
)


# ============================================================================
# Model Selection Tests
# ============================================================================

@pytest.mark.unit
class TestModelSelection:
    """Test model selection logic."""

    def test_select_model_for_coding_task(self, model_router):
        """Test model selection for coding tasks."""
        model = model_router.select_model(TaskType.CODING)
        config = MODEL_CONFIGS[model]
        assert TaskType.CODING in config["strengths"]

    def test_select_model_for_reasoning_task(self, model_router):
        """Test model selection for reasoning tasks."""
        model = model_router.select_model(TaskType.REASONING)
        config = MODEL_CONFIGS[model]
        assert TaskType.REASONING in config["strengths"]

    def test_select_model_for_creativity_task(self, model_router):
        """Test model selection for creativity tasks."""
        model = model_router.select_model(TaskType.CREATIVITY)
        config = MODEL_CONFIGS[model]
        assert TaskType.CREATIVITY in config["strengths"]

    def test_select_model_with_context_length_constraint(self, model_router):
        """Test model selection respects context length."""
        model = model_router.select_model(
            TaskType.LONG_CONTEXT,
            context_length=500000,
        )
        config = MODEL_CONFIGS[model]
        assert config["context_window"] >= 500000

    def test_select_model_cost_priority(self, model_router):
        """Test model selection with cost priority."""
        model = model_router.select_model(
            TaskType.FAST,
            priority="cost",
        )
        # Should select cheapest model
        assert model in ["gpt-4o-mini", "gemini-2.0-flash", "deepseek-chat"]

    def test_select_model_quality_priority(self, model_router):
        """Test model selection with quality priority."""
        model = model_router.select_model(
            TaskType.CRITICAL,
            priority="quality",
        )
        # Should select premium model
        assert model in ["claude-3-opus", "claude-3-5-sonnet", "gpt-4o"]

    def test_select_model_balanced_priority(self, model_router):
        """Test model selection with balanced priority."""
        model = model_router.select_model(
            TaskType.REASONING,
            priority="balanced",
        )
        # Should select mid-tier model
        assert model in MODEL_CONFIGS

    def test_select_model_fallback_when_no_match(self, model_router):
        """Test fallback when no model matches criteria."""
        # Request impossible context length
        model = model_router.select_model(
            TaskType.CODING,
            context_length=10000000,  # Impossibly large
        )
        # Should still return a model (fallback to any available)
        assert model in MODEL_CONFIGS


# ============================================================================
# Fallback Mechanism Tests
# ============================================================================

@pytest.mark.unit
class TestFallbackMechanism:
    """Test model fallback logic."""

    @pytest.mark.asyncio
    async def test_fallback_on_primary_failure(self, model_router, mock_litellm_completion):
        """Test fallback to secondary model on primary failure."""
        with patch("app.core.model_router.acompletion") as mock_completion:
            # First call fails, second succeeds
            mock_completion.side_effect = [
                Exception("Primary model failed"),
                mock_litellm_completion,
            ]

            result = await model_router.complete(
                messages=[{"role": "user", "content": "test"}],
                model="claude-3-opus",
            )

            assert result["model"] == "gpt-4o"  # Fallback model
            assert result["content"] == "Test AI response"
            assert mock_completion.call_count == 2

    @pytest.mark.asyncio
    async def test_no_fallback_when_primary_succeeds(self, model_router, mock_litellm_completion):
        """Test no fallback when primary model succeeds."""
        with patch("app.core.model_router.acompletion", return_value=mock_litellm_completion):
            result = await model_router.complete(
                messages=[{"role": "user", "content": "test"}],
                model="gpt-4o",
            )

            assert result["model"] == "gpt-4o"
            assert result["content"] == "Test AI response"

    @pytest.mark.asyncio
    async def test_raises_when_both_models_fail(self, model_router):
        """Test exception raised when both primary and fallback fail."""
        with patch("app.core.model_router.acompletion") as mock_completion:
            mock_completion.side_effect = Exception("All models failed")

            with pytest.raises(Exception, match="All models failed"):
                await model_router.complete(
                    messages=[{"role": "user", "content": "test"}],
                    model="claude-3-opus",
                )

    @pytest.mark.asyncio
    async def test_no_fallback_for_model_without_mapping(self, model_router):
        """Test behavior when model has no fallback mapping."""
        with patch("app.core.model_router.acompletion") as mock_completion:
            mock_completion.side_effect = Exception("Model failed")

            # Use a model not in FALLBACK_MAPPING
            with pytest.raises(Exception):
                await model_router.complete(
                    messages=[{"role": "user", "content": "test"}],
                    model="non-existent-model",
                )


# ============================================================================
# Usage Statistics Tests
# ============================================================================

@pytest.mark.unit
class TestUsageStatistics:
    """Test usage statistics tracking."""

    def test_initial_stats_are_zero(self, model_router):
        """Test initial statistics are zero."""
        stats = model_router.get_stats()
        assert stats["total_requests"] == 0
        assert stats["total_cost"] == 0.0
        assert isinstance(stats["by_model"], dict)

    @pytest.mark.asyncio
    async def test_stats_updated_on_success(self, model_router, mock_litellm_completion):
        """Test statistics updated on successful completion."""
        with patch("app.core.model_router.acompletion", return_value=mock_litellm_completion):
            await model_router.complete(
                messages=[{"role": "user", "content": "test"}],
                model="gpt-4o",
            )

            stats = model_router.get_stats()
            assert stats["total_requests"] == 1
            assert stats["total_cost"] > 0
            assert stats["by_model"]["gpt-4o"]["requests"] == 1
            assert stats["by_model"]["gpt-4o"]["failures"] == 0

    @pytest.mark.asyncio
    async def test_stats_updated_on_failure(self, model_router):
        """Test statistics updated on failure."""
        with patch("app.core.model_router.acompletion") as mock_completion:
            mock_completion.side_effect = [
                Exception("Failed"),
                Exception("Failed again"),
            ]

            try:
                await model_router.complete(
                    messages=[{"role": "user", "content": "test"}],
                    model="gpt-4o",
                )
            except Exception:
                pass

            stats = model_router.get_stats()
            assert stats["by_model"]["gpt-4o"]["failures"] > 0

    @pytest.mark.asyncio
    async def test_token_usage_tracked(self, model_router, mock_litellm_completion):
        """Test token usage is tracked correctly."""
        with patch("app.core.model_router.acompletion", return_value=mock_litellm_completion):
            await model_router.complete(
                messages=[{"role": "user", "content": "test"}],
                model="gpt-4o",
            )

            stats = model_router.get_stats()
            model_stats = stats["by_model"]["gpt-4o"]
            assert model_stats["input_tokens"] == 10
            assert model_stats["output_tokens"] == 20


# ============================================================================
# Cost Calculation Tests
# ============================================================================

@pytest.mark.unit
class TestCostCalculation:
    """Test cost calculation logic."""

    @pytest.mark.asyncio
    async def test_cost_calculated_correctly(self, model_router, mock_litellm_completion):
        """Test cost is calculated correctly based on token usage."""
        with patch("app.core.model_router.acompletion", return_value=mock_litellm_completion):
            await model_router.complete(
                messages=[{"role": "user", "content": "test"}],
                model="gpt-4o",
            )

            stats = model_router.get_stats()
            expected_cost = (10 / 1000 * 0.005) + (20 / 1000 * 0.015)
            assert abs(stats["total_cost"] - expected_cost) < 0.0001

    @pytest.mark.asyncio
    async def test_cost_accumulates_across_requests(self, model_router, mock_litellm_completion):
        """Test cost accumulates across multiple requests."""
        with patch("app.core.model_router.acompletion", return_value=mock_litellm_completion):
            # Make 3 requests
            for _ in range(3):
                await model_router.complete(
                    messages=[{"role": "user", "content": "test"}],
                    model="gpt-4o",
                )

            stats = model_router.get_stats()
            expected_cost = 3 * ((10 / 1000 * 0.005) + (20 / 1000 * 0.015))
            assert abs(stats["total_cost"] - expected_cost) < 0.0001


# ============================================================================
# Completion Tests
# ============================================================================

@pytest.mark.unit
class TestCompletion:
    """Test completion functionality."""

    @pytest.mark.asyncio
    async def test_complete_with_explicit_model(self, model_router, mock_litellm_completion):
        """Test completion with explicitly specified model."""
        with patch("app.core.model_router.acompletion", return_value=mock_litellm_completion):
            result = await model_router.complete(
                messages=[{"role": "user", "content": "test"}],
                model="gpt-4o",
            )

            assert result["model"] == "gpt-4o"
            assert result["content"] == "Test AI response"
            assert result["finish_reason"] == "stop"

    @pytest.mark.asyncio
    async def test_complete_with_auto_model_selection(self, model_router, mock_litellm_completion):
        """Test completion with automatic model selection."""
        with patch("app.core.model_router.acompletion", return_value=mock_litellm_completion):
            result = await model_router.complete(
                messages=[{"role": "user", "content": "test"}],
                task_type=TaskType.CODING,
            )

            assert result["model"] in MODEL_CONFIGS
            assert result["content"] == "Test AI response"

    @pytest.mark.asyncio
    async def test_complete_with_temperature(self, model_router, mock_litellm_completion):
        """Test completion respects temperature parameter."""
        with patch("app.core.model_router.acompletion", return_value=mock_litellm_completion) as mock:
            await model_router.complete(
                messages=[{"role": "user", "content": "test"}],
                model="gpt-4o",
                temperature=0.9,
            )

            # Verify temperature was passed to acompletion
            call_kwargs = mock.call_args[1]
            assert call_kwargs["temperature"] == 0.9

    @pytest.mark.asyncio
    async def test_complete_with_max_tokens(self, model_router, mock_litellm_completion):
        """Test completion respects max_tokens parameter."""
        with patch("app.core.model_router.acompletion", return_value=mock_litellm_completion) as mock:
            await model_router.complete(
                messages=[{"role": "user", "content": "test"}],
                model="gpt-4o",
                max_tokens=2000,
            )

            # Verify max_tokens was passed to acompletion
            call_kwargs = mock.call_args[1]
            assert call_kwargs["max_tokens"] == 2000
