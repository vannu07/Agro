import requests
import os

def weather_fetch(city_name):
    """
    Fetch temperature and humidity using Open-Meteo as the primary reliable source.
    Open-Meteo is free and does not require an API key.
    """
    if not city_name or city_name.lower() == "unknown":
        return 25.0, 75.0, True

    # 1. Primary Source: Open-Meteo (Free, High Reliability)
    try:
        # Geocode city name to coordinates
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url, timeout=3).json()
        if geo_res.get("results"):
            loc = geo_res["results"][0]
            lat, lon = loc["latitude"], loc["longitude"]
            
            # Fetch current weather
            meteo_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m"
            meteo_res = requests.get(meteo_url, timeout=3).json()
            if "current" in meteo_res:
                temp = float(meteo_res["current"]["temperature_2m"])
                hum = float(meteo_res["current"]["relative_humidity_2m"])
                print(f"[Open-Meteo Success]: Data for {city_name} ({lat}, {lon})")
                return temp, hum, False
    except Exception as e:
        print(f"[Open-Meteo Exception]: {e}")

    # 2. Secondary/Fallback: WeatherAPI.com (requires key)
    # Note: We import config here to avoid circular dependencies if needed, 
    # but usually utils are safe.
    from config import weather_api_key
    if weather_api_key:
        base_url = "http://api.weatherapi.com/v1/current.json"
        params = {"key": weather_api_key, "q": city_name}
        try:
            response = requests.get(base_url, params=params, timeout=4)
            data = response.json()
            if "error" not in data:
                return float(data["current"]["temp_c"]), float(data["current"]["humidity"]), False
        except Exception as e:
            print(f"[WeatherAPI Fallback Exception]: {e}")

    # 3. Final Fallback: Hardcoded Averages
    return 25.0, 75.0, True
