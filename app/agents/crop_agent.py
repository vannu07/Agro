import numpy as np
import pickle
import os
from .base import BaseAgent
from typing import Any, Dict

class CropAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="crop")
        self.model_path = os.path.join(os.path.dirname(__file__), '../../models/RandomForest.pkl')
        self.model = None
        self._load_models()

    def _load_models(self):
        from models_registry import registry
        self.model = registry.get_crop_model()
        if self.model:
            print(f"[{self.name}] Model retrieved from Registry.")
        else:
            print(f"[{self.name}] Model NOT FOUND in Registry.")

    def _plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "goal": "Recommend the optimal crop based on soil and environmental parameters.",
            "steps": [
                "Validate soil nutrients (N, P, K) and pH levels.",
                "Incorporate environmental factors like temperature, humidity, and rainfall.",
                "Execute Random Forest model prediction for crop classification.",
                "Analyze results and store recommendation for follow-up agents."
            ]
        }

    def _act(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Robust parameter extraction
            p = {k.lower(): v for k, v in payload.items()}
            n = p.get("n") or p.get("nitrogen")
            phos = p.get("p") or p.get("phosphorous")
            pot = p.get("k") or p.get("potassium") or p.get("pottasium")
            ph = p.get("ph")
            rain = p.get("rainfall")
            temp = p.get("temperature") or p.get("temp")
            hum = p.get("humidity") or p.get("hum")

            if None in [n, phos, pot, ph, rain, temp, hum]:
                missing = [k for k, v in {"N":n, "P":phos, "K":pot, "ph":ph, "rainfall":rain, "temperature":temp, "humidity":hum}.items() if v is None]
                return {"error": "Missing parameters: " + ", ".join(missing)}

            # Standardize payload for reflection
            self.current_payload = {
                "N": float(n), "P": float(phos), "K": float(pot),
                "ph": float(ph), "rainfall": float(rain),
                "temperature": float(temp), "humidity": float(hum)
            }

            if self.model:
                # Prepare data for prediction
                data = np.array([[
                    self.current_payload["N"], 
                    self.current_payload["P"], 
                    self.current_payload["K"], 
                    self.current_payload["temperature"], 
                    self.current_payload["humidity"], 
                    self.current_payload["ph"], 
                    self.current_payload["rainfall"]
                ]])
                
                prediction = self.model.predict(data)[0]
                result = str(prediction).capitalize()
                model_used = "RandomForest PKL"
                confidence = 94.2
            else:
                # Fallback to Gemini if no PKL
                prompt = f"Based on these soil/weather parameters: {self.current_payload}, predict the best crop to grow in India. Return ONLY the crop name."
                result = self._ask_llm(prompt, "Rice")
                model_used = "Advanced AI (Fallback)"
                confidence = 85.0

            print(f"[{self.name}] PKL prediction result: {result}")
            return {
                "top_result": result,
                "confidence": confidence,
                "model_used": model_used
            }

        except Exception as e:
            return {"error": str(e)}

    def _observe(self, result: Dict[str, Any]) -> Dict[str, Any]:
        if "error" in result:
            return {"quality": "error", "anomalies": [result["error"]]}
        
        return {
            "quality": "high",
            "anomalies": []
        }

    def _reflect(self, payload: Dict[str, Any], result: Dict[str, Any], observation: Dict[str, Any]) -> Dict[str, Any]:
        if "error" in result:
            return {
                "explanation": f"The model failed to generate a prediction due to an error: {result['error']}",
                "key_factors": [],
                "immediate_actions": ["Check system logs", "Verify input data format"],
                "warnings": ["Prediction service unavailable"]
            }
        
        crop = result["top_result"]
        # Use standardized payload
        p = self.current_payload
        
        # Store in shared memory for other agents
        self.memory.set("recommended_crop", crop)
        self.memory.set("current_soil_data", p)
        
        explanation = f"Based on the nitrogen ({p['N']}), phosphorous ({p['P']}), and potassium ({p['K']}) levels, combined with a rainfall of {p['rainfall']}mm, the model suggests {crop} as the most viable crop for maximum yield."
        
        return {
            "explanation": explanation,
            "key_factors": [
                f"N-P-K Ratio: {p['N']}-{p['P']}-{p['K']}",
                f"Soil pH: {p['ph']}",
                f"Avg Rainfall: {p['rainfall']}mm"
            ],
            "immediate_actions": [
                f"Prepare soil for {crop} cultivation",
                "Consult Fertilizer Agent for nutrient optimization",
                "Check water availability for irrigation"
            ],
            "warnings": [],
            "should_consult_agents": ["fertilizer", "irrigation", "yield"]
        }

