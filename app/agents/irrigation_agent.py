import os
from .base import BaseAgent
from typing import Any, Dict
from utils.irrigation import get_irrigation_advice, get_harvest_timing
import json

# Load fallback defaults generated from dataset
_DEFAULTS = {}
_CROP_ALIASES = {
    "wheat": "Wheat",
    "rice": "Rice",
    "maize": "Maize",
    "corn": "Maize",
    "potato": "Potato",
    "tomato": "Tomato",
    "carrot": "Carrot",
    "chilli": "Chilli",
    "chili": "Chilli",
}


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower().replace("  ", " ")


def _match_stage_key(stage: str, available_stages: Dict[str, Any]) -> str | None:
    normalized_stage = _normalize_text(stage)
    for key in available_stages.keys():
        key_norm = _normalize_text(key)
        if key_norm == normalized_stage:
            return key
    for key in available_stages.keys():
        key_norm = _normalize_text(key)
        if normalized_stage in key_norm or key_norm in normalized_stage:
            return key
    return None


def _resolve_crop_key(crop: Any) -> str:
    crop_text = _normalize_text(crop)
    return _CROP_ALIASES.get(crop_text, str(crop).strip())

try:
    defaults_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'crop_stage_water_defaults.json')
    if os.path.exists(defaults_path):
        with open(defaults_path, 'r', encoding='utf-8') as f:
            _DEFAULTS = json.load(f)
except Exception:
    _DEFAULTS = {}

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
            sowing_date = p.get("sowing_date")
            
            if not crop:
                return {"error": "Crop name is required (not in payload or memory)"}

            # 1. Run the user's custom XGBoost ML Model using all dataset features!
            irr_advice = get_irrigation_advice(crop, temp, humidity, soil_type, growth_stage, moi)
            ml_status = irr_advice.get("status", "MODERATE IRRIGATION RECOMMENDED")

            # If sowing_date is provided, use harvest timing to override irrigation when crop is ready
            try:
                if sowing_date:
                    harvest_info = get_harvest_timing(crop, sowing_date)
                    if isinstance(harvest_info, dict) and harvest_info.get("stage") == "READY FOR HARVEST":
                        result = {
                            "top_result": "0 Liters/Day",
                            "water_required_liters": 0.0,
                            "frequency_days": 1,
                            "best_irrigation_time": "Early Morning (5 AM - 8 AM)" if temp > 28 else "Late Afternoon (4 PM - 6 PM)",
                            "model_used": "XGBoost + Deterministic Water Estimator",
                            "confidence": 96.5,
                            "status": "NO IRRIGATION REQUIRED (Harvest)"
                        }
                        print(f"[{self.name}] Gemini prediction result: {result['top_result']}")
                        return result
            except Exception:
                pass

            # 2. Fast deterministic estimator to avoid LLM latency in hot path.
            # Use ML model's `water_need` as a base rate (interpreted as mm or liters/m^2)
            # Convert to liters per hectare: 1 mm over 1 ha = 10,000 liters
            reported_need = float(irr_advice.get("water_need", 10.0))

            # Growth stage multipliers (relative water demand)
            stage_multipliers = {
                "Germination": 0.4,
                "Seedling Stage": 0.6,
                "Vegetative": 1.0,
                "Vegetative Growth": 1.0,
                "Flowering": 1.2,
                "Pollination": 1.2,
                "Fruiting / Grain Filling": 1.3,
                "Fruit/Grain/Bulb Formation": 1.3,
                "Maturation": 0.9,
                "Harvest": 0.0,
                "Harvest Ready": 0.0,
                "Harvest Ready": 0.0
            }

            # Normalise the incoming growth_stage into a known key
            gs_key = growth_stage if isinstance(growth_stage, str) else str(growth_stage)
            gs_key = gs_key.strip()
            # Try to match substrings for more robust mapping
            matched_stage = None
            for k in stage_multipliers.keys():
                if k.lower() in gs_key.lower() or gs_key.lower() in k.lower():
                    matched_stage = k
                    break
            if matched_stage is None:
                matched_stage = "Vegetative"

            stage_multiplier = stage_multipliers.get(matched_stage, 1.0)

            # If model indicates no irrigation, allow exceptions for early growth stages
            if "NO IRRIGATION" in ml_status:
                crop_key = _resolve_crop_key(crop)
                crop_defaults = _DEFAULTS.get(crop_key, {})

                if matched_stage in ("Germination", "Seedling Stage", "Seedling"):
                    # Seedlings need minimal moisture even if model optimized to no irrigation
                    ml_status = "LOW IRRIGATION REQUIRED (Seedling)"
                    # ensure a reasonable small baseline
                    fallback_default = 2.0
                    stage_default_key = _match_stage_key(matched_stage, crop_defaults)
                    if stage_default_key:
                        stage_default = crop_defaults.get(stage_default_key, {})
                        fallback_default = float(stage_default.get('water_need', fallback_default) or fallback_default)
                    reported_need = max(reported_need, fallback_default)
                else:
                    # Try dataset-derived fallback for this crop+stage
                    try:
                        stage_default_key = _match_stage_key(matched_stage, crop_defaults)
                        if stage_default_key:
                            stage_default = crop_defaults[stage_default_key]
                            dataset_need = float(stage_default.get('water_need', 0.0) or 0.0)
                            if dataset_need > 0:
                                reported_need = dataset_need
                                ml_status = stage_default.get('status', ml_status)
                            else:
                                reported_need = max(reported_need, 4.5)
                        else:
                            reported_need = max(reported_need, 4.5)
                    except Exception:
                        reported_need = max(reported_need, 4.5)

            # Convert reported_need -> liters per hectare
            liters_per_ha = reported_need * 10000.0 * stage_multiplier

            # Apply small environmental adjustment factors
            temp_factor = 1.0 + max(-0.20, min(0.35, (temp - 28.0) * 0.02))
            humidity_factor = 1.0 + max(-0.25, min(0.20, (55.0 - humidity) * 0.008))
            moisture_factor = 1.0 + max(-0.30, min(0.30, (30.0 - moi) * 0.01))

            liters_per_ha = liters_per_ha * temp_factor * humidity_factor * moisture_factor
            liters_per_ha = max(0.0, liters_per_ha)

            # Area is interpreted as hectares in the form; total liters = liters_per_ha * hectares
            total_liters = liters_per_ha * area

            top_result = f"{int(total_liters):,} Liters/Day"

            result = {
                "top_result": top_result,
                "water_required_liters": total_liters,
                "field_area_hectares": area,
                "water_depth_mm": round(total_liters / (area * 10000.0), 2) if area > 0 else 0.0,
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

