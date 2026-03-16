# Importing essential libraries and modules

from flask import Flask, render_template, request, redirect, jsonify, session, url_for
import os
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
from utils.yield_logic import get_yield_prediction, get_unique_values
from utils.sustainability import get_rotation_advisor, get_crop_list
from utils.irrigation import get_irrigation_advice, get_harvest_timing

# ==============================================================================================
from utils.db import get_db, mongo
from orchestrator import Orchestrator

# Initialize database and Orchestrator
db = get_db()
orchestrator = Orchestrator()
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
        print("[Weather API Error]:", data["error"]["message"])
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


# ===============================================================================================
# ------------------------------------ FLASK APP -------------------------------------------------


app = Flask(__name__)
app.secret_key = os.getenv('AUTH0_SECRET', os.getenv("FLASK_SECRET_KEY", "super-secret-key-123"))

# Custom Jinja2 Filters
@app.template_filter('clamp')
def clamp_filter(v, low, high):
    try:
        return max(low, min(high, float(v)))
    except (ValueError, TypeError):
        return low

# Initialize Auth0
from auth import setup_auth, oauth, requires_auth
setup_auth(app)

# render home page


@app.route('/login')
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route('/callback')
def callback():
    try:
        token = oauth.auth0.authorize_access_token()
        session["user"] = token
        
        # Sync user to MongoDB!
        user_info = token.get("userinfo")
        if user_info:
            mongo.sync_user(user_info)
            
    except Exception as e:
        print(f"Auth Callback Error: {e}")
    
    return redirect(session.pop('next', '/dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(
        f'https://{os.getenv("AUTH0_DOMAIN")}/v2/logout?'
        f'client_id={os.getenv("AUTH0_CLIENT_ID")}&returnTo={url_for("home", _external=True)}'
    )

@app.route('/')
def home():
    title = 'Krishi Mitr - Home'
    return render_template('index.html', title=title)

@app.route('/about')
def about():
    title = 'Krishi Mitr - About Us'
    return render_template('about.html', title=title)

CASE_STUDIES_DATA = {
    "rakesh-delhi": {
        "name": "Rakesh",
        "location": "Delhi",
        "crop": "Paddy/Rice",
        "image": "case_study_rice_punjab.png",
        "title": "Precision Yield Enhancement for Paddy",
        "summary": "Rakesh implemented AI-driven nitrogen monitoring and precision irrigation, achieving a 20% yield increase in the urban-outskirts of Delhi.",
        "full_story": "Rakesh, a progressive farmer on the outskirts of Delhi, faced challenges with soil quality and erratic water supply. By using Krishi Mitr's Crop Advisor, he received a customized fertilization plan that perfectly balanced his soil's NPK levels. The Hydration Agent further optimized his irrigation schedule, ensuring every drop counted. The result was not just a 20% higher yield, but also a significantly healthier crop that fetched premium prices in the local mandis.",
        "stats": ["+20% Yield", "25% Water Saved", "15% Cost Reduction"]
    },
    "sudesh-delhi": {
        "name": "Sudesh",
        "location": "Delhi",
        "crop": "Potato",
        "image": "case_study_potato_bengal.png",
        "title": "Disease Prevention in Potato Crops",
        "summary": "Sudesh used the Plant Pathologist agent to detect early-stage Late Blight, saving her entire harvest from a potential epidemic.",
        "full_story": "Sudesh had been struggling with recurring crop losses due to potato blight. Last season, she integrated the Plant Pathologist AI into her daily routine. A simple photo upload flagged early-stage fungal infection weeks before it was visible to the naked eye. Following the AI's instant treatment recommendation, Sudesh was able to contain the outbreak locally, preserving 95% of her crop value and ensuring food security for her community.",
        "stats": ["95% Crop Saved", "72h Detection", "Zero Epidemic Spread"]
    },
    "ashok-delhi": {
        "name": "Ashok",
        "location": "Delhi",
        "crop": "Mustard",
        "image": "case_study_cotton_telangana.png",
        "title": "Smart Nutrient Management for Mustard",
        "summary": "Ashok optimized his fertilizer usage using Nutrient Lab, reducing chemical waste by 30% while maintaining peak health.",
        "full_story": "Ashok, farming in the Najafgarh area, was concerned about the rising costs of fertilizers. The Nutrient Lab agent analyzed his soil reports and generated a precise application schedule tailored to the growth stages of his mustard crop. By applying only what was needed, Ashok reduced his chemical input by 30%, leading to a more sustainable farming practice and a higher-quality oily seed output that surpassed regional benchmarks.",
        "stats": ["30% Less Fertilizer", "+12% Oil Content", "Organic-First Approach"]
    },
    "balbir-baghpat": {
        "name": "Balbir",
        "location": "Baghpat, UP",
        "crop": "Sugarcane",
        "image": "case_study_turmeric_erode.png",
        "title": "Sugarcane Yield Revolution",
        "summary": "Balbir transformed his sugarcane productivity in Baghpat using satellite-linked soil health monitoring and predictive analytics.",
        "full_story": "In the heart of the sugarcane belt in Baghpat, Balbir was a traditional farmer looking for a modern edge. Krishi Mitr provided him with long-term crop rotation advice and real-time alerts for pest infestations. By following the AI's 'Sustain Master' guidelines, Balbir improved the soil's organic carbon content, leading to thicker, juicier sugarcane stalks and an 18% increase in recovery rate at the local sugar factory.",
        "stats": ["+18% Recovery", "Soil Health ↑", "Pest Alert Accuracy: 98%"]
    },
    "suresh-baghpat": {
        "name": "Suresh",
        "location": "Baghpat, UP",
        "crop": "Wheat",
        "image": "case_study_irrigation_maharashtra.png",
        "title": "Optimized Irrigation for Wheat",
        "summary": "Suresh adopted IoT-enabled irrigation cycles, saving significant groundwater while boosting grain quality in the fertile UP plains.",
        "full_story": "Suresh's wheat fields in Baghpat were showing signs of water stress during critical growth periods. The Hydration Agent connected to local weather stations and provided Suresh with a week-ahead watering plan. This precision allowed Suresh to maintain optimal soil moisture without over-irrigating. The result was a bumper crop with superior grain weight and color, proving that smart water management is the key to resilience.",
        "stats": ["40% Water Saved", "+15% Grain Weight", "Energy Costs ↓ 20%"]
    },
    "pradeep-baroda": {
        "name": "Pradeep",
        "location": "Baroda, UP",
        "crop": "Vegetable Farming",
        "image": "case_study_apple_himachal.png",
        "title": "Diversified Vegetable Success",
        "summary": "Pradeep shifted to high-value vegetable farming based on market trend analytics and seasonal suitability predictions.",
        "full_story": "Pradeep, from Baroda in UP, used the 'Precision Yield' and 'Market Analytics' features to identify a gap in the local market for high-quality bell peppers and exotic vegetables. Krishi Mitr guided him through the entire greenhouse setup and nutrient management. By aligning his production with peak market demand intervals, Pradeep saw a tripling of his annual income, transforming his small plot into a highly profitable enterprise.",
        "stats": ["3x Income Increase", "Market-Led Production", "Year-round Yield"]
    }
}

@app.route('/case-studies')
@requires_auth
def case_studies():
    title = 'Krishi Mitr - Case Studies'
    return render_template('case_studies.html', title=title, cases=CASE_STUDIES_DATA)

MARKET_DATA = [
    {"crop": "Wheat", "price": "₹2,275", "change": "+1.2%", "trend": "up", "volume": "high"},
    {"crop": "Paddy", "price": "₹2,183", "change": "-0.5%", "trend": "down", "volume": "moderate"},
    {"crop": "Maize", "price": "₹1,962", "change": "+2.1%", "trend": "up", "volume": "high"},
    {"crop": "Cotton", "price": "₹6,020", "change": "+0.8%", "trend": "up", "volume": "low"},
    {"crop": "Mustard", "price": "₹5,450", "change": "-1.1%", "trend": "down", "volume": "moderate"},
]

@app.route('/market-trends')
@requires_auth
def market_trends():
    title = 'Krishi Mitr - Market Trends'
    return render_template('market_trends.html', title=title, market_data=MARKET_DATA)

NEWS_DATA = [
    {
        "title": "Government Announces New MSP for Kharif Crops",
        "category": "Policy",
        "date": "March 15, 2026",
        "summary": "The central government has increased the Minimum Support Price for various Kharif crops to ensure better returns for farmers.",
        "image": "future_tech.png"
    },
    {
        "title": "Smart Irrigation Adoption Rises in North India",
        "category": "Technology",
        "date": "March 14, 2026",
        "summary": "Over 50,000 farmers in Punjab and Haryana have successfully adopted AI-linked drip irrigation systems this season.",
        "image": "hero_farm.png"
    },
    {
        "title": "New Pest-Resistant Wheat Variety Released",
        "category": "Seed Tech",
        "date": "March 12, 2026",
        "summary": "Agricultural scientists have developed a new variety of wheat that is highly resistant to yellow rust and heat stress.",
        "image": "crop.png"
    }
]

@app.route('/agri-tech-news')
@requires_auth
def agri_tech_news():
    title = 'Krishi Mitr - Agri-Tech News'
    return render_template('agri_tech_news.html', title=title, news_items=NEWS_DATA)

@app.route('/case-study/<slug>')
@requires_auth
def case_study_detail(slug):
    case = CASE_STUDIES_DATA.get(slug)
    if not case:
        return "Case study not found", 404
    title = f'Krishi Mitr - {case["name"]}\'s Story'
    return render_template('case_study_detail.html', title=title, case=case)

@app.route('/profile')
@requires_auth
def profile():
    """Protected route - shows user profile with Elite UI"""
    title = 'Krishi Mitr - Your Profile'
    user = session.get('user')
    # Authlib userinfo is typically inside the token
    userinfo = user.get('userinfo') if user else None
    return render_template('profile.html', user=userinfo, title=title)

# render crop recommendation form page


@app.route('/crop-recommend')
@requires_auth
def crop_recommend():
    title = 'Krishi Mitr - Crop Recommendation'
    return render_template('crop.html', title=title)

# render fertilizer recommendation form page


@app.route('/fertilizer')
@requires_auth
def fertilizer_recommendation():
    title = 'Krishi Mitr - Fertilizer Suggestion'

    return render_template('fertilizer.html', title=title)

# render yield prediction form page
@app.route('/yield')
@requires_auth
def yield_prediction_form():
    title = 'Krishi Mitr - Yield Prediction'
    states, crops, seasons = get_unique_values()
    return render_template('yield.html', title=title, states=states, crops=crops, seasons=seasons)

# render sustainability advisor form page
@app.route('/sustainability')
@requires_auth
def sustainability_advisor():
    title = 'Krishi Mitr - Sustainability Advisor'
    crops = get_crop_list()
    return render_template('sustainability.html', title=title, crops=crops)

# render smart irrigation form page
@app.route('/irrigation')
@requires_auth
def irrigation_form():
    title = 'Krishi Mitr - Smart Irrigation'
    crops = get_crop_list()
    return render_template('irrigation.html', title=title, crops=crops)

# render disease prediction input page




# ===============================================================================================

# RENDER PREDICTION PAGES

# render crop recommendation result page


@app.route('/crop-predict', methods=['POST'])
@requires_auth
def crop_prediction():
    title = 'Krishi Mitr - Crop Recommendation'

    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])
        city = request.form.get("city")
        
        # 1. Fetch weather via utility (orchestrator handles the agentic logic next)
        weather = weather_fetch(city)
        if weather is None:
            return render_template('try_again.html', title=title)
        
        temperature, humidity = weather
        
        # 2. Call Crop Agent through Orchestrator
        payload = {
            "N": N, "P": P, "K": K, "ph": ph, "rainfall": rainfall,
            "temperature": temperature, "humidity": humidity
        }
        crop_res = orchestrator.dispatch("crop", payload)
        
        if crop_res["status"] == "ok":
            final_prediction = crop_res["data"]["recommended_crop"]
            # We can also call yield and market via orchestrator for the result page
            harvest_res = orchestrator.dispatch("yield", {
                "crop": final_prediction, "state": "Assam", "season": "Kharif", # Defaulting for demo
                "area": 1.0, "rainfall": rainfall, "fertilizer": 100, "pesticide": 10
            })
            
            # Pack agents for the UI (maintaining legacy template compatibility)
            ui_orchestration = {
                "agents": {
                    "weather": {"status": "ok", "data": {"temperature": temperature, "humidity": humidity}},
                    "crop": crop_res,
                    "yield": harvest_res
                }
            }
            # Log successful crop recommendation
            mongo.log_activity(
                activity_type="crop_recommendation",
                input_data=payload,
                result={"recommended_crop": final_prediction},
                metadata={"orchestration": ui_orchestration}
            )
            return render_template('crop-result.html', prediction=final_prediction, orchestration=ui_orchestration, title=title)
        return render_template('try_again.html', title=title)

# render fertilizer recommendation result page


@app.route('/fertilizer-predict', methods=['POST'])
@requires_auth
def fert_recommend():
    title = 'Krishi Mitr - Fertilizer Suggestion'

    payload = {
        "crop_name": str(request.form['cropname']),
        "N": int(request.form['nitrogen']),
        "P": int(request.form['phosphorous']),
        "K": int(request.form['pottasium'])
    }
    
    res = orchestrator.dispatch("fertilizer", payload)
    if res["status"] == "ok":
        # Log successful fertilizer recommendation
        mongo.log_activity(
            activity_type="fertilizer_suggestion",
            input_data=payload,
            result={"message": res["data"]["message"]},
            metadata={"key": res["data"].get("key")}
        )
        return render_template('fertilizer-result.html', recommendation=res["data"]["message"], title=title)
    return render_template('try_again.html', title=title)


@app.route('/disease-predict', methods=['GET', 'POST'])
@requires_auth
def disease_prediction():
    title = 'Krishi Mitr - Disease Detection'
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files.get('file')
        if not file:
            return render_template('disease.html', title=title)
        
        try:
            img = file.read()
            res = orchestrator.dispatch("disease", {"img_bytes": img})
            
            if res["status"] == "ok":
                prediction = res["data"]["label"]
                description = Markup(res["data"]["description"])
                
                # Log to DB
                mongo.log_activity(
                    activity_type="disease_detection",
                    input_data={"filename": file.filename},
                    result={"label": prediction, "description": res["data"]["description"]}
                )
                
                return render_template('disease-result.html', prediction=prediction, description=description, title=title)
        except Exception as e:
            print(f"Disease prediction error: {e}")
            return render_template('try_again.html', title=title)
            
    return render_template('disease.html', title=title)


@app.route('/dashboard')
@requires_auth
def dashboard():
    title = 'Krishi Mitr - Dashboard'
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
    # Fetch recent activity from MongoDB
    recent_activities = []
    try:
        logs = db.activity_logs.find().sort("timestamp", -1).limit(5)
        for log in logs:
            recent_activities.append({
                "type": log["activity_type"].replace("_", " ").title(),
                "time": log["timestamp"].strftime("%Y-%m-%d %H:%M"),
                "result": log["result"]
            })
    except Exception as e:
        print(f"ERR: Could not fetch recent activities: {e}")

    return render_template('dashboard.html', 
                           title=title, 
                           crop_stats=crop_stats, 
                           yield_stats=yield_summary,
                           recent_activities=recent_activities)


import google.generativeai as genai

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@app.route('/api/assistant', methods=['POST'])
def api_assistant():
    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).strip()
    
    if not user_message:
        return jsonify({"reply": "I'm listening! How can I help with your farming today?"})

    try:
        # Initialize the Gemini model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are 'FarmAI Assistant', an expert agricultural AI. Help Indian farmers with crop advice, soil health, weather impacts, and pest control. Keep responses concise, professional, and encouraging. Use simple English or Hinglish if appropriate. Always prioritize sustainable and safe farming practices."
        )
        
        # Generate response
        response = model.generate_content(user_message)
        reply = response.text.strip()
        
        # Log AI interaction
        mongo.log_activity(
            activity_type="ai_assistant_query",
            input_data={"message": user_message},
            result={"reply_length": len(reply)},
            metadata={"model": "gemini-1.5-flash"}
        )
        
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return jsonify({"reply": "I'm having a bit of trouble connecting to my brain right now. Please try again in a moment!"})


# ===============================================================================================
# render yield prediction result page
@app.route('/yield-predict', methods=['POST'])
@requires_auth
def yield_prediction_result():
    title = 'Krishi Mitr - Yield Prediction'
    if request.method == 'POST':
        payload = {
            "crop": request.form.get('crop'),
            "state": request.form.get('state'),
            "season": request.form.get('season'),
            "area": float(request.form.get('area', 1.0)),
            "rainfall": float(request.form.get('rainfall', 0.0)),
            "fertilizer": float(request.form.get('fertilizer', 0.0)),
            "pesticide": float(request.form.get('pesticide', 0.0))
        }

        res = orchestrator.dispatch("yield", payload)
        
        if res["status"] == "ok":
            return render_template('yield-result.html', prediction=res["data"], crop=payload["crop"], state=payload["state"], title=title)
        return render_template('try_again.html', title=title)


@app.route('/sustainability-predict', methods=['POST'])
@requires_auth
def sustainability_result():
    title = 'Krishi Mitr - Sustainability Advisor'
    if request.method == 'POST':
        payload = {
            "crop": request.form.get('crop'),
            "n": int(request.form.get('n', 0)),
            "p": int(request.form.get('p', 0)),
            "k": int(request.form.get('k', 0))
        }
        
        res = orchestrator.dispatch("sustainability", payload)
        if res["status"] == "ok":
            return render_template('sustainability-result.html', advice=res["data"], crop=payload["crop"], title=title)
        return render_template('try_again.html', title=title)


@app.route('/irrigation-predict', methods=['POST'])
@requires_auth
def irrigation_result():
    title = 'Krishi Mitr - Smart Irrigation'
    if request.method == 'POST':
        crop = request.form.get('crop')
        city = request.form.get('city')
        sowing_date = request.form.get('sowing_date')
        
        weather = weather_fetch(city)
        if weather:
            payload = {
                "crop": crop,
                "temp": weather[0],
                "humidity": weather[1],
                "sowing_date": sowing_date
            }
            res = orchestrator.dispatch("irrigation", payload)
            if res["status"] == "ok":
                return render_template('irrigation-result.html', irr=res["data"]["irrigation"], harvest=res["data"].get("harvest"), city=city, title=title)
        return render_template('try_again.html', title=title)

if __name__ == '__main__':
    app.run(debug=True)
