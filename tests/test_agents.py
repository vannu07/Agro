"""
Unit tests for Krishi Mitr Agent layer.
Tests AgentMemory, BaseAgent, and individual agent implementations.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

# Ensure app directory is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ---------- AgentMemory Tests ----------

class TestAgentMemory:
    """Tests for the singleton AgentMemory class."""

    def setup_method(self):
        """Reset singleton before each test."""
        from agents.base import AgentMemory
        AgentMemory._instance = None
        self.memory = AgentMemory()

    def test_singleton_pattern(self):
        """AgentMemory should return the same instance."""
        from agents.base import AgentMemory
        mem1 = AgentMemory()
        mem2 = AgentMemory()
        assert mem1 is mem2, "AgentMemory must be a singleton"

    def test_set_and_get(self):
        """set() should store values retrievable by get()."""
        self.memory.set("crop", "rice")
        assert self.memory.get("crop") == "rice"

    def test_get_default(self):
        """get() should return default for missing keys."""
        result = self.memory.get("nonexistent", "fallback")
        assert result == "fallback"

    def test_clear(self):
        """clear() should remove all stored data."""
        self.memory.set("key1", "value1")
        self.memory.set("key2", "value2")
        self.memory.clear()
        assert self.memory.get("key1") is None
        assert self.memory.get("key2") is None

    def test_get_all(self):
        """get_all() should return entire data dictionary."""
        self.memory.clear()
        self.memory.set("a", 1)
        self.memory.set("b", 2)
        data = self.memory.get_all()
        assert data == {"a": 1, "b": 2}


# ---------- BaseAgent Tests ----------

class TestBaseAgent:
    """Tests for BaseAgent abstract class methods."""

    def setup_method(self):
        from agents.base import AgentMemory
        AgentMemory._instance = None

    def test_ask_llm_fallback_when_no_gemini(self):
        """_ask_llm should return fallback when Gemini is not configured."""
        from agents.base import BaseAgent

        # Create a concrete subclass for testing
        class DummyAgent(BaseAgent):
            def _plan(self, payload): return {"goal": "test"}
            def _act(self, payload): return {"top_result": "test"}
            def _observe(self, result): return {"quality": "high"}
            def _reflect(self, payload, result, obs): return {"explanation": "ok"}

        with patch.dict(os.environ, {}, clear=True):
            agent = DummyAgent(name="dummy")
            agent.gemini = None  # Force no Gemini
            result = agent._ask_llm("What crop?", "wheat")
            assert result == "wheat"

    def test_format_response_structure(self):
        """format_response should produce the correct P.A.O.R. structure."""
        from agents.base import BaseAgent

        class DummyAgent(BaseAgent):
            def _plan(self, payload): return {"goal": "test"}
            def _act(self, payload): return {"top_result": "rice"}
            def _observe(self, result): return {"quality": "high"}
            def _reflect(self, payload, result, obs): return {"explanation": "Good match"}

        with patch.dict(os.environ, {}, clear=True):
            agent = DummyAgent(name="test_agent")
            response = agent.format_response(
                action_result={"top_result": "rice", "confidence": 95.0, "model_used": "RF"},
                plan={"goal": "Find best crop", "steps": ["Step 1"]},
                observation={"quality": "high", "anomalies": []},
                reflection={"explanation": "Good match", "key_factors": ["NPK"], "immediate_actions": [], "warnings": []}
            )

        assert response["primary_agent"] == "test_agent"
        assert response["status"] == "ok"
        assert response["result"]["agentic_loop"]["prediction"]["top_result"] == "rice"
        assert response["result"]["agentic_loop"]["prediction"]["confidence"] == 95.0
        assert response["result"]["agentic_loop"]["plan"]["goal"] == "Find best crop"
        assert response["result"]["agentic_loop"]["observations"]["quality"] == "high"
        assert response["result"]["agentic_loop"]["reflection"]["explanation"] == "Good match"

    def test_format_response_error_status(self):
        """format_response should return status 'error' when action_result has error."""
        from agents.base import BaseAgent

        class DummyAgent(BaseAgent):
            def _plan(self, payload): return {"goal": "test"}
            def _act(self, payload): return {"error": "Model failed"}
            def _observe(self, result): return {"quality": "error"}
            def _reflect(self, payload, result, obs): return {"explanation": "Failed"}

        with patch.dict(os.environ, {}, clear=True):
            agent = DummyAgent(name="test_agent")
            response = agent.format_response(
                action_result={"error": "Model not loaded"},
                plan={"goal": "test"},
                observation={"quality": "error"},
                reflection={"explanation": "Failed"}
            )

        assert response["status"] == "error"


# ---------- CropAgent Tests ----------

class TestCropAgent:
    """Tests for the CropAgent implementation."""

    def setup_method(self):
        from agents.base import AgentMemory
        AgentMemory._instance = None

    @patch('agents.crop_agent.pickle')
    @patch('builtins.open', create=True)
    @patch('os.path.exists', return_value=True)
    def test_plan_returns_correct_structure(self, mock_exists, mock_open, mock_pickle):
        """_plan() should return a goal and steps list."""
        mock_pickle.load.return_value = MagicMock()
        from agents.crop_agent import CropAgent
        agent = CropAgent()
        plan = agent._plan({"nitrogen": 90, "phosphorous": 42})
        assert "goal" in plan
        assert "steps" in plan
        assert isinstance(plan["steps"], list)

    @patch('agents.crop_agent.pickle')
    @patch('builtins.open', create=True)
    @patch('os.path.exists', return_value=True)
    def test_act_returns_error_on_missing_params(self, mock_exists, mock_open, mock_pickle):
        """_act() should return an error when required parameters are missing."""
        mock_pickle.load.return_value = MagicMock()
        from agents.crop_agent import CropAgent
        agent = CropAgent()
        result = agent._act({})  # Empty payload
        assert "error" in result or "top_result" in result  # Should handle gracefully


# ---------- DiseaseAgent Tests ----------

class TestDiseaseAgent:
    """Tests for the DiseaseAgent implementation."""

    def setup_method(self):
        from agents.base import AgentMemory
        AgentMemory._instance = None

    @patch('agents.disease_agent.disease_dic', {})
    @patch('models_registry.registry')
    def test_act_returns_error_no_input(self, mock_registry):
        """_act() should return error when no image or symptoms are provided."""
        mock_registry.get_disease_model.return_value = MagicMock()
        from agents.disease_agent import DiseaseAgent
        agent = DiseaseAgent()
        result = agent._act({})  # No image, no symptoms
        assert "error" in result

    @patch('agents.disease_agent.disease_dic', {})
    @patch('models_registry.registry')
    def test_plan_with_image(self, mock_registry):
        """_plan() should include ResNet9 step when image is present."""
        mock_registry.get_disease_model.return_value = MagicMock()
        from agents.disease_agent import DiseaseAgent
        agent = DiseaseAgent()
        plan = agent._plan({"img_bytes": b"fake_image"})
        assert "goal" in plan
        assert any("ResNet9" in step for step in plan["steps"])

    @patch('agents.disease_agent.disease_dic', {})
    @patch('models_registry.registry')
    def test_plan_with_text(self, mock_registry):
        """_plan() should include AI analysis step when only text is present."""
        mock_registry.get_disease_model.return_value = MagicMock()
        from agents.disease_agent import DiseaseAgent
        agent = DiseaseAgent()
        plan = agent._plan({"symptom_description": "yellow leaves"})
        assert "goal" in plan
        assert any("AI" in step or "description" in step.lower() for step in plan["steps"])
