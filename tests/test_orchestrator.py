"""
Unit tests for the Orchestrator — the central dispatch layer of Krishi Mitr.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestOrchestrator:
    """Tests for the Orchestrator dispatch and routing logic."""

    def setup_method(self):
        from agents.base import AgentMemory
        AgentMemory._instance = None

    def _make_orchestrator(self):
        """Create an Orchestrator with mocked agent constructors."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=False):
            from orchestrator import Orchestrator
            orch = Orchestrator()
            orch.gemini = None  # Disable AI routing
            return orch

    # --- Registration & Lazy Init ---

    def test_agent_registry_has_all_agents(self):
        """Orchestrator should register all 6 agent names."""
        orch = self._make_orchestrator()
        expected = {"crop", "fertilizer", "disease", "yield", "sustainability", "irrigation"}
        assert set(orch.agents.keys()) == expected

    def test_agents_start_as_none(self):
        """All agents should be None (lazy-loaded) initially."""
        orch = self._make_orchestrator()
        for name, agent in orch.agents.items():
            assert agent is None, f"Agent '{name}' should be None before first dispatch"

    # --- get_agent ---

    def test_get_agent_raises_on_unknown(self):
        """get_agent should raise ValueError for unknown agent names."""
        orch = self._make_orchestrator()
        with pytest.raises(ValueError, match="Unknown agent"):
            orch.get_agent("weather")

    @patch('orchestrator.CropAgent')
    def test_get_agent_lazy_initializes(self, MockCrop):
        """get_agent should create the agent on first call."""
        MockCrop.return_value = MagicMock()
        orch = self._make_orchestrator()
        agent = orch.get_agent("crop")
        assert agent is not None
        MockCrop.assert_called_once()

    @patch('orchestrator.CropAgent')
    def test_get_agent_returns_same_instance(self, MockCrop):
        """get_agent should return the same instance on subsequent calls."""
        MockCrop.return_value = MagicMock()
        orch = self._make_orchestrator()
        agent1 = orch.get_agent("crop")
        agent2 = orch.get_agent("crop")
        assert agent1 is agent2
        MockCrop.assert_called_once()  # Only created once

    # --- dispatch ---

    @patch('orchestrator.CropAgent')
    def test_dispatch_calls_agent_run(self, MockCrop):
        """dispatch should call the agent's run() method with the payload."""
        mock_agent = MagicMock()
        mock_agent.run.return_value = {"status": "ok", "primary_agent": "crop"}
        MockCrop.return_value = mock_agent

        orch = self._make_orchestrator()
        payload = {"nitrogen": 90, "phosphorous": 42}
        result = orch.dispatch("crop", payload)

        mock_agent.run.assert_called_once_with(payload)
        assert result["status"] == "ok"

    def test_dispatch_handles_unknown_agent_gracefully(self):
        """dispatch should return error dict for unknown agent names."""
        orch = self._make_orchestrator()
        result = orch.dispatch("weather", {"temp": 30})
        assert result["status"] == "error"
        assert "Orchestration failure" in result["message"]

    # --- smart_dispatch ---

    def test_smart_dispatch_without_gemini(self):
        """smart_dispatch should return error when Gemini is not configured."""
        orch = self._make_orchestrator()
        orch.gemini = None
        result = orch.smart_dispatch("What crop should I grow?", {})
        assert result["status"] == "error"
        assert "API key" in result["message"]

    # --- auto_trigger ---

    @patch('orchestrator.CropAgent')
    @patch('orchestrator.FertilizerAgent')
    @patch('orchestrator.IrrigationAgent')
    def test_auto_trigger_chains_agents(self, MockIrr, MockFert, MockCrop):
        """auto_trigger should dispatch fertilizer and irrigation after crop."""
        mock_crop = MagicMock()
        mock_fert = MagicMock()
        mock_irr = MagicMock()
        mock_crop.run.return_value = {"status": "ok", "top_result": "rice"}
        mock_fert.run.return_value = {"status": "ok"}
        mock_irr.run.return_value = {"status": "ok"}
        MockCrop.return_value = mock_crop
        MockFert.return_value = mock_fert
        MockIrr.return_value = mock_irr

        orch = self._make_orchestrator()
        orch.auto_trigger(
            trigger_agent="crop",
            result={"status": "ok"},
            context={"nitrogen": 90, "temperature": 25}
        )

        # Both fert and irr should have been dispatched
        mock_fert.run.assert_called_once()
        mock_irr.run.assert_called_once()

    # --- full_analysis ---

    @patch('orchestrator.CropAgent')
    @patch('orchestrator.FertilizerAgent')
    @patch('orchestrator.IrrigationAgent')
    @patch('orchestrator.YieldAgent')
    @patch('orchestrator.SustainabilityAgent')
    def test_full_analysis_runs_pipeline(self, MockSust, MockYield, MockIrr, MockFert, MockCrop):
        """full_analysis should dispatch all 5 pipeline agents."""
        for MockAgent in [MockCrop, MockFert, MockIrr, MockYield, MockSust]:
            mock_instance = MagicMock()
            mock_instance.run.return_value = {"status": "ok"}
            MockAgent.return_value = mock_instance

        orch = self._make_orchestrator()
        result = orch.full_analysis({"nitrogen": 50})

        assert result["summary"] == "Full Agricultural Analysis"
        assert "crop" in result["agents"]
        assert "fertilizer" in result["agents"]
        assert "irrigation" in result["agents"]
        assert "yield" in result["agents"]
        assert "sustainability" in result["agents"]

    @patch('orchestrator.CropAgent')
    @patch('orchestrator.FertilizerAgent')
    @patch('orchestrator.IrrigationAgent')
    @patch('orchestrator.YieldAgent')
    @patch('orchestrator.SustainabilityAgent')
    def test_full_analysis_handles_agent_failure(self, MockSust, MockYield, MockIrr, MockFert, MockCrop):
        """full_analysis should capture agent errors without crashing the pipeline."""
        # Crop succeeds
        crop_mock = MagicMock()
        crop_mock.run.return_value = {"status": "ok"}
        MockCrop.return_value = crop_mock

        # Fertilizer fails
        fert_mock = MagicMock()
        fert_mock.run.side_effect = Exception("Model file missing")
        MockFert.return_value = fert_mock

        # Others succeed
        for M in [MockIrr, MockYield, MockSust]:
            m = MagicMock()
            m.run.return_value = {"status": "ok"}
            M.return_value = m

        orch = self._make_orchestrator()
        result = orch.full_analysis({"nitrogen": 50})

        # Pipeline should NOT crash; fertilizer should show error
        assert result["agents"]["crop"]["status"] == "ok"
        assert result["agents"]["fertilizer"]["status"] == "error"
        assert result["agents"]["irrigation"]["status"] == "ok"
