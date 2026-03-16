"""
Crop Sustainability and Rotation Advisory Module

Provides functions for crop rotation advice, sustainability recommendations, and crop lists.
"""

from typing import Dict, List, Any
import pandas as pd


# Crop rotation compatibility matrix
CROP_ROTATION_GUIDE = {
    'Rice': {
        'good_rotations': ['Wheat', 'Legumes', 'Mustard'],
        'avoid': ['Rice'],
        'nitrogen_fixer': False,
        'soil_depleting': 'high'
    },
    'Wheat': {
        'good_rotations': ['Legumes', 'Maize', 'Sugarcane'],
        'avoid': ['Wheat', 'Barley'],
        'nitrogen_fixer': False,
        'soil_depleting': 'high'
    },
    'Maize': {
        'good_rotations': ['Legumes', 'Wheat', 'Rice'],
        'avoid': ['Maize'],
        'nitrogen_fixer': False,
        'soil_depleting': 'high'
    },
    'Cotton': {
        'good_rotations': ['Legumes', 'Groundnut', 'Wheat'],
        'avoid': ['Cotton'],
        'nitrogen_fixer': False,
        'soil_depleting': 'high'
    },
    'Sugarcane': {
        'good_rotations': ['Legumes', 'Wheat', 'Maize'],
        'avoid': ['Sugarcane'],
        'nitrogen_fixer': False,
        'soil_depleting': 'very_high'
    },
    'Potato': {
        'good_rotations': ['Legumes', 'Wheat', 'Rice'],
        'avoid': ['Potato', 'Tomato'],
        'nitrogen_fixer': False,
        'soil_depleting': 'medium'
    },
    'Tomato': {
        'good_rotations': ['Legumes', 'Wheat', 'Lettuce'],
        'avoid': ['Tomato', 'Potato'],
        'nitrogen_fixer': False,
        'soil_depleting': 'medium'
    },
    'Legumes': {
        'good_rotations': ['Rice', 'Wheat', 'Maize', 'Cotton'],
        'avoid': ['Legumes'],
        'nitrogen_fixer': True,
        'soil_depleting': 'very_low'
    },
    'Mustard': {
        'good_rotations': ['Rice', 'Legumes', 'Wheat'],
        'avoid': ['Mustard'],
        'nitrogen_fixer': False,
        'soil_depleting': 'low'
    },
    'Banana': {
        'good_rotations': ['Legumes', 'Ginger'],
        'avoid': ['Banana'],
        'nitrogen_fixer': False,
        'soil_depleting': 'high'
    }
}

# Sustainability practices for each crop
SUSTAINABILITY_PRACTICES = {
    'Rice': [
        'Alternate wetting and drying (AWD) reduces water use by 20-30%',
        'Use certified seeds to ensure genetic purity',
        'Practice crop rotation with legumes',
        'Implement integrated pest management (IPM)',
        'Avoid continuous monoculture'
    ],
    'Wheat': [
        'Conservation agriculture techniques reduce water and fertilizer',
        'Crop residue management prevents burning',
        'Rotate with legumes to restore nitrogen',
        'Use drip irrigation where possible',
        'Avoid excessive nitrogen application'
    ],
    'Maize': [
        'Intercrop with legumes to improve soil nitrogen',
        'Use mulching to conserve soil moisture',
        'Practice minimum tillage to reduce soil erosion',
        'Implement drip irrigation systems',
        'Rotate with nitrogen-fixing crops'
    ],
    'Cotton': [
        'Organic cotton reduces pesticide use by 90%',
        'Use integrated pest management strategies',
        'Practice crop rotation with food crops',
        'Promote pollinator-friendly practices',
        'Avoid monoculture plantations'
    ],
    'Sugarcane': [
        'Trash mulching improves soil organic matter',
        'Drip irrigation reduces water consumption significantly',
        'Intercrop with legumes between rows',
        'Bagasse-based composting enriches soil',
        'Rotate with food crops every 2-3 years'
    ],
    'Potato': [
        'Crop rotation with non-solanaceae crops',
        'Mulching prevents disease and conserves water',
        'Use resistant varieties to reduce pesticides',
        'Avoid acidic soils through lime application',
        'Practice staggered planting for continuous harvest'
    ],
    'Tomato': [
        'Drip irrigation improves water efficiency',
        'Mulching prevents fungal diseases',
        'Companion planting with basil repels pests',
        'Avoid excessive nitrogen that reduces flavor',
        'Practice crop rotation with brassicas'
    ],
    'Legumes': [
        'Host crop for nitrogen fixation in crop rotation',
        'Minimal fertilizer requirement',
        'Promotes soil structure improvement',
        'Drought-tolerant crop option',
        'Excellent for sustainable agriculture systems'
    ],
    'Mustard': [
        'Cold-season crop reduces water stress',
        'Minimal pest pressure in winter season',
        'Oil content improves with cool nights',
        'Good rotation crop for rice-wheat belt',
        'Short duration crop (90-100 days)'
    ],
    'Banana': [
        'Mulching with banana leaves maintains soil moisture',
        'Organic matter from plant debris enriches soil',
        'Shade crop integration (coconut intercropping)',
        'Water conservation through drip systems',
        'Integrated nutrient management systems'
    ]
}


def get_crop_list() -> List[str]:
    """Get list of all supported crops for sustainability advisor"""
    return sorted(list(CROP_ROTATION_GUIDE.keys()))


def get_rotation_advisor(current_crop: str, years_ahead: int = 3) -> Dict[str, Any]:
    """
    Get crop rotation recommendations for sustainable farming
    
    Args:
        current_crop: Current crop being grown
        years_ahead: Number of years to plan (default: 3)
    
    Returns:
        dict with rotation plan and recommendations
    """
    if current_crop not in CROP_ROTATION_GUIDE:
        return {
            'status': 'error',
            'message': f'Crop {current_crop} not in rotation guide',
            'available_crops': get_crop_list()
        }
    
    current_info = CROP_ROTATION_GUIDE[current_crop]
    good_rotations = current_info['good_rotations']
    nitrogen_fixer = current_info['nitrogen_fixer']
    soil_impact = current_info['soil_depleting']
    
    # Build rotation plan
    rotation_plan = [current_crop]
    
    # Prioritize nitrogen-fixing crops if current crop is soil-depleting
    if soil_impact in ['high', 'very_high'] and not nitrogen_fixer:
        # Prefer legumes
        legume_options = [c for c in good_rotations if CROP_ROTATION_GUIDE[c].get('nitrogen_fixer')]
        if legume_options:
            rotation_plan.append(legume_options[0])
        else:
            rotation_plan.append(good_rotations[0] if good_rotations else 'Legumes')
    else:
        rotation_plan.append(good_rotations[0] if good_rotations else 'Legumes')
    
    # Add alternating crops for remaining years
    remaining_rotations = [c for c in good_rotations if c not in rotation_plan]
    for i in range(years_ahead - 2):
        if remaining_rotations:
            rotation_plan.append(remaining_rotations[i % len(remaining_rotations)])
        else:
            rotation_plan.append(good_rotations[i % len(good_rotations)])
    
    # Ensure we have the right number of years
    rotation_plan = rotation_plan[:years_ahead]
    
    return {
        'status': 'ok',
        'current_crop': current_crop,
        'rotation_plan': rotation_plan,
        'nitrogen_fixer': nitrogen_fixer,
        'soil_impact': soil_impact,
        'avoid_crops': current_info['avoid'],
        'recommendations': SUSTAINABILITY_PRACTICES.get(current_crop, []),
        'benefits': get_rotation_benefits(current_crop, rotation_plan[1] if len(rotation_plan) > 1 else None)
    }


def get_rotation_benefits(current_crop: str, next_crop: str = None) -> List[str]:
    """
    Get benefits of rotating from current crop to next crop
    
    Args:
        current_crop: Current crop
        next_crop: Planned next crop
    
    Returns:
        List of benefit descriptions
    """
    benefits = []
    
    if not next_crop:
        return benefits
    
    current_info = CROP_ROTATION_GUIDE.get(current_crop, {})
    next_info = CROP_ROTATION_GUIDE.get(next_crop, {})
    
    # Check if rotation is recommended
    if next_crop in current_info.get('good_rotations', []):
        benefits.append(f'{next_crop} is an excellent rotation crop for {current_crop}')
    
    # Nitrogen fixation benefit
    if next_info.get('nitrogen_fixer') and current_info.get('soil_depleting') in ['high', 'very_high']:
        benefits.append(f'{next_crop} will restore soil nitrogen depleted by {current_crop}')
    
    # Soil structure benefit
    if current_info.get('soil_depleting') in ['high', 'very_high'] and next_info.get('nitrogen_fixer'):
        benefits.append('Improved soil health and organic matter content')
    
    # Disease control benefit
    if current_crop in next_info.get('avoid', []):
        benefits.append(f'Breaks pest and disease cycles specific to {current_crop}')
    else:
        benefits.append(f'{next_crop} has different pest pressures, reducing disease buildup')
    
    return benefits if benefits else ['Diversified farming system reduces risks']


def get_sustainability_score(crop: str, npk_values: Dict[str, int] = None) -> Dict[str, Any]:
    """
    Calculate sustainability score for a crop with given NPK values
    
    Args:
        crop: Crop name
        npk_values: dict with 'n', 'p', 'k' keys (optional)
    
    Returns:
        dict with sustainability metrics
    """
    if crop not in CROP_ROTATION_GUIDE:
        return {'status': 'error', 'message': f'Crop {crop} not found'}
    
    score = 80  # Base score
    
    # Check nitrogen fixer status
    if CROP_ROTATION_GUIDE[crop]['nitrogen_fixer']:
        score += 20
    
    # Adjust based on NPK balance if provided
    if npk_values:
        n = npk_values.get('n', 0)
        p = npk_values.get('p', 0)
        k = npk_values.get('k', 0)
        
        # Penalize excessive fertilizer use
        total_npk = n + p + k
        if total_npk > 300:
            score -= 20
        elif total_npk > 200:
            score -= 10
    
    # Soil depletion factor
    soil_impact = CROP_ROTATION_GUIDE[crop]['soil_depleting']
    if soil_impact == 'very_low':
        score += 15
    elif soil_impact == 'low':
        score += 10
    elif soil_impact == 'very_high':
        score -= 15
    
    return {
        'crop': crop,
        'sustainability_score': min(max(score, 0), 100),  # Clamp between 0-100
        'nitrogen_fixer': CROP_ROTATION_GUIDE[crop]['nitrogen_fixer'],
        'soil_impact': soil_impact,
        'practices': SUSTAINABILITY_PRACTICES.get(crop, [])
    }
