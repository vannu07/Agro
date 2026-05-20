import csv
import json
from collections import defaultdict, Counter
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'Data-processed', 'cropdata_updated.csv')
OUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'app', 'models', 'crop_stage_water_defaults.json')

# Mapping rules used in utils.irrigation.get_irrigation_advice
# Convert dataset label mean into a conservative fallback irrigation estimate.
# This is intentionally non-zero for most active growth stages.

def compute_defaults():
    stats = defaultdict(lambda: defaultdict(lambda: {'counts': Counter(), 'temps': []}))
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            crop = row.get('crop ID') or row.get('crop')
            stage = row.get('Seedling Stage') or row.get('growth_stage') or 'Unknown'
            try:
                temp = float(row.get('temp') or 0.0)
            except:
                temp = 0.0
            try:
                res = int(float(row.get('result') or 0))
            except:
                res = 0
            stats[crop][stage]['counts'][res] += 1
            stats[crop][stage]['temps'].append(temp)

    defaults = {}
    for crop, stages in stats.items():
        defaults[crop] = {}
        for stage, data in stages.items():
            counts = data['counts']
            temps = data['temps']
            avg_temp = sum(temps) / len(temps) if temps else 25.0
            mean_result = (sum(k * v for k, v in counts.items()) / sum(counts.values())) if counts else 0.0

            # Translate the label mean into a mm-like conservative estimate.
            # 0 -> low baseline, 1 -> moderate, 2 -> higher demand.
            if mean_result < 0.25:
                water_need = round(4.5 + (avg_temp * 0.03), 2)
                status = 'LOW IRRIGATION REQUIRED (Conservative)'
            elif mean_result < 0.55:
                water_need = round(6.5 + (avg_temp * 0.04), 2)
                status = 'MODERATE IRRIGATION RECOMMENDED'
            elif mean_result < 0.85:
                water_need = round(8.5 + (avg_temp * 0.05), 2)
                status = 'HIGHER IRRIGATION RECOMMENDED'
            else:
                water_need = round(10.0 + (avg_temp * 0.06), 2)
                status = 'IMMEDIATE IRRIGATION REQUIRED'
            defaults[crop][stage] = {
                'water_need': water_need,
                'status': status,
                'avg_temp': round(avg_temp,2),
                'samples': sum(counts.values()),
                'mean_result': round(mean_result, 4)
            }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8') as out:
        json.dump(defaults, out, indent=2)
    print('Wrote defaults to', OUT_PATH)

if __name__ == '__main__':
    compute_defaults()
