import os
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from google import genai

class AgentMemory:
    """
    Shared memory system for all Krishi Mitr agents.
    Allows agents to store and retrieve contextual information.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentMemory, cls).__new__(cls)
            cls._instance.data = {}
        return cls._instance

    def set(self, key: str, value: Any):
        self.data[key] = value

    def get(self, key: str, default: Any = None):
        return self.data.get(key, default)

    def clear(self):
        self.data = {}

    def get_all(self):
        return self.data

class BaseAgent(ABC):
    """
    Abstract Base Class for all Krishi Mitr Agents.
    Implements the TRUE Agentic Loop: PLAN -> ACT -> OBSERVE -> REFLECT.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.memory = AgentMemory()
        
        # Configure Advanced AI
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.gemini = genai.Client(api_key=api_key)
        else:
            self.gemini = None

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the agent's logic through a structured agentic loop.
        """
        print(f"\n[Agent: {self.name}] Starting Agentic Loop...")
        
        # 1. PLAN
        plan_obj = self._plan(payload)
        print(f"[Agent: {self.name}] PLAN: {plan_obj.get('goal', 'No goal')}")

        # 2. ACT
        action_result = self._act(payload)
        print(f"[Agent: {self.name}] ACT: Execution completed.")

        # 3. OBSERVE
        observation_obj = self._observe(action_result)
        print(f"[Agent: {self.name}] OBSERVE: {observation_obj.get('quality', 'Processed')}")

        # 4. REFLECT
        reflection_obj = self._reflect(payload, action_result, observation_obj)
        print(f"[Agent: {self.name}] REFLECT: {reflection_obj.get('explanation', '')[:50]}...")

        return self.format_response(
            action_result=action_result,
            plan=plan_obj,
            observation=observation_obj,
            reflection=reflection_obj
        )

    @abstractmethod
    def _plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze input and determine the strategy. Returns a dict."""
        pass

    @abstractmethod
    def _act(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the core logic or model prediction. Returns a dict."""
        pass

    @abstractmethod
    def _observe(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the results of the action. Returns a dict."""
        pass

    @abstractmethod
    def _reflect(self, payload: Dict[str, Any], result: Dict[str, Any], observation: Dict[str, Any]) -> Dict[str, Any]:
        """Reason about the outcome and update shared memory. Returns a dict."""
        pass

    def _ask_llm(self, prompt: str, fallback: str) -> str:
        """Utility to ask AI Engine for reasoning."""
        if not self.gemini:
            return fallback
        try:
            response = self.gemini.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"LLM Error in {self.name}: {e}")
            return fallback

    def format_response(self, action_result: Dict[str, Any], plan: Dict[str, Any], observation: Dict[str, Any], reflection: Dict[str, Any]) -> Dict[str, Any]:
        """Standardizes the output format according to Step 3 requirements."""
        
        # Determine top result from action_result or reflection
        top_result = action_result.get("top_result") or reflection.get("top_result") or "N/A"
        confidence = action_result.get("confidence") or 85.0
        model_used = action_result.get("model_used") or "AI Model"

        response = {
            "primary_agent": self.name,
            "result": {
                "agent": self.name.replace("_", " ").title(),
                "agentic_loop": {
                    "plan": {
                        "goal": plan.get("goal", "Analyzing data"),
                        "steps": plan.get("steps", [])
                    },
                    "prediction": {
                        "top_result": top_result,
                        "confidence": confidence,
                        "model_used": model_used
                    },
                    "observations": {
                        "quality": observation.get("quality", "high"),
                        "anomalies": observation.get("anomalies", [])
                    },
                    "reflection": {
                        "explanation": reflection.get("explanation", ""),
                        "key_factors": reflection.get("key_factors", []),
                        "immediate_actions": reflection.get("immediate_actions", []),
                        "warnings": reflection.get("warnings", []),
                        "should_consult_agents": reflection.get("should_consult_agents", [])
                    }
                },
                "summary": {
                    "top_result": top_result,
                    "confidence": confidence,
                    "explanation": reflection.get("explanation", ""),
                    "immediate_actions": reflection.get("immediate_actions", []),
                    "warnings": reflection.get("warnings", [])
                },
                "execution_log": [],
                "triggers": []
            },
            "status": "ok" if "error" not in action_result else "error",
            "auto_triggered": {},
            "execution_timeline": []
        }

        # Merge any extra keys from action_result into result
        for key, value in action_result.items():
            if key not in ["top_result", "confidence", "model_used", "error", "reason"]:
                response["result"][key] = value

        return response

