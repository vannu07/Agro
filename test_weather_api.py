import requests

api_key = "640da6f205ace73eecf74905cec73522"
city = "London"

print("--- Testing WeatherAPI.com ---")
url_wa = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
try:
    r = requests.get(url_wa)
    print(f"WeatherAPI Status: {r.status_code}")
    print(f"WeatherAPI Response: {r.text}")
except Exception as e:
    print(f"WeatherAPI Error: {e}")

print("\n--- Testing OpenWeatherMap.org ---")
url_owm = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}" # Wait, I used the same URL.
# OpenWeatherMap URL: api.openweathermap.org/data/2.5/weather?q={city name}&appid={API key}
url_owm = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
try:
    r = requests.get(url_owm)
    print(f"OpenWeatherMap Status: {r.status_code}")
    print(f"OpenWeatherMap Response: {r.text}")
except Exception as e:
    print(f"OpenWeatherMap Error: {e}")
