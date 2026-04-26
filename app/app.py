# Importing essential libraries and modules
print("DEBUG: app.py is starting...")

import sys
try:
    import openai
    if not hasattr(openai, 'DefaultHttpxClient'):
        class MockClient: pass
        openai.DefaultHttpxClient = MockClient
        print("DEBUG: Patched openai.DefaultHttpxClient")
except ImportError:
    pass

from flask import Flask, render_template, request, redirect, jsonify, session, url_for
import os
import re
from markupsafe import Markup
import numpy as np
import pandas as pd
from utils.disease import disease_dic
from utils.fertilizer import fertilizer_dic
import requests
from dotenv import load_dotenv
import config
import pickle
import io
import torch
from torchvision import transforms
from PIL import Image
from utils.model import ResNet9
from typing import Dict, Any
import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from utils.yield_logic import get_yield_prediction, get_unique_values, get_yield_trends
from utils.sustainability import get_rotation_advisor, get_crop_list, get_nutrient_spider_data
from utils.irrigation import get_irrigation_advice, get_harvest_timing, get_hydration_telemetry

# Load .env values even when running with `python app/app.py`.
load_dotenv()

# ==============================================================================================
from utils.db import get_db, mongo
from orchestrator import Orchestrator

# Initialize database and Orchestrator
db = get_db()
from models_registry import registry
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
    return registry.get_disease_model(len(disease_classes))

def load_crop_model():
    return registry.get_crop_model()


# =========================================================================================

# Custom functions for calculations



import requests
import config

def weather_fetch(city_name):
    """
    Fetch temperature and humidity using WeatherAPI with fallback logic.
    """
    if not city_name or city_name.lower() == "unknown":
        return 25.0, 75.0, True # Default values, is_fallback=True

    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": config.weather_api_key,
        "q": city_name
    }

    try:
        response = requests.get(base_url, params=params, timeout=5)
        data = response.json()
        if "error" in data:
            print(f"[Weather API Error for {city_name}]:", data["error"]["message"])
            return 25.0, 75.0, True
        
        temperature = data["current"]["temp_c"]
        humidity = data["current"]["humidity"]
        return temperature, humidity, False
    except Exception as e:
        print(f"[Weather API Exception]: {e}")
        return 25.0, 75.0, True




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
    weather_data = weather_fetch(city)
    if weather_data is None:
        result["message"] = "Weather data not available."
        return result
    temperature, humidity, is_fallback = weather_data
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
        result["message"] = "Missing parameters: " + ", ".join(missing)
        return result

    data = np.array([[float(n), float(phos), float(pot), float(temp), float(hum), float(ph), float(rain)]])
    model = load_crop_model()
    prediction = model.predict(data)[0]
    result["status"] = "ok"
    result["data"] = {
        "recommended_crop": str(prediction)
    }
    return result


def run_fertilizer_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    p = {k.lower(): v for k, v in payload.items()}
    crop_name = p.get("crop_name") or p.get("crop")
    N = int(p.get("n") or p.get("nitrogen", 0))
    P = int(p.get("p") or p.get("phosphorous", 0))
    K = int(p.get("k") or p.get("potassium", 0) or p.get("pottasium", 0))
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


def run_yield_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "agent": "yield",
        "status": "error",
        "data": {},
        "message": ""
    }
    p = {k.lower(): v for k, v in payload.items()}
    crop = p.get("crop") or p.get("crop_name")
    if not crop:
        result["message"] = "Missing parameter: crop"
        return result
    
    df = get_yield_data()
    if df is None:
        result["message"] = "Yield dataset not available."
        return result
    subset = df[df["Crop"].str.lower() == crop.lower()]
    if subset.empty:
        result["message"] = f"No yield data for crop: {crop}"
        return result
    mean_yield = float(subset["Yield"].mean())
    result["status"] = "ok"
    result["data"] = {
        "crop": crop,
        "avg_yield": mean_yield,
        "unit": "tons per hectare"
    }
    return result


# Load Market Trends Data
market_trends_df = None


def _normalize_market_trends_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize API/CSV market columns into the UI schema."""
    if df is None or df.empty:
        return pd.DataFrame()

    # Normalize incoming headers to simplify column matching.
    normalized = {}
    for col in df.columns:
        key = re.sub(r"[^a-z0-9]", "", str(col).strip().lower())
        normalized[key] = col

    def _pick(*aliases):
        for alias in aliases:
            if alias in normalized:
                return normalized[alias]
        return None

    col_map = {
        "state": _pick("state"),
        "district": _pick("district"),
        "market": _pick("market", "marketname"),
        "commodity": _pick("commodity", "crop"),
        "variety": _pick("variety"),
        "arrival_date": _pick("arrivaldate"),
        "min_price": _pick("minprice", "minimumprice"),
        "max_price": _pick("maxprice", "maximumprice"),
        "modal_price": _pick("modalprice"),
    }

    out = pd.DataFrame()
    for target_col, source_col in col_map.items():
        if source_col and source_col in df.columns:
            out[target_col] = df[source_col]
        else:
            out[target_col] = ""

    for col in ["state", "district", "market", "commodity", "variety", "arrival_date"]:
        out[col] = out[col].astype(str).str.strip()

    for col in ["min_price", "max_price", "modal_price"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out = out.dropna(subset=["modal_price"], how="all")
    out = out[out["arrival_date"].astype(str).str.len() > 0]
    out = out.drop_duplicates(
        subset=["state", "district", "market", "commodity", "variety", "arrival_date", "modal_price"]
    )
    return out


def _fetch_market_trends_from_api() -> pd.DataFrame:
    """Fetch market trends from data.gov.in API using env-driven config."""
    resource_id = os.getenv("MARKET_API_RESOURCE_ID", "").strip()
    api_key = os.getenv("MARKET_API_KEY", "").strip()
    if not resource_id or not api_key:
        return pd.DataFrame()

    base_url = f"https://api.data.gov.in/resource/{resource_id}"
    limit = int(os.getenv("MARKET_API_LIMIT", "1000"))
    max_pages = int(os.getenv("MARKET_API_MAX_PAGES", "50"))
    timeout_sec = int(os.getenv("MARKET_API_TIMEOUT", "20"))
    all_records = []

    for page in range(max_pages):
        offset = page * limit
        params = {
            "api-key": api_key,
            "format": "json",
            "offset": offset,
            "limit": limit,
        }
        try:
            response = requests.get(base_url, params=params, timeout=timeout_sec)
            response.raise_for_status()
            payload = response.json() if response.content else {}
        except Exception as exc:
            print(f"Market API fetch warning at page {page + 1}: {exc}")
            # Return what we already have, otherwise caller will fallback to CSV.
            break

        if payload.get("status") == "error":
            print(f"Market API returned error: {payload.get('message', 'unknown')}")
            break

        records = payload.get("records", [])
        if not records:
            break
        all_records.extend(records)
        if len(records) < limit:
            break

    if not all_records:
        return pd.DataFrame()

    api_df = pd.DataFrame(all_records)
    return _normalize_market_trends_df(api_df)


def get_market_trends_data():
    global market_trends_df
    if market_trends_df is not None:
        return market_trends_df

    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        market_csv_path = os.path.join(project_root, "Data-processed", "market_trend.csv")

        # Prefer live API data when config is present, fallback to local CSV.
        live_df = _fetch_market_trends_from_api()
        if not live_df.empty:
            market_trends_df = live_df
            try:
                market_trends_df.to_csv(market_csv_path, index=False)
            except Exception:
                pass
            return market_trends_df

        df = pd.read_csv(market_csv_path)
        market_trends_df = _normalize_market_trends_df(df)
    except Exception as e:
        print(f"Error loading market trends: {e}")
        market_trends_df = pd.DataFrame()
    return market_trends_df

def run_market_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "agent": "market",
        "status": "ok",
        "data": {},
        "message": ""
    }
    p = {k.lower(): v for k, v in payload.items()}
    crop = p.get("crop") or p.get("crop_name")
    state = p.get("state")
    
    if not crop:
        result["status"] = "error"
        result["message"] = "Missing parameter: crop"
        return result
    
    df = get_market_trends_data()
    if df.empty:
        result["status"] = "error"
        result["message"] = "Market price dataset not available."
        return result

    # Filter by crop (case-insensitive)
    subset = df[df["commodity"].str.lower() == crop.lower()]
    
    if state:
        state_subset = subset[subset["state"].str.lower() == state.lower()]
        if not state_subset.empty:
            subset = state_subset

    if subset.empty:
        result["status"] = "error"
        result["message"] = f"No market data found for {crop}."
        return result
    
    # Get latest/modal price
    latest = subset.iloc[0]
    modal = float(latest["modal_price"])
    max_p = float(subset["max_price"].max())
    min_p = float(subset["min_price"].min())
    
    # "Market Wisdom" logic
    advice = "HOLD"
    confidence = 0.7
    if modal >= max_p * 0.95:
        advice = "SELL NOW"
        message = f"Prices for {crop} are at a peak (₹{modal}). Historical data suggests a downward correction soon. Sell now for maximum ROI."
        confidence = 0.92
    elif modal <= min_p * 1.1:
        advice = "STRONG HOLD"
        message = f"Prices for {crop} are currently near historical lows. Hold your stock for at least 3-4 weeks for a predicted recovery."
        confidence = 0.85
    else:
        advice = "WATCHLIST"
        message = f"Market is currently stable for {crop}. Monitor for slight surges in the next 10 days before considering bulk liquidation."

    result["data"] = {
        "crop": str(latest["commodity"]),
        "state": str(latest["state"]),
        "district": str(latest["district"]),
        "market": str(latest["market"]),
        "modal_price": modal,
        "min_price": float(latest["min_price"]),
        "max_price": float(latest["max_price"]),
        "historical_max": max_p,
        "historical_min": min_p,
        "advice": advice,
        "advice_message": message,
        "confidence": confidence,
        "currency": "INR",
        "unit": "Quintal"
    }
    return result


# ===============================================================================================
# ------------------------------------ FLASK APP -------------------------------------------------

from utils.constants import INDIAN_STATES, AGRICULTURAL_CROPS, SOIL_TYPES, GROWTH_STAGES

# App Instance
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
    return redirect(url_for('dashboard')) # Always direct to dashboard in review mode

@app.route('/callback')
def callback():
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/')
def home():
    title = 'Krishi Mitr - Home'
    return render_template('index.html', title=title)

@app.route('/services')
def services():
    title = 'Krishi Mitr - Services'
    return render_template('services.html', title=title)

@app.route('/about')
def about():
    title = 'Krishi Mitr - About Us'
    market_df = get_market_trends_data()
    agent_count = len(getattr(orchestrator, "agents", {}) or {})
    if agent_count <= 0:
        agent_count = 5

    about_stats = {
        "support_hours": "24/7",
        "smart_agents": f"{agent_count}+",
        "records": int(len(market_df)) if not market_df.empty else 0,
        "states": int(market_df['state'].dropna().astype(str).str.strip().nunique()) if not market_df.empty else 0,
        "live_markets": int(market_df['market'].dropna().astype(str).str.strip().nunique()) if not market_df.empty else 0,
    }
    return render_template('about.html', title=title, about_stats=about_stats)

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


LIVE_AGRI_NEWS_FEEDS = [
    (
        "https://news.google.com/rss/search?q=agri+tech+india+when:7d&hl=en-IN&gl=IN&ceid=IN:en",
        "Technology",
    ),
    (
        "https://news.google.com/rss/search?q=agriculture+policy+india+when:7d&hl=en-IN&gl=IN&ceid=IN:en",
        "Policy",
    ),
    (
        "https://news.google.com/rss/search?q=farming+innovation+india+when:7d&hl=en-IN&gl=IN&ceid=IN:en",
        "Innovation",
    ),
]


def _strip_html(text):
    clean = re.sub(r"<[^>]+>", " ", str(text or ""))
    return " ".join(clean.split())


def _format_news_date(pub_date):
    value = str(pub_date or "").strip()
    if not value:
        return "Latest"
    try:
        return parsedate_to_datetime(value).strftime('%d %b %Y')
    except Exception:
        return value[:25]


def _fetch_live_agri_news(limit=7):
    image_cycle = ["future_tech.png", "hero_farm.png", "crop.png"]
    benefit_by_category = {
        "Technology": "Adopt practical tech ideas to reduce input cost and increase farm efficiency.",
        "Policy": "Use policy updates to plan crop, selling timing, and support-scheme decisions.",
        "Innovation": "Try small pilot changes in farm operations using latest innovation insights.",
    }

    items = []
    seen_titles = set()

    for feed_url, category in LIVE_AGRI_NEWS_FEEDS:
        try:
            response = requests.get(
                feed_url,
                timeout=6,
                headers={"User-Agent": "Mozilla/5.0 (KrishiMitrNewsBot/1.0)"},
            )
            response.raise_for_status()
            root = ET.fromstring(response.content)
        except Exception:
            continue

        for node in root.findall("./channel/item"):
            raw_title = node.findtext("title", default="")
            title = _strip_html(raw_title)
            if not title:
                continue

            title_key = title.lower()
            if title_key in seen_titles:
                continue

            seen_titles.add(title_key)
            link = (node.findtext("link", default="") or "").strip()
            summary_raw = node.findtext("description", default="")
            summary = _strip_html(summary_raw)
            if not summary:
                summary = "Recent agriculture update fetched from live feed."

            items.append(
                {
                    "title": title,
                    "category": category,
                    "date": _format_news_date(node.findtext("pubDate", default="")),
                    "summary": summary[:260],
                    "benefit": benefit_by_category.get(category, "Useful update for smarter crop and market decisions."),
                    "image": image_cycle[len(items) % len(image_cycle)],
                    "url": link,
                }
            )

            if len(items) >= limit:
                return items

    return items


def _build_market_signal_news():
    df = get_market_trends_data()
    if df.empty:
        return NEWS_DATA

    work = df.copy()
    work['arrival_dt'] = pd.to_datetime(work['arrival_date'], errors='coerce')
    work['modal_num'] = pd.to_numeric(work['modal_price'], errors='coerce')
    work = work.dropna(subset=['arrival_dt', 'modal_num'])
    if work.empty:
        return NEWS_DATA

    latest_dt = work['arrival_dt'].max()
    latest = work[work['arrival_dt'] == latest_dt]
    if latest.empty:
        return NEWS_DATA

    latest_label = latest_dt.strftime('%d %b %Y')

    top_crop = "Wheat"
    top_price = 0.0
    top_series = latest.groupby('commodity')['modal_num'].mean().sort_values(ascending=False)
    if not top_series.empty:
        top_crop = str(top_series.index[0])
        top_price = float(top_series.iloc[0])

    prev_dt = work[work['arrival_dt'] < latest_dt]['arrival_dt'].max()
    rising_crop = top_crop
    rising_pct = 0.0
    if pd.notna(prev_dt):
        prev = work[work['arrival_dt'] == prev_dt].groupby('commodity')['modal_num'].mean()
        now = latest.groupby('commodity')['modal_num'].mean()
        joined = pd.concat([prev.rename('prev'), now.rename('now')], axis=1).dropna()
        if not joined.empty:
            joined = joined[joined['prev'] > 0]
            if not joined.empty:
                joined['pct'] = ((joined['now'] - joined['prev']) / joined['prev']) * 100.0
                joined = joined.sort_values('pct', ascending=False)
                rising_crop = str(joined.index[0])
                rising_pct = float(joined.iloc[0]['pct'])

    market_count = int(latest['market'].dropna().astype(str).str.strip().nunique())
    state_count = int(latest['state'].dropna().astype(str).str.strip().nunique())

    return [
        {
            "title": f"{top_crop} leads modal prices on latest snapshot",
            "category": "Market Intelligence",
            "date": latest_label,
            "summary": f"Latest dataset snapshot shows {top_crop} near INR {int(round(top_price)):,} modal price, helping farmers plan selling windows better.",
            "benefit": "Identify better selling timing for your crop before mandi visit.",
            "image": "future_tech.png"
        },
        {
            "title": f"{rising_crop} shows strongest short-term movement",
            "category": "Price Signal",
            "date": latest_label,
            "summary": f"Compared with the previous available market date, {rising_crop} moved by {rising_pct:+.1f} percent in average modal price.",
            "benefit": "Use this trend to decide hold vs sell strategy for next few days.",
            "image": "hero_farm.png"
        },
        {
            "title": "Fresh mandi coverage updated across regions",
            "category": "Coverage",
            "date": latest_label,
            "summary": f"Latest market upload contains signals from {market_count} markets across {state_count} states for practical price comparison.",
            "benefit": "Cross-check nearby markets to avoid under-pricing your produce.",
            "image": "crop.png"
        }
    ]


def _build_dynamic_agri_news(limit=7):
    live_items = _fetch_live_agri_news(limit=limit)
    if len(live_items) >= 5:
        return live_items[:limit]

    market_items = _build_market_signal_news()
    if live_items:
        return (live_items + market_items)[:limit]

    return market_items[:limit] if market_items else NEWS_DATA[:limit]


def _build_dynamic_dashboard_market_data(limit=6):
    df = get_market_trends_data()
    if df.empty:
        return MARKET_DATA

    work = df.copy()
    work['arrival_dt'] = pd.to_datetime(work['arrival_date'], errors='coerce')
    work['modal_num'] = pd.to_numeric(work['modal_price'], errors='coerce')
    work = work.dropna(subset=['arrival_dt', 'modal_num'])
    if work.empty:
        return MARKET_DATA

    latest_dt = work['arrival_dt'].max()
    latest = work[work['arrival_dt'] == latest_dt]
    prev_dt = work[work['arrival_dt'] < latest_dt]['arrival_dt'].max()
    prev = work[work['arrival_dt'] == prev_dt] if pd.notna(prev_dt) else pd.DataFrame()

    latest_group = latest.groupby('commodity')['modal_num'].mean().sort_values(ascending=False)
    prev_group = prev.groupby('commodity')['modal_num'].mean() if not prev.empty else pd.Series(dtype='float64')

    items = []
    for crop, modal in latest_group.head(limit).items():
        prev_modal = float(prev_group.get(crop, 0.0) or 0.0)
        pct = ((float(modal) - prev_modal) / prev_modal * 100.0) if prev_modal > 0 else 0.0
        trend = "up" if pct > 0.15 else ("down" if pct < -0.15 else "flat")
        change = f"{pct:+.1f}%"
        spread_series = latest[latest['commodity'] == crop]
        volatility = pd.to_numeric(spread_series['max_price'], errors='coerce') - pd.to_numeric(spread_series['min_price'], errors='coerce')
        vol_score = float(volatility.dropna().mean()) if not volatility.dropna().empty else 0.0
        volume = "high" if vol_score >= 600 else ("moderate" if vol_score >= 250 else "low")

        items.append({
            "crop": str(crop),
            "price": f"₹{int(round(float(modal))):,}",
            "change": change,
            "trend": trend,
            "volume": volume,
        })

    return items or MARKET_DATA

@app.route('/market-trends')
@requires_auth
def market_trends():
    title = 'Krishi Mitr - Market Trends'
    selected_state = request.args.get('state', '').strip()
    selected_crop = request.args.get('crop', '').strip()

    def _normalize_text(value):
        # Normalize casing + repeated internal spaces so CSV text quirks do not break filters.
        return ' '.join(str(value).strip().lower().split())
    
    df = get_market_trends_data()
    
    # Extract unique values for dropdowns (display cleaned values)
    all_states = []
    all_crops = []
    if not df.empty:
        all_states = sorted({
            ' '.join(str(v).strip().split())
            for v in df['state'].dropna().astype(str).tolist()
            if str(v).strip()
        })
        all_crops = sorted({
            ' '.join(str(v).strip().split())
            for v in df['commodity'].dropna().astype(str).tolist()
            if str(v).strip()
        })
    all_markets = sorted(df['market'].dropna().astype(str).str.strip().unique().tolist()) if not df.empty else []
    latest_arrival = None
    if not df.empty and 'arrival_date' in df.columns:
        latest_arrival = pd.to_datetime(df['arrival_date'], errors='coerce').max()
    
    filtered_df = df
    if not df.empty:
        filtered_df = filtered_df.copy()
        filtered_df['state_key'] = filtered_df['state'].apply(_normalize_text)
        filtered_df['commodity_key'] = filtered_df['commodity'].apply(_normalize_text)
        selected_state_key = _normalize_text(selected_state) if selected_state else ''
        selected_crop_key = _normalize_text(selected_crop) if selected_crop else ''
        if selected_state:
            filtered_df = filtered_df[filtered_df['state_key'] == selected_state_key]
        if selected_crop:
            filtered_df = filtered_df[filtered_df['commodity_key'] == selected_crop_key]
            
    formatted_data = []
    if not filtered_df.empty:
        filtered_df = filtered_df.copy()
        filtered_df['arrival_dt'] = pd.to_datetime(filtered_df['arrival_date'], errors='coerce')
        filtered_df['modal_num'] = pd.to_numeric(filtered_df['modal_price'], errors='coerce')
        modal_values = filtered_df['modal_num'].dropna()
        q33 = float(modal_values.quantile(0.33)) if not modal_values.empty else 0.0
        q66 = float(modal_values.quantile(0.66)) if not modal_values.empty else 0.0

        # Get top 21 matches for a nice grid
        display_df = filtered_df.sort_values('arrival_dt', ascending=False, na_position='last').head(21)
        for _, row in display_df.iterrows():
            min_price = float(row.get('min_price', 0) or 0)
            max_price = float(row.get('max_price', 0) or 0)
            modal_price = float(row.get('modal_num', 0) or 0)

            history_mask = (
                (filtered_df['commodity_key'] == row.get('commodity_key', '')) &
                (filtered_df['state_key'] == row.get('state_key', ''))
            )
            history_df = filtered_df.loc[history_mask, ['arrival_dt', 'modal_num']].dropna().sort_values('arrival_dt')

            pct_change = 0.0
            if len(history_df) >= 2:
                prev_val = float(history_df.iloc[-2]['modal_num'] or 0)
                curr_val = float(history_df.iloc[-1]['modal_num'] or 0)
                if prev_val > 0:
                    pct_change = ((curr_val - prev_val) / prev_val) * 100.0

            change_label = f"{pct_change:+.1f}%"
            trend = "up" if pct_change > 0.15 else ("down" if pct_change < -0.15 else "flat")

            if modal_price <= 0:
                volume = "N/A"
            elif modal_price >= q66:
                volume = "High"
            elif modal_price >= q33:
                volume = "Moderate"
            else:
                volume = "Low"

            formatted_data.append({
                "crop": str(row.get("commodity", "Unknown")).strip(),
                "price": f"₹{int(modal_price):,}" if modal_price else "N/A",
                "state": str(row.get("state", "Unknown")).strip(),
                "district": str(row.get("district", "Unknown")).strip(),
                "market": str(row.get("market", "Unknown")).strip(),
                "variety": str(row.get("variety", "")).strip(),
                "arrival_date": str(row.get("arrival_date", "")).strip(),
                "min_price": f"₹{int(min_price):,}" if min_price else "N/A",
                "max_price": f"₹{int(max_price):,}" if max_price else "N/A",
                "spread": f"₹{int(max_price - min_price):,}" if max_price and min_price else "N/A",
                "change": change_label,
                "trend": trend,
                "volume": volume
            })

    present_rate_display = 'N/A'
    present_rate_date = 'N/A'
    rate_source_df = filtered_df if not filtered_df.empty else df
    if not rate_source_df.empty and 'modal_price' in rate_source_df.columns:
        rate_calc_df = rate_source_df.copy()
        if 'arrival_date' in rate_calc_df.columns:
            rate_calc_df['arrival_dt'] = pd.to_datetime(rate_calc_df['arrival_date'], errors='coerce')
            latest_rate_dt = rate_calc_df['arrival_dt'].max()
            if pd.notna(latest_rate_dt):
                rate_calc_df = rate_calc_df[rate_calc_df['arrival_dt'] == latest_rate_dt]
                present_rate_date = latest_rate_dt.strftime('%d %b %Y')

        modal_series = pd.to_numeric(rate_calc_df['modal_price'], errors='coerce').dropna()
        if not modal_series.empty:
            # Present market rate = average modal price from the latest available date.
            present_rate_display = f"₹{int(round(float(modal_series.mean()))):,}"

    summary = {
        "total_records": int(len(df)) if not df.empty else 0,
        "states_count": int(df['state'].dropna().astype(str).str.strip().nunique()) if not df.empty else 0,
        "commodities_count": int(df['commodity'].dropna().astype(str).str.strip().nunique()) if not df.empty else 0,
        "markets_count": int(df['market'].dropna().astype(str).str.strip().nunique()) if not df.empty else 0,
        "latest_arrival": latest_arrival.strftime('%d %b %Y') if latest_arrival is not None and not pd.isna(latest_arrival) else 'N/A',
        "present_rate": present_rate_display,
        "present_rate_date": present_rate_date
    }
    
    return render_template('market_trends.html', 
                           title=title, 
                           market_records=formatted_data,
                           market_data=formatted_data,
                           states=all_states,
                           crops=all_crops,
                           all_crops=all_crops,
                           all_markets=all_markets,
                           summary=summary,
                           selected_state=selected_state,
                           selected_crop=selected_crop)

@app.route('/api/market-trends')
def api_market_trends():
    """API for Next.js frontend or AJAX calls"""
    df = get_market_trends_data()
    if df.empty:
        return jsonify({"status": "error", "message": "No data unavailable"}), 404
    
    return jsonify({
        "status": "ok",
        "data": df.head(100).to_dict(orient='records')
    })

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
    return render_template('agri_tech_news.html', title=title, news_items=_build_dynamic_agri_news(limit=7))

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


@app.route("/agent/crop")
def crop_recommendation():
    return render_template('crop.html', 
                          states=INDIAN_STATES, 
                          crops=AGRICULTURAL_CROPS)

# render fertilizer recommendation form page


@app.route("/agent/fertilizer")
def fertilizer_recommendation():
    return render_template('fertilizer.html', crops=AGRICULTURAL_CROPS)

# render yield prediction form page
@app.route('/yield')
@requires_auth
def yield_prediction_form():
    title = 'Krishi Mitr - Yield Prediction'
    states, crops, seasons = get_unique_values()
    return render_template('yield.html', title=title, states=states, crops=crops, seasons=seasons)

# render sustainability advisor form page
@app.route("/agent/sustainability")
def sustainability_advisor():
    return render_template('sustainability.html', 
                          crops=AGRICULTURAL_CROPS, 
                          states=INDIAN_STATES, 
                          soil_types=SOIL_TYPES)

# render smart irrigation form page
@app.route("/agent/irrigation")
def irrigation_form():
    return render_template('irrigation.html', 
                          crops=AGRICULTURAL_CROPS, 
                          states=INDIAN_STATES, 
                          soil_types=SOIL_TYPES, 
                          growth_stages=GROWTH_STAGES)

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
        city = request.form.get("city", "").strip()
        
        # 1. Fetch weather via utility with fallback
        temperature, humidity, is_fallback = weather_fetch(city)
        warning = "Note: Using regional averages as real-time weather for your city was unavailable." if is_fallback else None
        
        # 2. Call Crop Agent through Orchestrator
        payload = {
            "N": N, "P": P, "K": K, "ph": ph, "rainfall": rainfall,
            "temperature": temperature, "humidity": humidity
        }
        crop_res = orchestrator.dispatch("crop", payload)
        
        if crop_res.get("status") == "ok":
            # Extract from new agentic format: res["result"]["agentic_loop"]["prediction"]["top_result"]
            try:
                final_prediction = crop_res["result"]["agentic_loop"]["prediction"]["top_result"]
            except (KeyError, TypeError):
                final_prediction = crop_res.get("result", {}).get("summary", {}).get("top_result", "Unknown")
            
            # Also call yield for the result page
            harvest_res = orchestrator.dispatch("yield", {
                "crop": final_prediction, "state": "Assam", "season": "Kharif",
                "area": 1.0, "rainfall": rainfall, "fertilizer": 100, "pesticide": 10
            })
            
            # Build yield data for template compatibility
            yield_data = {}
            if harvest_res.get("status") == "ok":
                try:
                    yield_top = harvest_res["result"]["agentic_loop"]["prediction"]["top_result"]
                    yield_explanation = harvest_res["result"]["agentic_loop"]["reflection"]["explanation"]
                except (KeyError, TypeError):
                    yield_top = "N/A"
                    yield_explanation = ""
                yield_data = {
                    "status": "ok",
                    "data": {
                        "avg_yield": yield_top,
                        "unit": "Quintal/Hectare",
                        "message": yield_explanation[:150]
                    }
                }
            
            # Pack agents for the UI (template-compatible format)
            ui_orchestration = {
                "agents": {
                    "weather": {"status": "ok", "data": {"temperature": temperature, "humidity": humidity, "risk_level": "low"}},
                    "crop": crop_res,
                    "yield": yield_data
                }
            }
            # Log successful crop recommendation
            mongo.log_activity(
                activity_type="crop_recommendation",
                input_data=payload,
                result={"recommended_crop": final_prediction},
                metadata={}
            )
            return render_template('crop-result.html', prediction=final_prediction, orchestration=ui_orchestration, title=title, warning=warning, input_data=payload)
        return render_template('try_again.html', title=title, error="We couldn't generate a crop recommendation. Please check your soil data.")
    return render_template('try_again.html', title=title, error="Invalid Request Method")

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
    if res.get("status") == "ok":
        # Extract from new agentic format
        try:
            explanation = res["result"]["agentic_loop"]["reflection"]["explanation"]
        except (KeyError, TypeError):
            explanation = res.get("result", {}).get("summary", {}).get("explanation", "Apply balanced NPK fertilizer.")
        
        # Convert raw newlines into HTML breaks for perfect clean formatting
        recommendation = Markup(explanation.replace('\n', '<br>'))
        
        # Log successful fertilizer recommendation
        mongo.log_activity(
            activity_type="fertilizer_suggestion",
            input_data=payload,
            result={"message": str(explanation)[:200]},
            metadata={}
        )
        return render_template('fertilizer-result.html', recommendation=recommendation, orchestration=res, title=title, input_data=payload, cropname=payload["crop_name"])
    return render_template('try_again.html', title=title, error="Fertilizer analysis interrupted. Please verify the crop name and nutrient levels.")


@app.route('/disease-predict', methods=['GET', 'POST'])
@requires_auth
def disease_prediction():
    title = 'Krishi Mitr - Disease Detection'
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files.get('file')
        if not file:
            return render_template('disease.html', title=title, error="No image uploaded.")
        
        try:
            img = file.read()
            res = orchestrator.dispatch("disease", {"img_bytes": img})
            
            if res.get("status") == "ok":
                # ... existing success logic ...
                try:
                    prediction = res["result"]["agentic_loop"]["prediction"]["top_result"]
                    explanation = res["result"]["agentic_loop"]["reflection"]["explanation"]
                except (KeyError, TypeError):
                    prediction = res.get("result", {}).get("summary", {}).get("top_result", "Unknown")
                    explanation = "Disease detected. Please consult an agricultural expert."
                
                description = Markup(explanation)
                
                # Log to DB
                mongo.log_activity(
                    activity_type="disease_detection",
                    input_data={"filename": file.filename},
                    result={"label": prediction, "description": str(explanation)[:200]}
                )
                
                return render_template('disease-result.html', prediction=prediction, description=description, title=title)
            else:
                # Extract real error from agentic response if possible
                anomalies = res.get("result", {}).get("agentic_loop", {}).get("observations", {}).get("anomalies", [])
                error_msg = res.get("message") or (anomalies[0] if anomalies else "The AI worker was unable to analyze this image. Please ensure it's a clear photo of a plant leaf.")
                return render_template('disease.html', title=title, error=error_msg)
        except Exception as e:
            print(f"Disease prediction error: {e}")
            return render_template('try_again.html', title=title, error="Neural vision system failed to process the image. Please ensure it's a clear photo of a plant leaf.")
            
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
    if db is not None:
        try:
            logs = db.activity_logs.find().sort("timestamp", -1).limit(5)
            for log in logs:
                recent_activities.append({
                    "type": log["activity_type"].replace("_", " ").title(),
                    "time": log["timestamp"].strftime("%Y-%m-%d %H:%M"),
                    "result": log["result"]
                })
        except Exception as e:
            # print(f"ERR: Could not fetch recent activities: {e}")
            pass

    return render_template('dashboard.html', 
                           title=title, 
                           crop_stats=crop_stats, 
                           yield_stats=yield_summary,
                           recent_activities=recent_activities,
                           market_data=_build_dynamic_dashboard_market_data())


from google import genai

# Configure AI Engine
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

@app.route('/api/assistant', methods=['POST'])
def api_assistant():
    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).strip()
    
    if not user_message:
        return jsonify({"reply": "I'm listening! How can I help with your farming today?"})

    if not client:
        return jsonify({"reply": "AI Engine API key missing. Please configure your environment."})

    try:
        # Generate response using new SDK
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_message,
            config={
                "system_instruction": "You are 'FarmAI Assistant', an expert agricultural AI. Help Indian farmers with crop advice, soil health, weather impacts, and pest control. Keep responses concise, professional, and encouraging. Use simple English or Hinglish if appropriate. Always prioritize sustainable and safe farming practices."
            }
        )
        reply = response.text.strip()
        
        # Log AI interaction
        mongo.log_activity(
            activity_type="ai_assistant_query",
            input_data={"message": user_message},
            result={"reply_length": len(reply)},
            metadata={"model": "gemini-2.0-flash"}
        )
        
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"AI Engine Error: {e}")
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

        # Use orchestrator for agentic fallback and reliability
        res = orchestrator.dispatch("yield", payload)
        
        if res.get("status") == "ok":
            agent_result = res.get("result", {})
            yield_data = {
                "yield_per_hectare": agent_result.get("yield_per_hectare", 0),
                "total_production": agent_result.get("total_production", 0),
                "unit": agent_result.get("agentic_loop", {}).get("prediction", {}).get("model_used", "Metric Tons"),
            }
            prediction_block = agent_result.get("agentic_loop", {}).get("prediction", {})
            prediction = {
                "yield_per_hectare": yield_data.get("yield_per_hectare", 0),
                "total_production": yield_data.get("total_production", 0),
                "unit": "Metric Tons",
                "message": agent_result.get("agentic_loop", {}).get("reflection", {}).get("explanation", f"Analysis complete for {payload['crop']} in {payload['state']}.")
            }
            
            # Log
            mongo.log_activity(
                activity_type="yield_prediction",
                input_data=payload,
                result=prediction,
                metadata={}
            )
            # Get historical trends for Plotly
            trends = get_yield_trends(payload["crop"], payload["state"])
            
            return render_template('yield-result.html', 
                                    prediction=prediction, 
                                    crop=payload["crop"], 
                                    state=payload["state"], 
                                    area=payload["area"],
                                    rainfall=payload["rainfall"],
                                    fertilizer=payload["fertilizer"],
                                    pesticide=payload["pesticide"],
                                    title=title, 
                                    trends=trends)
        return render_template('try_again.html', title=title, error="Insufficient data for yield prediction. The agent was unable to formulate a reliable estimate.")
        return render_template('try_again.html', title=title, error="Insufficient data for yield prediction in this region/crop combination.")


@app.route('/sustainability-predict', methods=['POST'])
@requires_auth
def sustainability_result():
    title = 'Krishi Mitr - Sustainability Advisor'
    if request.method == 'POST':
        crop = request.form.get('crop')
        try:
            n = int(request.form.get('n', 0))
            p = int(request.form.get('p', 0))
            k = int(request.form.get('k', 0))
            ph = float(request.form.get('ph', 6.5))
            organic = float(request.form.get('organic', 2.0))
            moisture = float(request.form.get('moisture', 15.0))
            solar = int(request.form.get('solar', 15))
        except (ValueError, TypeError):
            n, p, k, ph, organic, moisture, solar = 0, 0, 0, 6.5, 2.0, 15.0, 15
        
        region = request.form.get('region', 'Punjab')
        season = request.form.get('season', 'Kharif')
        soil_type = request.form.get('soil_type', 'Alluvial')
        
        # Use Agentic Orchestrator
        payload = {
            "crop": crop,
            "n": n, "p": p, "k": k,
            "ph": ph, "organic": organic, "moisture": moisture,
            "solar": solar, "region": region, "season": season, "soil_type": soil_type
        }
        
        res = orchestrator.dispatch("sustainability", payload)
        
        if res.get("status") == "ok":
            # Extract from agentic format
            try:
                advice = res["result"]["agentic_loop"]["reflection"]["explanation"]
                # For backward compatibility with template if needed
                legacy_advice = {
                    "next_crop_suggestions": res["result"]["agentic_loop"]["reflection"].get("key_factors", []),
                    "rotation_strategy": advice
                }
            except (KeyError, TypeError):
                legacy_advice = {"next_crop_suggestions": ["Diversified Veggies"], "rotation_strategy": "Maintain soil health."}

            # Log
            mongo.log_activity(
                activity_type="sustainability_advice",
                input_data=payload,
                result={"advice": str(advice)[:200]},
                metadata={}
            )
            # Get Spider Chart Data
            spider_data = get_nutrient_spider_data(n, p, k)
            
            return render_template('sustainability-result.html', advice=legacy_advice, orchestration=res, crop=crop, title=title, spider_data=spider_data)
        return render_template('try_again.html', title=title, error="Sustainability Agent was unable to formulate a strategy for this soil profile.")


@app.route('/irrigation-predict', methods=['POST'])
@requires_auth
def irrigation_result():
    title = 'Krishi Mitr - Smart Irrigation'
    if request.method == 'POST':
        crop = request.form.get('crop')
        city = request.form.get('city', "").strip()
        sowing_date = request.form.get('sowing_date')
        soil_type = request.form.get('soil_type')
        growth_stage = request.form.get('growth_stage')
        moi = float(request.form.get('moi', 25.0))
        
        weather_data = weather_fetch(city)
        if weather_data:
            temperature, humidity, is_fallback = weather_data
            
            # Use Agentic Orchestrator
            payload = {
                "crop": crop, "city": city, "sowing_date": sowing_date,
                "soil_type": soil_type, "growth_stage": growth_stage, "moi": moi,
                "temperature": temperature, "humidity": humidity
            }
            
            res = orchestrator.dispatch("irrigation", payload)
            
            if res.get("status") == "ok":
                # Legacy compatibility for templates
                try:
                    refl = res["result"]["agentic_loop"]["reflection"]
                    prediction = res["result"]["agentic_loop"]["prediction"]
                    status_str = res["result"].get("status", "MODERATE IRRIGATION RECOMMENDED")
                    
                    if "NO IRRIGATION" in status_str:
                        color = "success"
                        status_text = "Optimal"
                    elif "IMMEDIATE" in status_str:
                        color = "danger"
                        status_text = "Action Required"
                    else:
                        color = "info"
                        status_text = "Action Required"

                    irr_legacy = {
                        "crop": crop,
                        "weather": {"temp": temperature, "humidity": humidity},
                        "soil": soil_type,
                        "moi": moi,
                        "color": color,
                        "water_need": prediction.get("top_result", "0 Liters/Day"),
                        "status": status_text,
                        "message": refl.get("explanation", ""),
                        "simple_title": "Easy Water Guide",
                        "simple_summary": (
                            f"Water {crop} with about {prediction.get('top_result', '0 Liters/Day')} today. "
                            f"Best time: {prediction.get('best_irrigation_time', 'Early morning')}."
                        ),
                        "simple_action": (
                            "If the field is dry and hot, water now. If the soil feels moist, wait and check again later."
                        )
                    }
                except (KeyError, TypeError) as e:
                    irr_legacy = {
                        "crop": crop,
                        "weather": {"temp": temperature, "humidity": humidity},
                        "soil": soil_type,
                        "moi": moi,
                        "color": "info",
                        "water_need": "Moderate",
                        "status": "Stable",
                        "message": "Proceed with standard cycle. AI engine encountered temporary issue.",
                        "simple_title": "Easy Water Guide",
                        "simple_summary": "Water a little and check again later.",
                        "simple_action": "Use the normal watering schedule until the model is available again."
                    }
                
                harvest = get_harvest_timing(crop, sowing_date)
                
                # Log
                mongo.log_activity(
                    activity_type="irrigation_advice",
                    input_data=payload,
                    result=irr_legacy,
                    metadata={}
                )
                base_need_numeric = res.get("result", {}).get("water_required_liters", 10.0)
                hydration_data = get_hydration_telemetry(crop, base_need_numeric)
                
                return render_template('irrigation-result.html', irr=irr_legacy, orchestration=res, harvest=harvest, city=city, title=title, hydration_data=hydration_data)
            return render_template('try_again.html', title=title, error="Irrigation Agent telemetry timeout. Please verify sensor connectivity.")
        return render_template('try_again.html', title=title, error="Weather telemetry for this city is temporarily unavailable. Irrigation schedule cannot be safely generated.")

from flask_cors import CORS
CORS(app) # Enable CORS for all routes

# ===============================================================================================
# TRUE AGENTIC AI API ROUTES
# ===============================================================================================

@app.route('/api/agent/<agent_name>', methods=['POST'])
def api_specific_agent(agent_name):
    """Directly triggers a specific agent with the agentic loop."""
    payload = request.get_json(silent=True) or {}
    # For disease agent, handle image if sent as base64 or similar (simplified for this API)
    result = orchestrator.dispatch(agent_name, payload)
    return jsonify(result)

@app.route('/api/agent/smart', methods=['POST'])
def api_smart_agent():
    """Uses LLM to route the query to the best agent."""
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")
    payload = data.get("payload", {})
    if not query:
        return jsonify({"status": "error", "message": "No query provided"}), 400
    
    result = orchestrator.smart_dispatch(query, payload)
    return jsonify(result)

@app.route('/api/agent/full-analysis', methods=['POST'])
def api_full_analysis():
    """Runs all agents in a sequence for a complete farm report."""
    payload = request.get_json(silent=True) or {}
    results = orchestrator.full_analysis(payload)
    return jsonify({
        "status": "ok",
        "results": results,
        "shared_memory": orchestrator.memory.get_all()
    })

@app.route('/api/memory', methods=['GET'])
def api_get_memory():
    """Returns the current state of the shared agent memory."""
    return jsonify({
        "shared_memory": orchestrator.memory.get_all()
    })

# ===============================================================================================
# Chatbot Endpoints
# ===============================================================================================
from flask import Response, stream_with_context
from chatbot_logic import stream_chat_response, get_chatbot_status

@app.route('/chatbot', methods=['GET'])
def chatbot_page():
    return render_template('chatbot.html', chatbot_status=get_chatbot_status())


@app.route('/api/chatbot/status', methods=['GET'])
def chatbot_status():
    status = get_chatbot_status()
    overall_ok = bool(status.get('gemini_configured')) and bool(status.get('rag_ready'))
    return jsonify({
        "status": "ok" if overall_ok else "warning",
        "chatbot": status
    })

@app.route('/api/chatbot/stream', methods=['POST'])
def chatbot_stream():
    data = request.get_json(silent=True) or {}
    query = data.get('query', '')
    history = data.get('history', [])
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    return Response(stream_with_context(stream_chat_response(query, history)), mimetype='text/event-stream')

@app.route('/api/chatbot/feedback', methods=['POST'])
def chatbot_feedback():
    data = request.get_json(silent=True) or {}
    emoji = data.get('emoji')
    comment = data.get('comment')
    # Use standard python logging or just print
    print(f"Chatbot Feedback -> Emoji: {emoji}, Comment: {comment}", flush=True)
    with open('chatbot_feedback.log', 'a', encoding='utf-8') as f:
        f.write(f"Emoji: {emoji}, Comment: {comment}\\n")
    return jsonify({"status": "success"})

# ===============================================================================================

if __name__ == '__main__':
    # Disable reloader by default to prevent slow startup/memory issues on Windows
    app.run(debug=True, use_reloader=False)
