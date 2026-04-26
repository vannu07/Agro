import os


weather_api_key = os.getenv("WEATHER_API_KEY") or os.getenv("weather_api_key", "")
