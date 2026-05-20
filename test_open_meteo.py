import requests

# Open-Meteo is a free API that doesn't require a key.
# We'll test with coordinates for a sample location (e.g., Delhi, India: 28.61, 77.20)
lat = 28.61
lon = 77.20
url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,precipitation&timezone=Asia/Kolkata"

print(f"--- Testing Open-Meteo API for Lat: {lat}, Lon: {lon} ---")
try:
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        print("SUCCESS: Open-Meteo API is working!")
        current = data.get('current', {})
        print(f"Temperature: {current.get('temperature_2m')}°C")
        print(f"Humidity: {current.get('relative_humidity_2m')}%")
        print(f"Precipitation: {current.get('precipitation')}mm")
        print(f"Wind Speed: {current.get('wind_speed_10m')}km/h")
    else:
        print(f"FAILED: Status code: {response.status_code}")
        print(f"Error: {data}")
except Exception as e:
    print(f"ERROR: {e}")
