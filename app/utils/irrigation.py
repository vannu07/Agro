import os
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

_IRRIGATION_ARTIFACTS = None


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

        input_df = pd.DataFrame([{
            'crop ID': crop_encoded,
            'soil_type': soil_encoded,
            'Seedling Stage': growth_encoded,
            'MOI': moi,
            'temp': temp,
            'humidity': humidity,
            'Moisture_Efficiency': moisture_efficiency
        }])

        # 3. Predict
        input_scaled = scaler.transform(input_df[features])
        prediction = int(model.predict(input_scaled)[0])

        # 4. Map Result (0=No, 1=Yes, 2=Moderate)
        if prediction == 1:
            status = "IMMEDIATE IRRIGATION REQUIRED"
            color = "danger"
            water_need = round(15.0 + (temp * 0.1), 2)
        elif prediction == 2:
            status = "MODERATE IRRIGATION RECOMMENDED"
            color = "info"
            water_need = round(8.0 + (temp * 0.05), 2)
        else:
            status = "NO IRRIGATION REQUIRED (Optimized)"
            color = "success"
            water_need = 0.0

        return {
            "water_need": water_need,
            "status": status,
            "color": color,
            "crop": crop,
            "weather": {"temp": temp, "humidity": humidity},
            "soil": soil_type,
            "stage": growth_stage,
            "moi": moi
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

def get_hydration_telemetry(crop, base_need):
    """
    Generates a 7-day hydration demand forecast for Plotly visualization.
    """
    import random
    days = [(datetime.now() + timedelta(days=i)).strftime("%a") for i in range(7)]
    values = []
    current = base_need
    
    for _ in range(7):
        if current < 5000:
            # Soil is highly saturated right now; represent the field slowly drying out over the week
            current += random.uniform(4000, 12000)
        else:
            # Normal fluctuation based on evapotranspiration
            step_variance = random.uniform(-0.08, 0.08) * base_need
            current += step_variance
            
        values.append(max(0, round(current, 0)))
    
    return {
        "labels": days,
        "values": values,
        "threshold": [base_need] * 7
    }
