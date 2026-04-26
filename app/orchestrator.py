import os
import json
import threading
from google import genai
from typing import Any, Dict, Optional, List
from agents import (
    CropAgent, FertilizerAgent, DiseaseAgent, 
    YieldAgent, SustainabilityAgent, IrrigationAgent
)
from agents.base import AgentMemory

class Orchestrator:
    """
    The Central Intelligence of Krishi Mitr.
    Responsible for SMART routing and autonomous agent triggering.
    """
    
    def __init__(self):
        self.memory = AgentMemory()
        self.agents = {
            "crop": None,
            "fertilizer": None,
            "disease": None,
            "yield": None,
            "sustainability": None,
            "irrigation": None
        }
        
        # Configure AI Engine for Routing
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.gemini = genai.Client(api_key=api_key)
        else:
            self.gemini = None

    def get_agent(self, agent_name: str):
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        if self.agents[agent_name] is None:
            if agent_name == "crop": self.agents["crop"] = CropAgent()
            elif agent_name == "fertilizer": self.agents["fertilizer"] = FertilizerAgent()
            elif agent_name == "disease": self.agents["disease"] = DiseaseAgent()
            elif agent_name == "yield": self.agents["yield"] = YieldAgent()
            elif agent_name == "sustainability": self.agents["sustainability"] = SustainabilityAgent()
            elif agent_name == "irrigation": self.agents["irrigation"] = IrrigationAgent()
        
        return self.agents[agent_name]

    def dispatch(self, task: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Routes the task to the correct agent and handles auto-triggering."""
        try:
            agent = self.get_agent(task)
            result = agent.run(payload)
            
            # Post-execution Auto-triggering logic (Autonomous chaining)
            if task == "crop" and result.get("status") == "ok":
                # Run background chaining so UI response is not blocked.
                threading.Thread(
                    target=self._auto_trigger_async,
                    args=(task, result, payload),
                    daemon=True
                ).start()
            
            return result
        except Exception as e:
            return {
                "agent": task,
                "status": "error",
                "message": f"Orchestration failure: {str(e)}"
            }

    def _auto_trigger_async(self, trigger_agent: str, result: Dict[str, Any], context: Dict[str, Any]):
        try:
            self.auto_trigger(trigger_agent, result, context)
        except Exception as exc:
            print(f"[Orchestrator] Async auto-trigger failed: {exc}")

    def smart_dispatch(self, query: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Uses LLM to decide which agent(s) to call based on natural language."""
        if not self.gemini:
            return {"status": "error", "message": "AI Engine API key missing for smart routing."}
        
        prompt = f"""
        You are the Krishi Mitr Dispatcher. Given the user query: "{query}"
        And the available agents: crop, fertilizer, disease, yield, sustainability, irrigation.
        Decide which single agent is most relevant. Return ONLY the agent name in lowercase.
        If multiple are relevant, pick the most immediate one (e.g., 'crop' before 'fertilizer').
        """
        try:
            # Using updated genai SDK syntax
            response = self.gemini.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            chosen_agent = response.text.strip().lower()
            # Basic validation of chosen agent
            if chosen_agent not in self.agents:
                chosen_agent = "crop" # Default
            return self.dispatch(chosen_agent, payload)
        except Exception as e:
            print(f"[Orchestrator] Smart routing failed: {e}")
            return self.dispatch("crop", payload) # Direct fallback

    def auto_trigger(self, trigger_agent: str, result: Dict[str, Any], context: Dict[str, Any]):
        """Autonomous chaining: If Crop Agent finishes, trigger Fertilizer and Irrigation."""
        if trigger_agent == "crop":
            print(f"[Orchestrator] Auto-triggering Fertilizer and Irrigation agents...")
            
            # Recommended crop is now in memory
            # Run Fertilizer with updated context
            fert_payload = context.copy()
            # Ensure names match what agent expects
            if "N" not in fert_payload and "nitrogen" in fert_payload: fert_payload["N"] = fert_payload["nitrogen"]
            self.dispatch("fertilizer", fert_payload)
            
            # Run Irrigation
            irr_payload = context.copy()
            if "temp" not in irr_payload and "temperature" in irr_payload: irr_payload["temp"] = irr_payload["temperature"]
            self.dispatch("irrigation", irr_payload)

    def full_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the entire pipeline sequentially and returns all results."""
        self.memory.clear()
        all_results = {
            "summary": "Full Agricultural Analysis",
            "agents": {}
        }
        
        pipeline = ["crop", "fertilizer", "irrigation", "yield", "sustainability"]
        for agent_name in pipeline:
            try:
                all_results["agents"][agent_name] = self.dispatch(agent_name, payload)
            except Exception as e:
                all_results["agents"][agent_name] = {"status": "error", "message": str(e)}
                
        return all_results

