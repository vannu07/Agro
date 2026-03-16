"""
Smart Irrigation and Harvest Timing Advisory Module

Provides irrigation scheduling and harvest timing predictions based on crop, weather, and timing.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import math

# Irrigation requirements for different crops (mm/day during growing season)
CROP_WATER_REQUIREMENTS = {
    'Rice': {'peak': 6.0, 'minimum': 2.0, 'critical_stage': 'Flowering to Grain filling'},
    'Wheat': {'peak': 4.5, 'minimum': 1.5, 'critical_stage': 'Grain filling'},
    'Maize': {'peak': 5.0, 'minimum': 1.8, 'critical_stage': 'Tasseling'},
    'Cotton': {'peak': 4.0, 'minimum': 1.2, 'critical_stage': 'Flowering'},
    'Sugarcane': {'peak': 5.5, 'minimum': 2.0, 'critical_stage': 'Vegetative growth'},
    'Potato': {'peak': 4.0, 'minimum': 1.5, 'critical_stage': 'Tuberization'},
    'Tomato': {'peak': 3.5, 'minimum': 1.5, 'critical_stage': 'Flowering and Fruiting'},
    'Banana': {'peak': 4.5, 'minimum': 2.0, 'critical_stage': 'Year-round'},
    'Mustard': {'peak': 2.5, 'minimum': 0.8, 'critical_stage': 'Flowering'},
    'Legumes': {'peak': 3.0, 'minimum': 1.0, 'critical_stage': 'Flowering and Pod filling'}
}

# Growing season duration in days
CROP_DURATION = {
    'Rice': 120,
    'Wheat': 150,
    'Maize': 120,
    'Cotton': 180,
    'Sugarcane': 360,
    'Potato': 90,
    'Tomato': 150,
    'Banana': 270,
    'Mustard': 100,
    'Legumes': 90
}

# Optimal temperature ranges for crops (Celsius)
CROP_TEMPERATURE_RANGE = {
    'Rice': {'min': 15, 'optimal': 28, 'max': 32},
    'Wheat': {'min': 10, 'optimal': 20, 'max': 25},
    'Maize': {'min': 15, 'optimal': 25, 'max': 30},
    'Cotton': {'min': 18, 'optimal': 27, 'max': 32},
    'Sugarcane': {'min': 18, 'optimal': 27, 'max': 32},
    'Potato': {'min': 10, 'optimal': 18, 'max': 25},
    'Tomato': {'min': 15, 'optimal': 25, 'max': 30},
    'Banana': {'min': 15, 'optimal': 25, 'max': 32},
    'Mustard': {'min': 5, 'optimal': 18, 'max': 25},
    'Legumes': {'min': 10, 'optimal': 22, 'max': 28}
}

# Humidity preferences (percentage)
CROP_HUMIDITY_PREFERENCE = {
    'Rice': {'min': 60, 'optimal': 75, 'max': 90},
    'Wheat': {'min': 40, 'optimal': 60, 'max': 75},
    'Maize': {'min': 50, 'optimal': 70, 'max': 85},
    'Cotton': {'min': 40, 'optimal': 65, 'max': 80},
    'Sugarcane': {'min': 50, 'optimal': 70, 'max': 85},
    'Potato': {'min': 50, 'optimal': 70, 'max': 85},
    'Tomato': {'min': 50, 'optimal': 70, 'max': 80},
    'Banana': {'min': 60, 'optimal': 75, 'max': 90},
    'Mustard': {'min': 40, 'optimal': 60, 'max': 75},
    'Legumes': {'min': 40, 'optimal': 65, 'max': 80}
}


def get_irrigation_advice(crop: str, temperature: float = None, humidity: float = None, 
                         soil_moisture: float = None) -> Dict[str, Any]:
    """
    Get irrigation advice based on crop and weather conditions
    
    Args:
        crop: Crop name
        temperature: Current temperature in Celsius (optional)
        humidity: Current humidity in percentage (optional)
        soil_moisture: Current soil moisture level 0-100 (optional)
    
    Returns:
        dict with irrigation recommendations
    """
    if crop not in CROP_WATER_REQUIREMENTS:
        return {
            'status': 'error',
            'message': f'Crop {crop} not in irrigation database',
            'available_crops': list(CROP_WATER_REQUIREMENTS.keys())
        }
    
    water_req = CROP_WATER_REQUIREMENTS[crop]
    temp_range = CROP_TEMPERATURE_RANGE[crop]
    humidity_pref = CROP_HUMIDITY_PREFERENCE[crop]
    
    # Calculate water requirement adjustment based on weather
    water_adjustment = 1.0
    
    if temperature is not None:
        # Higher temperature increases water demand
        if temperature > temp_range['optimal']:
            excess = temperature - temp_range['optimal']
            water_adjustment += excess * 0.05
        elif temperature < temp_range['optimal']:
            deficit = temp_range['optimal'] - temperature
            water_adjustment -= deficit * 0.03
    
    if humidity is not None:
        # Higher humidity reduces water demand due to less evaporation
        if humidity < humidity_pref['optimal']:
            water_adjustment += (humidity_pref['optimal'] - humidity) * 0.01
        else:
            water_adjustment -= (humidity - humidity_pref['optimal']) * 0.01
    
    adjusted_water = water_req['peak'] * water_adjustment
    
    # Irrigation schedule recommendation
    if soil_moisture is not None and soil_moisture < 40:
        irrigation_urgency = 'URGENT - Irrigate immediately'
        irrigation_interval = '1-2 days'
    elif soil_moisture is not None and soil_moisture < 60:
        irrigation_urgency = 'NEEDED - Irrigate within next 2-3 days'
        irrigation_interval = '3-4 days'
    else:
        irrigation_urgency = 'MONITOR - Check soil moisture regularly'
        irrigation_interval = '4-5 days'
    
    return {
        'status': 'ok',
        'crop': crop,
        'current_water_requirement_mm_per_day': round(adjusted_water, 2),
        'peak_requirement_mm_per_day': water_req['peak'],
        'minimum_requirement_mm_per_day': water_req['minimum'],
        'critical_stage': water_req['critical_stage'],
        'irrigation_urgency': irrigation_urgency,
        'recommended_interval_days': irrigation_interval,
        'optimal_temperature_celsius': temp_range['optimal'],
        'current_temperature_celsius': temperature,
        'optimal_humidity_percent': humidity_pref['optimal'],
        'current_humidity_percent': humidity,
        'advice': get_irrigation_tips(crop, temperature, humidity),
        'conservation_tips': get_water_conservation_tips(crop)
    }


def get_harvest_timing(crop: str, sowing_date: str = None) -> Dict[str, Any]:
    """
    Calculate estimated harvest date and pre-harvest preparations
    
    Args:
        crop: Crop name
        sowing_date: Sowing date in format 'YYYY-MM-DD' (optional)
    
    Returns:
        dict with harvest timing and preparations
    """
    if crop not in CROP_DURATION:
        return {
            'status': 'error',
            'message': f'Crop {crop} not in harvest database'
        }
    
    duration = CROP_DURATION[crop]
    
    harvest_dict = {
        'status': 'ok',
        'crop': crop,
        'growing_duration_days': duration,
    }
    
    if sowing_date:
        try:
            sowing = datetime.strptime(sowing_date, '%Y-%m-%d')
            harvest_date = sowing + timedelta(days=duration)
            harvest_dict['sowing_date'] = sowing_date
            harvest_dict['estimated_harvest_date'] = harvest_date.strftime('%Y-%m-%d')
            harvest_dict['days_until_harvest'] = (harvest_date - datetime.now()).days
            
            # Pre-harvest preparations
            days_left = (harvest_date - datetime.now()).days
            if days_left > 30:
                stage = 'Early growth phase'
                preparations = get_growth_stage_preparations(crop, 'early')
            elif days_left > 15:
                stage = 'Mid-growth phase'
                preparations = get_growth_stage_preparations(crop, 'mid')
            elif days_left > 5:
                stage = 'Late growth phase'
                preparations = get_growth_stage_preparations(crop, 'late')
            else:
                stage = 'Pre-harvest phase'
                preparations = get_growth_stage_preparations(crop, 'pre_harvest')
            
            harvest_dict['current_stage'] = stage
            harvest_dict['preparations'] = preparations
        
        except ValueError:
            harvest_dict['error'] = 'Invalid date format. Use YYYY-MM-DD'
    
    else:
        harvest_dict['estimated_harvest_date'] = f'~{duration} days from sowing'
        harvest_dict['note'] = 'Provide sowing date for exact harvest date calculation'
    
    return harvest_dict


def get_irrigation_tips(crop: str, temperature: float = None, humidity: float = None) -> List[str]:
    """Get specific irrigation tips for a crop"""
    tips = []
    
    crop_specific_tips = {
        'Rice': [
            'Maintain water level of 5-10 cm during vegetative growth',
            'Allow field to dry briefly during active tillering',
            'Increase water level during flowering stage',
            'Reduce water before harvest'
        ],
        'Wheat': [
            'Critical irrigation periods: CRI, boot, and milk stages',
            'Provide 4-5 irrigations for good yield in rainfed areas',
            'Avoid water stagnation during winter',
            'Irrigate at sunrise for better water retention'
        ],
        'Maize': [
            'Critical irrigation at V6-V8, tasseling, and grain formation',
            'Each irrigation should wet soil to 45 cm depth',
            'Avoid irrigation immediately after rains',
            'Drip irrigation saves 25-30% water'
        ],
        'Cotton': [
            'Avoid excessive irrigation during early growth',
            'Increase irrigation during flowering',
            'Stop irrigation 3 weeks before harvest',
            'Furrow method irrigation is most efficient'
        ],
        'Sugarcane': [
            'Requires 1200-1500 mm water annually',
            'Monthly irrigation of 50 mm each during dry season',
            'Avoid water stagnation causing fungal diseases',
            'Drip irrigation can reduce water use by 40%'
        ],
        'Potato': [
            'Critical at emergence and tuberization stages',
            'Provide 3-5 irrigations depending on rainfall',
            'Reduce irrigation at maturity to avoid blight',
            'Use sprinkler irrigation for uniform coverage'
        ],
        'Tomato': [
            'Drip irrigation is ideal - saves water and prevents diseases',
            'Water 2-3 times per week during fruiting',
            'Avoid wetting foliage to prevent fungal diseases',
            'Provide consistent moisture for uniform fruit quality'
        ],
        'Banana': [
            'Requires year-round moisture availability',
            'Monthly requirement: 100-150 mm',
            'Mulching helps retain moisture',
            'Drip system recommended in dry climates'
        ],
        'Mustard': [
            'Requires 3-4 irrigations in rabi season',
            'Critical at flowering stage',
            'Post-sowing irrigation improves germination',
            'Avoid waterlogging which causes root rot'
        ],
        'Legumes': [
            'Moderate water requirement',
            'Critical irrigation at flowering stage',
            'Avoid water stagnation',
            'Drip irrigation recommended for better economics'
        ]
    }
    
    tips.extend(crop_specific_tips.get(crop, []))
    
    # Temperature-based tips
    if temperature is not None:
        if temperature > 30:
            tips.append('High temperature detected - increase irrigation frequency to compensate for evaporation')
        elif temperature < 10:
            tips.append('Low temperature - reduce irrigation frequency to avoid waterlogging')
    
    # Humidity-based tips
    if humidity is not None:
        if humidity > 80:
            tips.append('High humidity - reduce irrigation to prevent fungal diseases')
        elif humidity < 40:
            tips.append('Low humidity - increase irrigation frequency to maintain soil moisture')
    
    return tips


def get_water_conservation_tips(crop: str) -> List[str]:
    """Get water conservation and efficiency tips"""
    conservation_tips = [
        'Use drip irrigation instead of flood irrigation (saves 30-40% water)',
        'Apply mulch to conserve soil moisture',
        'Improve soil organic matter through composting',
        'Practice conservation agriculture techniques',
        'Use moisture sensors for precise irrigation scheduling',
        'Schedule irrigation for early morning to reduce evaporation',
        'Collect and reuse agricultural runoff where possible',
        'Select drought-resistant varieties when available'
    ]
    
    crop_specific = {
        'Rice': 'Practice alternate wetting and drying (AWD) to save 20-30% water',
        'Wheat': 'Mulching can save 15-20% irrigation water',
        'Maize': 'Drip irrigation is ideal, saving up to 35% water',
        'Cotton': 'Furrow irrigation is more efficient than flood irrigation',
        'Sugarcane': 'Drip system reduces water use by 40%, improves yield',
        'Potato': 'Sprinkler irrigation provides uniform water distribution',
        'Tomato': 'Drip irrigation prevents foliar diseases and saves water',
        'Banana': 'Micro-irrigation systems are highly efficient',
        'Mustard': 'Soil moisture conservation through mulching',
        'Legumes': 'Minimal water requirement - use efficiently'
    }
    
    if crop in crop_specific:
        conservation_tips.append(crop_specific[crop])
    
    return conservation_tips


def get_growth_stage_preparations(crop: str, stage: str) -> List[str]:
    """Get preparations needed at different growth stages"""
    
    preparations_by_stage = {
        'early': [
            'Ensure proper soil preparation and field leveling',
            'Monitor for seed germination',
            'Apply pre-emergence herbicides if needed',
            'Check irrigation systems for proper function'
        ],
        'mid': [
            'Monitor nutrient status and apply top dressing if needed',
            'Scout for pests and diseases regularly',
            'Ensure timely weeding',
            'Adjust irrigation based on growth and weather'
        ],
        'late': [
            'Prepare harvesting equipment',
            'Monitor crop maturity indicators',
            'Reduce irrigation gradually',
            'Plan post-harvest activities'
        ],
        'pre_harvest': [
            'Arrange harvesting labor and equipment',
            'Check weather forecast for optimal harvest timing',
            'Prepare storage facilities',
            'Stop irrigation completely',
            'Schedule transportation and market logistics'
        ]
    }
    
    return preparations_by_stage.get(stage, [])
