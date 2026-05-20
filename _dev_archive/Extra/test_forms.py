import requests

pages = {
    "Crop": "/crop-recommend",
    "Fertilizer": "/fertilizer",
    "Disease": "/disease-predict",
    "Yield": "/yield-prediction",
    "Sustainability": "/sustainability",
    "Irrigation": "/irrigation",
}

for name, path in pages.items():
    try:
        r = requests.get(f"http://127.0.0.1:5000{path}", timeout=5)
        has_solid_input = "0f172a" in r.text or "crop-input" in r.text or "f-input" in r.text or "y-input" in r.text or "s-input" in r.text or "i-input" in r.text or "upload-zone" in r.text
        print(f"{name}: {r.status_code} | Solid inputs: {has_solid_input} | Size: {len(r.text)}")
    except Exception as e:
        print(f"{name}: ERROR - {e}")
