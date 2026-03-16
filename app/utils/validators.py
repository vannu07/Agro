"""Input Validation and Sanitization Module"""

import re
from typing import Any, Dict, List, Tuple

class ValidationError(Exception):
    """Custom validation error"""
    pass

def sanitize_string(value: str, max_length: int = 500) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        raise ValidationError("Value must be a string")
    if len(value) > max_length:
        raise ValidationError(f"String exceeds {max_length} characters")
    value = value.strip()
    value = re.sub(r'<[^>]+>', '', value)  # Remove HTML tags
    return value

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_number(value: Any, min_val: float = None, max_val: float = None) -> Tuple[bool, float]:
    """Validate numeric input"""
    try:
        num = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"'{value}' is not a valid number")
    
    if min_val is not None and num < min_val:
        raise ValidationError(f"Value must be >= {min_val}")
    if max_val is not None and num > max_val:
        raise ValidationError(f"Value must be <= {max_val}")
    
    return True, num

def validate_crop_name(crop: str) -> bool:
    """Validate crop name"""
    valid_crops = [
        'Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane',
        'Potato', 'Tomato', 'Banana', 'Mustard', 'Legumes',
        'Apple', 'Grape', 'Orange', 'Pepper', 'Soybean'
    ]
    return crop in valid_crops

def validate_npk_values(n: Any, p: Any, k: Any) -> Tuple[bool, Dict]:
    """Validate NPK values"""
    errors = []
    try:
        n_val = float(n)
        if n_val < 0 or n_val > 300:
            errors.append("Nitrogen must be 0-300")
    except (ValueError, TypeError):
        errors.append("Invalid nitrogen value")
    
    try:
        p_val = float(p)
        if p_val < 0 or p_val > 300:
            errors.append("Phosphorous must be 0-300")
    except (ValueError, TypeError):
        errors.append("Invalid phosphorous value")
    
    try:
        k_val = float(k)
        if k_val < 0 or k_val > 300:
            errors.append("Potassium must be 0-300")
    except (ValueError, TypeError):
        errors.append("Invalid potassium value")
    
    if errors:
        raise ValidationError("; ".join(errors))
    
    return True, {'N': n_val, 'P': p_val, 'K': k_val}

def validate_ph_value(ph: Any) -> Tuple[bool, float]:
    """Validate soil pH value"""
    try:
        ph_val = float(ph)
        if ph_val < 0 or ph_val > 14:
            raise ValidationError("pH must be 0-14")
        return True, ph_val
    except (ValueError, TypeError):
        raise ValidationError("Invalid pH value")

def validate_rainfall(rainfall: Any) -> Tuple[bool, float]:
    """Validate rainfall value"""
    try:
        rainfall_val = float(rainfall)
        if rainfall_val < 0 or rainfall_val > 10000:
            raise ValidationError("Rainfall value invalid")
        return True, rainfall_val
    except (ValueError, TypeError):
        raise ValidationError("Invalid rainfall value")

def validate_temperature(temp: Any) -> Tuple[bool, float]:
    """Validate temperature"""
    try:
        temp_val = float(temp)
        if temp_val < -50 or temp_val > 60:
            raise ValidationError("Temperature outside range")
        return True, temp_val
    except (ValueError, TypeError):
        raise ValidationError("Invalid temperature value")

def validate_humidity(humidity: Any) -> Tuple[bool, float]:
    """Validate humidity percentage"""
    try:
        humidity_val = float(humidity)
        if humidity_val < 0 or humidity_val > 100:
            raise ValidationError("Humidity must be 0-100%")
        return True, humidity_val
    except (ValueError, TypeError):
        raise ValidationError("Invalid humidity value")

def validate_city_name(city: str) -> bool:
    """Validate city name"""
    if not isinstance(city, str):
        return False
    city = city.strip()
    pattern = r'^[a-zA-Z\s\-]{2,50}$'
    return bool(re.match(pattern, city))

__all__ = [
    'ValidationError', 'sanitize_string', 'validate_email', 'validate_number',
    'validate_crop_name', 'validate_npk_values', 'validate_ph_value',
    'validate_rainfall', 'validate_temperature', 'validate_humidity',
    'validate_city_name'
]
