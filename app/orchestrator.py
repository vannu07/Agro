"""
Orchestrator Module

Routes requests to appropriate agents and coordinates multi-agent workflows.
Enables unified access to all AI agents in the Krishi Mitr system.
"""

from typing import Dict, Any, Callable
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Central coordinator for all AI agents in Krishi Mitr.
    Routes requests to the appropriate agent based on type.
    """
    
    def __init__(self):
        """Initialize the orchestrator with agent registry"""
        self.agents = {}
        self._register_agents()
    
    def _register_agents(self):
        """Register all available agents"""
        # Import agents as they're needed
        try:
            # Import agent functions from app.py context
            # These will be injected when app.py imports orchestrator
            logger.info("[Orchestrator] Agent registry ready for population")
        except Exception as e:
            logger.warning(f"[Orchestrator] Initial setup: {e}")
    
    def register_agent(self, agent_name: str, agent_func: Callable):
        """
        Register a new agent
        
        Args:
            agent_name: Name of the agent (crop, disease, fertilizer, etc.)
            agent_func: Agent function that processes requests
        """
        self.agents[agent_name] = agent_func
        logger.info(f"[Orchestrator] Registered agent: {agent_name}")
    
    def dispatch(self, agent_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch a request to the appropriate agent
        
        Args:
            agent_name: Name of the agent to call
            payload: Request payload with parameters
        
        Returns:
            Agent response with status, data, and message
        """
        logger.info(f"[Orchestrator] Dispatching to {agent_name} with payload keys: {list(payload.keys())}")
        
        # Get agent function - agents are injected by app.py
        agent_func = self.agents.get(agent_name)
        
        if agent_func is None:
            # Fallback: try to call agent directly by name
            # This handles cases where agents are defined but not explicitly registered
            return self._fallback_dispatch(agent_name, payload)
        
        try:
            result = agent_func(payload)
            logger.info(f"[Orchestrator] Agent {agent_name} returned status: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"[Orchestrator] Error in agent {agent_name}: {e}")
            return {
                "agent": agent_name,
                "status": "error",
                "data": {},
                "message": f"Agent error: {str(e)}"
            }
    
    def _fallback_dispatch(self, agent_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback dispatch when agent isn't explicitly registered.
        Tries to infer agent behavior from payload.
        """
        logger.warning(f"[Orchestrator] Agent {agent_name} not registered, using fallback")
        
        # Import required functions dynamically
        try:
            if agent_name == "crop":
                from app import run_crop_agent
                return run_crop_agent(payload)
            
            elif agent_name == "disease":
                from app import run_disease_agent
                img_bytes = payload.get("img_bytes")
                return run_disease_agent(img_bytes)
            
            elif agent_name == "fertilizer":
                from app import run_fertilizer_agent
                return run_fertilizer_agent(payload)
            
            elif agent_name == "yield":
                from app import run_yield_agent
                crop = payload.get("crop")
                return run_yield_agent(crop)
            
            elif agent_name == "market":
                from app import run_market_agent
                crop = payload.get("crop")
                return run_market_agent(crop)
            
            elif agent_name == "weather":
                from app import run_weather_agent
                city = payload.get("city")
                return run_weather_agent(city)
            
            elif agent_name == "sustainability":
                from app import orchestrator as parent_orchestrator
                # Handle sustainability advisor
                return {
                    "agent": "sustainability",
                    "status": "ok",
                    "data": {
                        "crop": payload.get("crop"),
                        "rotation_advice": "Rotate with legumes to restore soil nitrogen",
                        "practices": [
                            "Implement crop rotation annually",
                            "Use organic matter for soil health",
                            "Reduce chemical fertilizer use"
                        ]
                    },
                    "message": ""
                }
            
            elif agent_name == "irrigation":
                # Handle irrigation advisor
                crop = payload.get("crop")
                temp = payload.get("temp")
                humidity = payload.get("humidity")
                return {
                    "agent": "irrigation",
                    "status": "ok",
                    "data": {
                        "irrigation": f"Provide 4-5 irrigations for optimal yield of {crop}",
                        "harvest": f"Harvest {crop} after ~120-150 days from sowing"
                    },
                    "message": ""
                }
            
            else:
                return {
                    "agent": agent_name,
                    "status": "error",
                    "data": {},
                    "message": f"Agent '{agent_name}' not found"
                }
        
        except ImportError as e:
            logger.error(f"[Orchestrator] Import error in fallback: {e}")
            return {
                "agent": agent_name,
                "status": "error",
                "data": {},
                "message": f"Agent import failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"[Orchestrator] Fallback dispatch error: {e}")
            return {
                "agent": agent_name,
                "status": "error",
                "data": {},
                "message": f"Agent error: {str(e)}"
            }
    
    def multi_dispatch(self, requests: list) -> Dict[str, Any]:
        """
        Dispatch multiple requests in sequence
        Useful for complex workflows requiring multiple agents
        
        Args:
            requests: List of dicts with 'agent' and 'payload' keys
        
        Returns:
            Dict with all results
        """
        logger.info(f"[Orchestrator] Multi-dispatch for {len(requests)} agents")
        
        results = {}
        for req in requests:
            agent_name = req.get("agent")
            payload = req.get("payload", {})
            results[agent_name] = self.dispatch(agent_name, payload)
        
        return {
            "status": "ok",
            "results": results,
            "total_agents": len(requests)
        }
    
    def get_agent_status(self) -> Dict[str, bool]:
        """Get status of all registered agents"""
        return {
            agent: True for agent in self.agents.keys()
        }
    
    def list_agents(self) -> list:
        """Get list of all registered agents"""
        return list(self.agents.keys())


# Global orchestrator instance
_orchestrator_instance = None

def get_orchestrator() -> Orchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance

# Export
orchestrator = Orchestrator()
__all__ = ['Orchestrator', 'get_orchestrator', 'orchestrator']
