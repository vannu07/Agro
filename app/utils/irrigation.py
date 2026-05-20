import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .constants import AGRICULTURAL_CROPS, INDIAN_STATES, CROP_CATEGORIES, SOIL_TYPES

# Load ML Artifacts
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../models/hydration_model.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), '../../models/hydration_scaler.pkl')
ENCODER_PATH = os.path.join(os.path.dirname(__file__), '../../models/hydration_encoders.pkl')
FEATURES_PATH = os.path.join(os.path.dirname(__file__), '../../models/hydration_features.pkl')
DEFAULTS_PATH = os.path.join(os.path.dirname(__file__), '../../models/crop_stage_water_defaults.json')

_IRRIGATION_ARTIFACTS = None
_WATER_DEFAULTS = None


def _normalize_text(value):
    return str(value or "").strip().lower().replace("  ", " ")


def _load_water_defaults():
    global _WATER_DEFAULTS
    if _WATER_DEFAULTS is None:
        try:
            if os.path.exists(DEFAULTS_PATH):
                with open(DEFAULTS_PATH, 'r', encoding='utf-8') as f:
                    _WATER_DEFAULTS = json.load(f)
            else:
                _WATER_DEFAULTS = {}
        except Exception:
            _WATER_DEFAULTS = {}
    return _WATER_DEFAULTS


def _resolve_crop_key(crop):
    crop_norm = _normalize_text(crop)
    aliases = {
        'wheat': 'Wheat',
        'rice': 'Rice',
        'maize': 'Maize',
        'corn': 'Maize',
        'potato': 'Potato',
        'tomato': 'Tomato',
        'carrot': 'Carrot',
        'chilli': 'Chilli',
        'chili': 'Chilli',
    }
    return aliases.get(crop_norm, str(crop).strip())


def _match_stage_key(stage, available_stages):
    stage_norm = _normalize_text(stage)
    for key in available_stages.keys():
        key_norm = _normalize_text(key)
        if key_norm == stage_norm:
            return key
    for key in available_stages.keys():
        key_norm = _normalize_text(key)
        if stage_norm in key_norm or key_norm in stage_norm:
            return key
    return None


def _get_irrigation_artifacts():
    global _IRRIGATION_ARTIFACTS
    if _IRRIGATION_ARTIFACTS is None:
        _IRRIGATION_ARTIFACTS = {
            "model": joblib.load(MODEL_PATH),
            "scaler": joblib.load(SCALER_PATH),
            "encoders": joblib.load(ENCODER_PATH),
            "features": joblib.load(FEATURES_PATH),
        }
    return _IRRIGATION_ARTIFACTS

def get_irrigation_advice(crop, temp, humidity, soil_type='Black Soil', growth_stage='Seedling Stage', moi=25.0):
    """
    Predicts irrigation needs using the XGBoost Champion Model.
    """
    try:
        # 1. Load Model & Preprocessors
        artifacts = _get_irrigation_artifacts()
        model = artifacts["model"]
        scaler = artifacts["scaler"]
        encoders = artifacts["encoders"]
        features = artifacts["features"]
        water_defaults = _load_water_defaults()

        # 2. Prepare Input Data
        # Map categorical values using saved encoders
        # Fallback to 0 if category is unseen
        try:
            crop_encoded = encoders['crop ID'].transform([crop])[0]
        except:
            # Try to find a similar crop in the same category if unseen
            crop_encoded = 0
            for cat, crops in CROP_CATEGORIES.items():
                if crop in crops:
                    # Pick the first crop from this category that MIGHT be in the encoder
                    # This is better than absolute 0
                    for c in crops:
                        try:
                            crop_encoded = encoders['crop ID'].transform([c])[0]
                            break
                        except:
                            continue
                    break
            
        try:
            soil_encoded = encoders['soil_type'].transform([soil_type])[0]
        except:
            soil_encoded = 0
            
        try:
            growth_encoded = encoders['Seedling Stage'].transform([growth_stage])[0]
        except:
            growth_encoded = 0

        # Feature Engineering: Moisture_Efficiency
        moisture_efficiency = moi / (temp + 1)
        humidity_temp_ratio = humidity / (temp + 1)
        dryness_index = (100.0 - humidity) + (temp * 0.5)

        input_df = pd.DataFrame([{
            'crop ID': crop_encoded,
            'soil_type': soil_encoded,
            'Seedling Stage': growth_encoded,
            'MOI': moi,
            'temp': temp,
            'humidity': humidity,
            'Moisture_Efficiency': moisture_efficiency,
            'Humidity_Temp_Ratio': humidity_temp_ratio,
            'Dryness_Index': dryness_index,
        }])

        # 3. Predict
        input_scaled = scaler.transform(input_df[features])
        prediction = int(model.predict(input_scaled)[0])
        confidence = None
        try:
            proba = model.predict_proba(input_scaled)[0]
            confidence = float(max(proba))
        except Exception:
            confidence = None

        # 4. Blend model output with dataset-derived defaults to produce a stable irrigation recommendation.
        crop_key = _resolve_crop_key(crop)
        crop_defaults = water_defaults.get(crop_key, {})
        stage_key = _match_stage_key(growth_stage, crop_defaults)
        stage_default = crop_defaults.get(stage_key, {}) if stage_key else {}
        baseline_need = float(stage_default.get('water_need', 0.0) or 0.0)

        if baseline_need <= 0:
            stage_norm = _normalize_text(growth_stage)
            if 'harvest' in stage_norm:
                baseline_need = 0.0
            elif any(token in stage_norm for token in ['germination', 'seedling']):
                baseline_need = 4.5
            elif any(token in stage_norm for token in ['flowering', 'pollination']):
                baseline_need = 8.0
            elif any(token in stage_norm for token in ['maturation', 'maturity']):
                baseline_need = 5.5
            else:
                baseline_need = 6.5

        model_multiplier = {
            0: 0.88,
            1: 1.00,
            2: 1.18,
        }.get(prediction, 1.0)

        if confidence is not None:
            if confidence < 0.65:
                model_multiplier *= 0.95
            elif confidence > 0.90:
                model_multiplier *= 1.04

        # Keep environmental adjustment subtle so crop/stage defaults remain the main signal.
        temp_adjust = 1.0 + max(-0.12, min(0.16, (temp - 28.0) * 0.012))
        humidity_adjust = 1.0 + max(-0.10, min(0.12, (55.0 - humidity) * 0.006))
        moisture_adjust = 1.0 + max(-0.15, min(0.18, (30.0 - moi) * 0.008))

        adjusted_need = baseline_need * model_multiplier * temp_adjust * humidity_adjust * moisture_adjust
        if adjusted_need < 0:
            adjusted_need = 0.0

        # 5. Map result to readable status.
        stage_norm = _normalize_text(growth_stage)
        if 'harvest' in stage_norm:
            status = "NO IRRIGATION REQUIRED (Harvest)"
            color = "success"
            water_need = 0.0
        elif adjusted_need < 3.5:
            status = "LOW IRRIGATION REQUIRED"
            color = "success"
            water_need = round(adjusted_need, 2)
        elif adjusted_need < 7.5:
            status = "MODERATE IRRIGATION RECOMMENDED"
            color = "info"
            water_need = round(adjusted_need, 2)
        else:
            status = "IMMEDIATE IRRIGATION REQUIRED"
            color = "danger"
            water_need = round(adjusted_need, 2)

        return {
            "water_need": water_need,
            "status": status,
            "color": color,
            "crop": crop,
            "weather": {"temp": temp, "humidity": humidity},
            "soil": soil_type,
            "stage": growth_stage,
            "moi": moi,
            "confidence": confidence,
            "model_prediction": prediction,
        }

    except Exception as e:
        print(f"Irrigation Model Error: {e}")
        # Fallback to legacy rule-based logic
        return {
            "water_need": 10.0,
            "status": "Irrigation Recommended (Fallback Logic)",
            "color": "info",
            "crop": crop,
            "weather": {"temp": temp, "humidity": humidity}
        }

def get_harvest_timing(crop, sowing_date_str):
    """
    Predicts harvest readiness based on crop-specific growth duration.
    """
    durations = {
        "wheat": 110, "potato": 100, "carrot": 80, "tomato": 90, "chilli": 150, "rice": 120
    }
    
    try:
        sowing_date = datetime.strptime(sowing_date_str, "%Y-%m-%d")
        duration = durations.get(crop.lower(), 100)
        harvest_date = sowing_date + timedelta(days=duration)
        today = datetime.now()
        
        days_remaining = (harvest_date - today).days
        progress = min(100, max(0, int(((duration - days_remaining) / duration) * 100)))
        
        if days_remaining <= 0:
            stage = "READY FOR HARVEST"
        elif days_remaining < 15:
            stage = "LATE MATURITY / RIPENING"
        elif days_remaining < 45:
            stage = "FLOWERING / FRUITING"
        else:
            stage = "VEGETATIVE GROWTH"
            
        return {
            "harvest_date": harvest_date.strftime("%Y-%m-%d"),
            "days_remaining": max(0, days_remaining),
            "progress": progress,
            "stage": stage
        }
    except:
        return {"error": "Invalid date format"}

def get_hydration_telemetry(crop, base_need_mm):
    """
    Generates a 7-day hydration demand forecast for Plotly visualization.
    """
    import random
    days = [(datetime.now() + timedelta(days=i)).strftime("%a") for i in range(7)]
    values = []
    current = float(base_need_mm or 0.0)

    # Keep the chart in depth units (mm/day) instead of field-total liters.
    if current <= 0:
        return {
            "labels": days,
            "values": [0.0] * 7,
            "threshold": [0.0] * 7,
        }
    
    for _ in range(7):
        if current < 3:
            # Very low demand fields dry slowly.
            current += random.uniform(0.1, 0.6)
        else:
            # Normal fluctuation based on evapotranspiration in mm/day
            step_variance = random.uniform(-0.08, 0.08) * current
            current += step_variance
            
        values.append(max(0, round(current, 2)))
    
    return {
        "labels": days,
        "values": values,
        "threshold": [round(base_need_mm, 2)] * 7
    }
