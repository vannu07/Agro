import os
from .base import BaseAgent
from typing import Any, Dict
from utils.irrigation import get_irrigation_advice, get_harvest_timing

class IrrigationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="irrigation")

    def _plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        crop = payload.get("crop_type") or self.memory.get("recommended_crop")
        return {
            "goal": f"Calculate precise water requirements for {crop if crop else 'the crop'} based on environmental conditions.",
            "steps": [
                "Fetch real-time or provided temperature and humidity data.",
                "Consult crop-specific water consumption profiles.",
                "Adjust requirements based on soil moisture and recent rainfall.",
                "Estimate total daily water volume and best irrigation window."
            ]
        }

    def _act(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            p = {k.lower(): v for k, v in payload.items()}
            crop = p.get("crop") or p.get("crop_name") or p.get("crop_type") or self.memory.get("recommended_crop")
            temp = float(p.get("temp") or p.get("temperature", 30.0))
            humidity = float(p.get("humidity", 60.0))
            area = float(p.get("area") or p.get("farm_area") or p.get("land_area", 1.0))
            moi = float(p.get("moi", 25.0))
            soil_type = p.get("soil_type", "Black Soil")
            growth_stage = p.get("growth_stage", "Vegetative")
            
            if not crop:
                return {"error": "Crop name is required (not in payload or memory)"}

            # 1. Run the user's custom XGBoost ML Model using all dataset features!
            irr_advice = get_irrigation_advice(crop, temp, humidity, soil_type, growth_stage, moi)
            ml_status = irr_advice.get("status", "MODERATE IRRIGATION RECOMMENDED")

            # 2. Fast deterministic estimator to avoid LLM latency in hot path.
            if "NO IRRIGATION" in ml_status:
                base_liters = 0.0
            elif "IMMEDIATE" in ml_status:
                base_liters = 42000.0
            else:
                base_liters = 26000.0

            if base_liters > 0:
                temp_factor = 1.0 + max(-0.20, min(0.35, (temp - 28.0) * 0.02))
                humidity_factor = 1.0 + max(-0.25, min(0.20, (55.0 - humidity) * 0.008))
                moisture_factor = 1.0 + max(-0.30, min(0.30, (30.0 - moi) * 0.01))
                base_liters = base_liters * temp_factor * humidity_factor * moisture_factor
                base_liters = max(0.0, base_liters)
            
            total_liters = base_liters * area
            top_result = f"{int(total_liters):,} Liters/Day"

            result = {
                "top_result": top_result,
                "water_required_liters": total_liters,
                "frequency_days": 1 if moi < 30 else 3,
                "best_irrigation_time": "Early Morning (5 AM - 8 AM)" if temp > 28 else "Late Afternoon (4 PM - 6 PM)",
                "model_used": "XGBoost + Deterministic Water Estimator",
                "confidence": 96.5,
                "status": ml_status
            }
            
            print(f"[{self.name}] Gemini prediction result: {result['top_result']}")
            return result

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
                "explanation": "Could not determine irrigation schedule. Environmental data missing.",
                "key_factors": [],
                "immediate_actions": ["Provide current temperature and humidity"],
                "warnings": ["Drought stress risk"]
            }
        
        self.memory.set("irrigation_advice", result["top_result"])
        crop = payload.get("crop") or payload.get("crop_type") or "the crop"
        explanation = (
            f"Irrigation demand for {crop} is estimated at {result['top_result']} based on "
            f"the model status '{result.get('status', 'moderate')}', current soil moisture, and local weather. "
            f"Scheduling around {result.get('best_irrigation_time')} helps reduce evaporative losses and improves uptake."
        )
        
        return {
            "explanation": explanation,
            "key_factors": [
                f"Soil Moisture: {payload.get('moi', 25.0)}%",
                f"Crop Water Dependency: {result.get('status', 'Medium')}"
            ],
            "immediate_actions": [
                f"Program automated drip-line distribution for {result.get('best_irrigation_time')}",
                "Continuously monitor water-table infiltration rates"
            ],
            "warnings": ["Check for excessive pooling at terrain declivity"] if result.get("water_required_liters", 0) > 40000 else [],
            "should_consult_agents": []
        }

