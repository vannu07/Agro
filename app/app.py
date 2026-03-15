# Importing essential libraries and modules

from flask import Flask, render_template, request, redirect, jsonify
from markupsafe import Markup
import numpy as np
import pandas as pd
from utils.disease import disease_dic
from utils.fertilizer import fertilizer_dic
import requests
import config
import pickle
import io
import torch
from torchvision import transforms
from PIL import Image
from utils.model import ResNet9
from typing import Dict, Any

# ==============================================================================================

# -------------------------LOADING THE TRAINED MODELS -----------------------------------------------

# Loading plant disease classification model

disease_classes = ['Apple___Apple_scab',
                   'Apple___Black_rot',
                   'Apple___Cedar_apple_rust',
                   'Apple___healthy',
                   'Blueberry___healthy',
                   'Cherry_(including_sour)___Powdery_mildew',
                   'Cherry_(including_sour)___healthy',
                   'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
                   'Corn_(maize)___Common_rust_',
                   'Corn_(maize)___Northern_Leaf_Blight',
                   'Corn_(maize)___healthy',
                   'Grape___Black_rot',
                   'Grape___Esca_(Black_Measles)',
                   'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
                   'Grape___healthy',
                   'Orange___Haunglongbing_(Citrus_greening)',
                   'Peach___Bacterial_spot',
                   'Peach___healthy',
                   'Pepper,_bell___Bacterial_spot',
                   'Pepper,_bell___healthy',
                   'Potato___Early_blight',
                   'Potato___Late_blight',
                   'Potato___healthy',
                   'Raspberry___healthy',
                   'Soybean___healthy',
                   'Squash___Powdery_mildew',
                   'Strawberry___Leaf_scorch',
                   'Strawberry___healthy',
                   'Tomato___Bacterial_spot',
                   'Tomato___Early_blight',
                   'Tomato___Late_blight',
                   'Tomato___Leaf_Mold',
                   'Tomato___Septoria_leaf_spot',
                   'Tomato___Spider_mites Two-spotted_spider_mite',
                   'Tomato___Target_Spot',
                   'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
                   'Tomato___Tomato_mosaic_virus',
                   'Tomato___healthy']

disease_model_path = 'models/plant_disease_model.pth'
disease_model = None  # Lazy load

def load_disease_model():
    global disease_model
    if disease_model is None:
        print("Loading disease model...")
        disease_model = ResNet9(3, len(disease_classes))
        disease_model.load_state_dict(torch.load(
            disease_model_path, map_location=torch.device('cpu'), weights_only=False))
        disease_model.eval()
    return disease_model


# Loading crop recommendation model

crop_recommendation_model_path = 'models/RandomForest.pkl'
crop_recommendation_model = None  # Lazy load

def load_crop_model():
    global crop_recommendation_model
    if crop_recommendation_model is None:
        print("Loading crop recommendation model...")
        crop_recommendation_model = pickle.load(
            open(crop_recommendation_model_path, 'rb'))
    return crop_recommendation_model


# =========================================================================================

# Custom functions for calculations



import requests
import config

def weather_fetch(city_name):
    """
    Fetch temperature and humidity using WeatherAPI
    """
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": config.weather_api_key,
        "q": city_name
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if "error" in data:
        print("❌ Weather API error:", data["error"]["message"])
        return None

    temperature = data["current"]["temp_c"]  # Directly in Celsius
    humidity = data["current"]["humidity"]

    return temperature, humidity




def predict_image(img, model=None):
    """
    Transforms image to tensor and predicts disease label
    :params: image
    :return: prediction (string)
    """
    if model is None:
        model = load_disease_model()
    
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.ToTensor(),
    ])
    image = Image.open(io.BytesIO(img))
    img_t = transform(image)
    img_u = torch.unsqueeze(img_t, 0)

    # Get predictions from model
    yb = model(img_u)
    # Pick index with highest probability
    _, preds = torch.max(yb, dim=1)
    prediction = disease_classes[preds[0].item()]
    # Retrieve the class label
    return prediction


def run_weather_agent(city: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "agent": "weather",
        "status": "error",
        "data": {},
        "message": ""
    }
    weather = weather_fetch(city)
    if weather is None:
        result["message"] = "Weather data not available."
        return result
    temperature, humidity = weather
    risk_score = 0
    if temperature < 15 or temperature > 35:
        risk_score += 1
    if humidity < 30 or humidity > 85:
        risk_score += 1
    if risk_score == 0:
        level = "low"
    elif risk_score == 1:
        level = "moderate"
    else:
        level = "high"
    result["status"] = "ok"
    result["data"] = {
        "city": city,
        "temperature": float(temperature),
        "humidity": float(humidity),
        "risk_level": level
    }
    return result


def run_crop_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "agent": "crop",
        "status": "error",
        "data": {},
        "message": ""
    }
    for key in ["N", "P", "K", "ph", "rainfall", "temperature", "humidity"]:
        if key not in payload:
            result["message"] = "Missing parameter: " + key
            return result
    data = np.array([[payload["N"], payload["P"], payload["K"], payload["temperature"], payload["humidity"], payload["ph"], payload["rainfall"]]])
    model = load_crop_model()
    prediction = model.predict(data)[0]
    result["status"] = "ok"
    result["data"] = {
        "recommended_crop": str(prediction)
    }
    return result


def run_fertilizer_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    crop_name = payload["crop_name"]
    N = payload["N"]
    P = payload["P"]
    K = payload["K"]
    df = pd.read_csv("app/Data/fertilizer.csv")
    nr = df[df["Crop"] == crop_name]["N"].iloc[0]
    pr = df[df["Crop"] == crop_name]["P"].iloc[0]
    kr = df[df["Crop"] == crop_name]["K"].iloc[0]
    n = nr - N
    p = pr - P
    k = kr - K
    temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
    max_value = temp[max(temp.keys())]
    if max_value == "N":
        if n < 0:
            key = "NHigh"
        else:
            key = "Nlow"
    elif max_value == "P":
        if p < 0:
            key = "PHigh"
        else:
            key = "Plow"
    else:
        if k < 0:
            key = "KHigh"
        else:
            key = "Klow"
    response_text = str(fertilizer_dic[key])
    return {
        "agent": "fertilizer",
        "status": "ok",
        "data": {
            "crop_name": crop_name,
            "key": key,
            "message": response_text
        },
        "message": ""
    }


def run_disease_agent(img: bytes) -> Dict[str, Any]:
    try:
        label = predict_image(img)
        description = str(disease_dic[label])
        return {
            "agent": "disease",
            "status": "ok",
            "data": {
                "label": label,
                "description": description
            },
            "message": ""
        }
    except Exception as exc:
        return {
            "agent": "disease",
            "status": "error",
            "data": {},
            "message": str(exc)
        }


yield_data = None


def get_yield_data():
    global yield_data
    if yield_data is not None:
        return yield_data
    try:
        df = pd.read_csv("Data-raw/raw_districtwise_yield_data.csv")
        df = df.dropna(subset=["Area", "Production"])
        df = df[df["Area"] > 0]
        df["Yield"] = df["Production"] / df["Area"]
        yield_data = df
    except Exception:
        yield_data = None
    return yield_data


def run_yield_agent(crop: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "agent": "yield",
        "status": "error",
        "data": {},
        "message": ""
    }
    df = get_yield_data()
    if df is None:
        result["message"] = "Yield dataset not available."
        return result
    subset = df[df["Crop"].str.lower() == crop.lower()]
    if subset.empty:
        result["message"] = "No yield data for this crop."
        return result
    mean_yield = float(subset["Yield"].mean())
    result["status"] = "ok"
    result["data"] = {
        "crop": crop,
        "avg_yield": mean_yield,
        "unit": "tons per hectare"
    }
    return result


MARKET_PRICES = {
    "rice": 2200.0,
    "wheat": 2400.0,
    "maize": 1900.0,
    "jute": 4000.0,
    "coffee": 12000.0,
    "banana": 1500.0
}


def run_market_agent(crop: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "agent": "market",
        "status": "ok",
        "data": {},
        "message": ""
    }
    price = MARKET_PRICES.get(crop.lower())
    if price is None:
        result["status"] = "error"
        result["message"] = "Market price not available."
        return result
    result["data"] = {
        "crop": crop,
        "price_per_quintal": float(price),
        "currency": "INR"
    }
    return result


def orchestrate_crop(payload: Dict[str, Any]) -> Dict[str, Any]:
    agents: Dict[str, Any] = {}
    city = payload.get("city")
    if city:
        weather_res = run_weather_agent(city)
        agents["weather"] = weather_res
        if weather_res["status"] == "ok":
            enriched = dict(payload)
            enriched["temperature"] = weather_res["data"]["temperature"]
            enriched["humidity"] = weather_res["data"]["humidity"]
        else:
            return {
                "task": "crop_recommendation",
                "agents": agents
            }
    else:
        return {
            "task": "crop_recommendation",
            "agents": {}
        }
    crop_res = run_crop_agent(enriched)
    agents["crop"] = crop_res
    crop_name = None
    if crop_res["status"] == "ok":
        crop_name = crop_res["data"].get("recommended_crop")
    if crop_name:
        agents["yield"] = run_yield_agent(crop_name)
        agents["market"] = run_market_agent(crop_name)
    return {
        "task": "crop_recommendation",
        "agents": agents
    }


def orchestrate_fertilizer(payload: Dict[str, Any]) -> Dict[str, Any]:
    agents: Dict[str, Any] = {}
    agents["fertilizer"] = run_fertilizer_agent(payload)
    return {
        "task": "fertilizer_recommendation",
        "agents": agents
    }


def orchestrate_disease(img: bytes) -> Dict[str, Any]:
    agents: Dict[str, Any] = {}
    agents["disease"] = run_disease_agent(img)
    return {
        "task": "disease_detection",
        "agents": agents
    }


def run_orchestrator(task: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if task == "crop_recommendation":
        return orchestrate_crop(payload)
    if task == "fertilizer_recommendation":
        return orchestrate_fertilizer(payload)
    return {
        "task": task,
        "agents": {}
    }

# ===============================================================================================
# ------------------------------------ FLASK APP -------------------------------------------------


app = Flask(__name__)

# render home page


@ app.route('/')
def home():
    title = 'FarmIQ - Home'
    return render_template('index.html', title=title)

# render crop recommendation form page


@ app.route('/crop-recommend')
def crop_recommend():
    title = 'FarmIQ - Crop Recommendation'
    return render_template('crop.html', title=title)

# render fertilizer recommendation form page


@ app.route('/fertilizer')
def fertilizer_recommendation():
    title = 'FarmIQ - Fertilizer Suggestion'

    return render_template('fertilizer.html', title=title)

# render disease prediction input page




# ===============================================================================================

# RENDER PREDICTION PAGES

# render crop recommendation result page


@ app.route('/crop-predict', methods=['POST'])
def crop_prediction():
    title = 'FarmIQ - Crop Recommendation'

    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])
        city = request.form.get("city")
        payload = {
            "N": N,
            "P": P,
            "K": K,
            "ph": ph,
            "rainfall": rainfall,
            "city": city
        }
        orchestration = run_orchestrator("crop_recommendation", payload)
        agents = orchestration.get("agents", {})
        crop_agent = agents.get("crop")
        if crop_agent and crop_agent.get("status") == "ok":
            final_prediction = crop_agent["data"]["recommended_crop"]
            return render_template('crop-result.html', prediction=final_prediction, orchestration=orchestration, title=title)
        return render_template('try_again.html', title=title)

# render fertilizer recommendation result page


@ app.route('/fertilizer-predict', methods=['POST'])
def fert_recommend():
    title = 'FarmIQ - Fertilizer Suggestion'

    crop_name = str(request.form['cropname'])
    N = int(request.form['nitrogen'])
    P = int(request.form['phosphorous'])
    K = int(request.form['pottasium'])
    payload = {
        "crop_name": crop_name,
        "N": N,
        "P": P,
        "K": K
    }
    orchestration = run_orchestrator("fertilizer_recommendation", payload)
    agents = orchestration.get("agents", {})
    fert_agent = agents.get("fertilizer")
    if fert_agent and fert_agent.get("status") == "ok":
        message = fert_agent["data"]["message"]
        response = Markup(message)
        return render_template('fertilizer-result.html', recommendation=response, title=title)
    return render_template('fertilizer-result.html', recommendation="Fertilizer recommendation not available.", title=title)

# render disease prediction result page


@app.route('/disease-predict', methods=['GET', 'POST'])
def disease_prediction():
    title = 'FarmIQ - Disease Detection'

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files.get('file')
        if not file:
            return render_template('disease.html', title=title)
        try:
            img = file.read()
            orchestration = orchestrate_disease(img)
            agents = orchestration.get("agents", {})
            disease_agent = agents.get("disease")
            if disease_agent and disease_agent.get("status") == "ok":
                prediction = Markup(disease_agent["data"]["description"])
                return render_template('disease-result.html', prediction=prediction, title=title)
        except Exception:
            return render_template('disease.html', title=title)
    return render_template('disease.html', title=title)


@app.route('/dashboard')
def dashboard():
    title = 'FarmIQ - Dashboard'
    crop_stats = None
    try:
        crop_df = pd.read_csv('Data-processed/crop_recommendation.csv')
        unique_crops = sorted(crop_df['label'].unique().tolist())
        crop_stats = {
            "total_rows": int(len(crop_df)),
            "unique_count": int(len(unique_crops)),
            "unique_crops": unique_crops
        }
    except Exception:
        crop_stats = None
    yield_summary = []
    df = get_yield_data()
    if df is not None:
        grouped = df.groupby("Crop")["Yield"].mean().reset_index()
        top = grouped.sort_values("Yield", ascending=False).head(10)
        for _, row in top.iterrows():
            yield_summary.append({
                "crop": row["Crop"],
                "avg_yield": float(row["Yield"]),
                "unit": "tons per hectare"
            })
    return render_template('dashboard.html', title=title, crop_stats=crop_stats, yield_stats=yield_summary)


@app.route('/api/assistant', methods=['POST'])
def api_assistant():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    text = message.lower()
    reply = "I did not understand your question. Please try asking about crop, fertilizer, or disease."
    if "crop" in text:
        reply = "Use the Crop section to get recommendations based on your soil and city weather."
    elif "fertilizer" in text:
        reply = "Use the Fertilizer section and enter your NPK values to get suggestions."
    elif "disease" in text:
        reply = "Upload a clear leaf image in the Disease section so I can analyse it."
    elif "weather" in text:
        reply = "Enter your city on the Crop page so I can fetch live weather data."
    return jsonify({"reply": reply})


# ===============================================================================================
if __name__ == '__main__':
    app.run(debug=False)
