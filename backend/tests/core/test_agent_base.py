"""
Unit tests for BaseAgent.

Tests cover:
- Agent initialization
- Thinking and reasoning
- Reflection mechanism
- Tool registration and execution
- Message passing
- Execution logging
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.core.agent_base import (
    BaseAgent,
    ReasoningMode,
    AgentStatus,
    AgentMessage,
)


# ============================================================================
# Agent Initialization Tests
# ============================================================================

@pytest.mark.unit
class TestAgentInitialization:
    """Test agent initialization."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self, test_agent):
        """Test agent initializes with correct attributes."""
        assert test_agent.agent_id == "test-agent-001"
        assert test_agent.name == "Test Agent"
        assert test_agent.description == "Agent for testing"
        assert test_agent.reasoning_mode == ReasoningMode.FAST
        assert test_agent.status == AgentStatus.IDLE
        assert isinstance(test_agent.tools, dict)
        assert isinstance(test_agent.message_queue, list)
        assert isinstance(test_agent.execution_history, list)

    @pytest.mark.asyncio
    async def test_agent_with_different_reasoning_modes(self, mock_model_router, mock_memory_manager):
        """Test agent with different reasoning modes."""
        from tests.conftest import TestAgent
        
        for mode in ReasoningMode:
            agent = TestAgent(
                agent_id=f"agent-{mode.value}",
                name="Test",
                description="Test",
                model_router=mock_model_router,
                memory_manager=mock_memory_manager,
                reasoning_mode=mode,
            )
            assert agent.reasoning_mode == mode


# ============================================================================
# Thinking and Reasoning Tests
# ============================================================================

@pytest.mark.unit
class TestThinking:
    """Test agent thinking functionality."""

    @pytest.mark.asyncio
    async def test_think_basic(self, test_agent):
        """Test basic thinking operation."""
        test_agent.model_router.complete.return_value = {
            "content": "Thought response",
            "model": "gpt-4o",
        }
        
        result = await test_agent.think("Test prompt")
        
        assert result == "Thought response"
        assert test_agent.status == AgentStatus.THINKING
        test_agent.model_router.complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_think_with_context(self, test_agent):
        """Test thinking with context."""
        test_agent.model_router.complete.return_value = {
            "content": "Contextual response",
            "model": "gpt-4o",
        }
        
        context = {"key": "value"}
        result = await test_agent.think("Test prompt", context=context)
        
        assert result == "Contextual response"
        call_args = test_agent.model_router.complete.call_args
        messages = call_args[1]["messages"]
        assert any("Context:" in msg["content"] for msg in messages)

    @pytest.mark.asyncio
    async def test_think_stores_in_memory(self, test_agent):
        """Test thinking stores result in memory."""
        test_agent.model_router.complete.return_value = {
            "content": "Response",
            "model": "gpt-4o",
        }
        
        await test_agent.think("Test prompt")
        
        test_agent.memory_manager.store_short_term.assert_called_once()
        call_args = test_agent.memory_manager.store_short_term.call_args
        assert "agent:test-agent-001:last_thought" in call_args[0]

    @pytest.mark.asyncio
    async def test_think_uses_correct_temperature(self, test_agent):
        """Test thinking uses temperature based on reasoning mode."""
        test_agent.model_router.complete.return_value = {
            "content": "Response",
            "model": "gpt-4o",
        }
        
        await test_agent.think("Test prompt")
        
        call_args = test_agent.model_router.complete.call_args
        # FAST mode should use temperature 0.3
        assert call_args[1]["temperature"] == 0.3

    @pytest.mark.asyncio
    async def test_think_failure_raises_exception(self, test_agent):
        """Test thinking failure raises exception."""
        test_agent.model_router.complete.side_effect = Exception("Model error")
        
        with pytest.raises(Exception, match="Model error"):
            await test_agent.think("Test prompt")


# ============================================================================
# Reflection Tests
# ============================================================================

@pytest.mark.unit
class TestReflection:
    """Test agent reflection mechanism."""

    @pytest.mark.asyncio
    async def test_reflect_on_output(self, test_agent):
        """Test reflection on output."""
        test_agent.model_router.complete.return_value = {
            "content": "Quality analysis",
            "model": "gpt-4o",
        }
        
        result = await test_agent.reflect("Test output")
        
        assert result["original_output"] == "Test output"
        assert result["reflection"] == "Quality analysis"
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_reflect_calls_think(self, test_agent):
        """Test reflection uses think method."""
        test_agent.model_router.complete.return_value = {
            "content": "Analysis",
            "model": "gpt-4o",
        }
        
        await test_agent.reflect("Output")
        
        test_agent.model_router.complete.assert_called_once()
        call_args = test_agent.model_router.complete.call_args
        messages = call_args[1]["messages"]
        assert any("Analyze this output" in msg["content"] for msg in messages)


# ============================================================================
# Tool Management Tests
# ============================================================================

@pytest.mark.unit
class TestToolManagement:
    """Test tool registration and execution."""

    @pytest.mark.asyncio
    async def test_register_tool(self, test_agent):
        """Test tool registration."""
        async def test_tool(arg1, arg2):
            return arg1 + arg2
        
        test_agent.register_tool("add", test_tool)
        
        assert "add" in test_agent.tools
        assert test_agent.tools["add"] == test_tool

    @pytest.mark.asyncio
    async def test_use_tool_success(self, test_agent):
        """Test successful tool execution."""
        async def test_tool(value):
            return value * 2
        
        test_agent.register_tool("double", test_tool)
        result = await test_agent.use_tool("double", value=5)
        
        assert result == 10

    @pytest.mark.asyncio
    async def test_use_tool_not_found(self, test_agent):
        """Test using non-existent tool raises error."""
        with pytest.raises(ValueError, match="Tool nonexistent not found"):
            await test_agent.use_tool("nonexistent")

    @pytest.mark.asyncio
    async def test_use_tool_execution_failure(self, test_agent):
        """Test tool execution failure raises exception."""
        async def failing_tool():
            raise Exception("Tool failed")
        
        test_agent.register_tool("fail", failing_tool)
        
        with pytest.raises(Exception, match="Tool failed"):
            await test_agent.use_tool("fail")


# ============================================================================
# Message Passing Tests
# ============================================================================

@pytest.mark.unit
class TestMessagePassing:
    """Test agent message passing."""

    @pytest.mark.asyncio
    async def test_send_message(self, test_agent):
        """Test sending message to another agent."""
        await test_agent.send_message("agent-002", "Hello", "greeting")
        
        assert len(test_agent.message_queue) == 1
        message = test_agent.message_queue[0]
        assert message.sender == "test-agent-001"
        assert message.recipient == "agent-002"
        assert message.content == "Hello"
        assert message.message_type == "greeting"

    @pytest.mark.asyncio
    async def test_receive_messages(self, test_agent):
        """Test receiving messages."""
        # Add messages to queue
        msg1 = AgentMessage(
            sender="agent-002",
            recipient="test-agent-001",
            content="Message 1",
            message_type="task",
            timestamp=datetime.utcnow(),
        )
        msg2 = AgentMessage(
            sender="agent-003",
            recipient="test-agent-001",
            content="Message 2",
            message_type="task",
            timestamp=datetime.utcnow(),
        )
        test_agent.message_queue.extend([msg1, msg2])
        
        messages = await test_agent.receive_messages()
        
        assert len(messages) == 2
        assert messages[0].content == "Message 1"
        assert messages[1].content == "Message 2"
        assert len(test_agent.message_queue) == 0

    @pytest.mark.asyncio
    async def test_receive_messages_filters_by_recipient(self, test_agent):
        """Test receiving only messages for this agent."""
        msg1 = AgentMessage(
            sender="agent-002",
            recipient="test-agent-001",
            content="For me",
            message_type="task",
            timestamp=datetime.utcnow(),
        )
        msg2 = AgentMessage(
            sender="agent-003",
            recipient="other-agent",
            content="Not for me",
            message_type="task",
            timestamp=datetime.utcnow(),
        )
        test_agent.message_queue.extend([msg1, msg2])
        
        messages = await test_agent.receive_messages()
        
        assert len(messages) == 1
        assert messages[0].content == "For me"
        assert len(test_agent.message_queue) == 1  # Other message remains


# ============================================================================
# Execution Logging Tests
# ============================================================================

@pytest.mark.unit
class TestExecutionLogging:
    """Test execution logging."""

    @pytest.mark.asyncio
    async def test_log_execution(self, test_agent):
        """Test logging execution."""
        task = {"action": "test"}
        result = {"status": "success"}
        
        await test_agent.log_execution(task, result)
        
        assert len(test_agent.execution_history) == 1
        entry = test_agent.execution_history[0]
        assert entry["agent_id"] == "test-agent-001"
        assert entry["task"] == task
        assert entry["result"] == result
        assert "timestamp" in entry

    @pytest.mark.asyncio
    async def test_log_execution_stores_in_memory(self, test_agent):
        """Test execution log stored in episodic memory."""
        task = {"action": "test"}
        result = {"status": "success"}
        
        await test_agent.log_execution(task, result)
        
        test_agent.memory_manager.store_episodic.assert_called_once()


# ============================================================================
# System Prompt and Configuration Tests
# ============================================================================

@pytest.mark.unit
class TestSystemConfiguration:
    """Test system prompt and configuration."""

    def test_get_system_prompt(self, test_agent):
        """Test system prompt generation."""
        prompt = test_agent.get_system_prompt()
        
        assert "Test Agent" in prompt
        assert "Agent for testing" in prompt
        assert "fast" in prompt.lower()

    def test_get_temperature_for_reasoning_modes(self, mock_model_router, mock_memory_manager):
        """Test temperature varies by reasoning mode."""
        from tests.conftest import TestAgent
        
        expected_temps = {
            ReasoningMode.FAST: 0.3,
            ReasoningMode.DEEP: 0.7,
            ReasoningMode.STRATEGIC: 0.5,
            ReasoningMode.CREATOR: 0.9,
            ReasoningMode.ARCHITECT: 0.6,
        }
        
        for mode, expected_temp in expected_temps.items():
            agent = TestAgent(
                agent_id="test",
                name="Test",
                description="Test",
                model_router=mock_model_router,
                memory_manager=mock_memory_manager,
                reasoning_mode=mode,
            )
            assert agent.get_temperature() == expected_temp
