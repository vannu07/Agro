import os
import joblib
import pandas as pd
import numpy as np

from .constants import AGRICULTURAL_CROPS, INDIAN_STATES, CROP_CATEGORIES

_SUSTAINABILITY_ARTIFACTS = None


def _get_sustainability_artifacts(model_dir):
    global _SUSTAINABILITY_ARTIFACTS
    if _SUSTAINABILITY_ARTIFACTS is None:
        _SUSTAINABILITY_ARTIFACTS = {
            "clf": joblib.load(os.path.join(model_dir, 'sustain_recommend_model.pkl')),
            "reg": joblib.load(os.path.join(model_dir, 'sustain_yield_model.pkl')),
            "scaler_c": joblib.load(os.path.join(model_dir, 'sustain_class_scaler.pkl')),
            "scaler_r": joblib.load(os.path.join(model_dir, 'sustain_reg_scaler.pkl')),
            "encoders": joblib.load(os.path.join(model_dir, 'sustain_encoders.pkl')),
            "features": joblib.load(os.path.join(model_dir, 'sustain_features.pkl')),
        }
    return _SUSTAINABILITY_ARTIFACTS

def get_rotation_advisor(current_crop, soil_n, soil_p, soil_k, ph=6.5, organic=2.0, moisture=15.0, solar=15, region='Punjab', season='Kharif', soil_type='Alluvial'):
    """
    Suggests the next crop for rotation and sustainability tips using ML if available.
    """
    
    model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')
    model_path = os.path.join(model_dir, 'sustain_recommend_model.pkl')
    yield_model_path = os.path.join(model_dir, 'sustain_yield_model.pkl')
    
    # Sustainability Tips (Commonly shared)
    tips = [
        "Incorporate organic manure to improve soil structure and water retention.",
        "Practice intercropping with legumes to naturally fix nitrogen in the soil.",
        "Use mulching to conserve soil moisture and suppress weed growth.",
        "Implement drip irrigation to reduce water wastage by up to 40%.",
        "Adopt Integrated Pest Management (IPM) to reduce chemical pesticide usage."
    ]

    # Try ML-driven advice
    if os.path.exists(model_path) and os.path.exists(yield_model_path):
        try:
            artifacts = _get_sustainability_artifacts(model_dir)
            clf = artifacts["clf"]
            reg = artifacts["reg"]
            scaler_c = artifacts["scaler_c"]
            scaler_r = artifacts["scaler_r"]
            encoders = artifacts["encoders"]
            features = artifacts["features"]
            
            # Prepare Features for Classifier
            year = 2024
            
            # Handle unseen region
            try:
                reg_enc = encoders['Region'].transform([region])[0]
            except:
                reg_enc = 0
                
            try:
                sea_enc = encoders['Season'].transform([season])[0]
            except:
                sea_enc = 0
                
            try:
                soil_enc = encoders['Soil Type'].transform([soil_type])[0]
            except:
                soil_enc = 0
                
            rot_enc = 0 # Default placeholder
            rainfall = 800 # Placeholder
            
            x_c = pd.DataFrame([[year, reg_enc, sea_enc, soil_enc, ph, soil_n, soil_p, soil_k, organic, moisture, rainfall, solar, rot_enc]], columns=features['class'])
            x_c_scaled = scaler_c.transform(x_c)
            
            next_crop_enc = clf.predict(x_c_scaled)[0]
            next_crop = encoders['Crop_Planted (Action)'].inverse_transform([next_crop_enc])[0]
            
            # Predict Yield for that recommended crop
            x_r = x_c.copy()
            x_r['Crop_Enc'] = next_crop_enc
            x_r_scaled = scaler_r.transform(x_r)
            predicted_yield = reg.predict(x_r_scaled)[0]
            
            analysis = f"Based on ML synthesis, rotating to {next_crop} will optimize your harvest. Projected yield with current soil health: {predicted_yield:.2f} kg/ha."
            
            return {
                "next_crop_suggestions": [next_crop, "Green Gram", "Soybean"],
                "soil_analysis": analysis,
                "sustainability_tips": tips[:3],
                "ml_active": True
            }
        except Exception as e:
            print(f"ML Inference Error: {e}")

    # Fallback to Rule-Based (Heuristics)
    rotations = {
        "Cereals": ["Black Gram", "Green Gram", "Cowpea", "Chickpea"],
        "Pulses": ["Maize", "Wheat", "Sunflower", "Mustard"],
        "Oilseeds": ["Wheat", "Sorghum", "Maize"],
        "Fruits": ["Legumes", "Cover Crops", "Vegetables"],
        "Vegetables": ["Legumes", "Cereals", "Mustard"],
        "Commercial": ["Groundnut", "Soybean", "Black Gram"],
        "Spices": ["Cereals", "Pulses", "Legumes"],
        "Plantation": ["Legumes", "Cover Crops"]
    }
    
    # Categorize current crop
    category = "Cereals" # Default
    for cat, crops in CROP_CATEGORIES.items():
        if current_crop in crops:
            category = cat
            break
            
    suggestions = rotations.get(category, ["Legumes", "Pulses", "Cover Crops"])
    
    analysis = ""
    if soil_n < 50:
        analysis = f"Soil is Low in Nitrogen. Rotating from {current_crop} to {suggestions[0]} will restore nitrogen levels."
    elif soil_p < 40:
        analysis = "Phosphorous levels are low. Consider adding bone meal or rock phosphate before the next sowing."
    else:
        analysis = f"Soil health is moderate. Optimal rotation to {suggestions[0]} will maintain these levels."

    return {
        "next_crop_suggestions": suggestions,
        "soil_analysis": analysis,
        "sustainability_tips": tips[:3],
        "ml_active": False
    }

def get_crop_list():
    return AGRICULTURAL_CROPS

def get_nutrient_spider_data(n, p, k):
    ideal_n = 80
    ideal_p = 60
    ideal_k = 70
    return {
        "labels": ["Nitrogen (N)", "Phosphorous (P)", "Potassium (K)"],
        "values": [min(n, 150), min(p, 150), min(k, 150)],
        "benchmark": [ideal_n, ideal_p, ideal_k]
    }
