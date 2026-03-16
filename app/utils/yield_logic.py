"""
Yield Prediction Logic Module

Provides functions for yield prediction, data processing, and unique value extraction.
"""

import pandas as pd
from typing import Tuple, List

# Cache for yield data
_yield_data_cache = None
_unique_values_cache = None


def get_yield_data():
    """
    Load and cache yield data from CSV
    Returns processed DataFrame with Area, Production, and calculated Yield
    """
    global _yield_data_cache
    if _yield_data_cache is not None:
        return _yield_data_cache
    
    try:
        # Try multiple possible paths for the dataset
        paths = [
            "Data-raw/raw_districtwise_yield_data.csv",
            "app/Data-raw/raw_districtwise_yield_data.csv",
            "Data/raw_districtwise_yield_data.csv"
        ]
        
        df = None
        for path in paths:
            try:
                df = pd.read_csv(path)
                break
            except FileNotFoundError:
                continue
        
        if df is None:
            # Create a sample dataset if file not found
            print("[WARNING] Yield data file not found. Using sample data.")
            df = create_sample_yield_data()
        
        # Process the data
        df = df.dropna(subset=["Area", "Production"])
        df = df[df["Area"] > 0]
        df["Yield"] = df["Production"] / df["Area"]
        
        _yield_data_cache = df
        return df
    
    except Exception as e:
        print(f"[ERROR] Failed to load yield data: {e}")
        return None


def create_sample_yield_data():
    """Create sample yield data for testing"""
    sample_crops = ['Rice', 'Wheat', 'Maize', 'Sugarcane', 'Cotton', 'Potato', 'Tomato']
    sample_states = ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Assam']
    sample_seasons = ['Kharif', 'Rabi']
    
    data = []
    import random
    random.seed(42)
    
    for crop in sample_crops:
        for state in sample_states:
            for season in sample_seasons:
                area = random.uniform(10, 100)
                production = random.uniform(100, 500)
                data.append({
                    'Crop': crop,
                    'State': state,
                    'Season': season,
                    'Area': area,
                    'Production': production,
                    'Yield': production / area
                })
    
    return pd.DataFrame(data)


def get_unique_values() -> Tuple[List[str], List[str], List[str]]:
    """
    Extract unique states, crops, and seasons from yield data
    Returns: (states, crops, seasons)
    """
    global _unique_values_cache
    if _unique_values_cache is not None:
        return _unique_values_cache
    
    df = get_yield_data()
    
    if df is None or df.empty:
        # Return default values if data unavailable
        return (
            ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Assam'],
            ['Rice', 'Wheat', 'Maize', 'Sugarcane', 'Cotton'],
            ['Kharif', 'Rabi']
        )
    
    states = []
    crops = []
    seasons = []
    
    if 'State' in df.columns:
        states = sorted(df['State'].unique().tolist())
    if 'Crop' in df.columns:
        crops = sorted(df['Crop'].unique().tolist())
    if 'Season' in df.columns:
        seasons = sorted(df['Season'].unique().tolist())
    
    _unique_values_cache = (states, crops, seasons)
    return _unique_values_cache


def get_yield_prediction(crop: str, state: str = None, season: str = None) -> dict:
    """
    Get yield prediction for a specific crop and location
    
    Args:
        crop: Crop name
        state: State name (optional)
        season: Season (Kharif/Rabi) (optional)
    
    Returns:
        dict with crop, average_yield, min_yield, max_yield
    """
    df = get_yield_data()
    
    if df is None or df.empty:
        return {
            'crop': crop,
            'average_yield': 0,
            'min_yield': 0,
            'max_yield': 0,
            'unit': 'tons/hectare',
            'error': 'No yield data available'
        }
    
    # Filter by crop
    subset = df[df['Crop'].str.lower() == crop.lower()]
    
    # Filter by state if provided
    if state and 'State' in df.columns:
        subset = subset[subset['State'].str.lower() == state.lower()]
    
    # Filter by season if provided
    if season and 'Season' in df.columns:
        subset = subset[subset['Season'].str.lower() == season.lower()]
    
    if subset.empty:
        return {
            'crop': crop,
            'average_yield': 0,
            'min_yield': 0,
            'max_yield': 0,
            'unit': 'tons/hectare',
            'error': f'No yield data found for {crop}'
        }
    
    yields = subset['Yield'].values
    
    return {
        'crop': crop,
        'state': state,
        'season': season,
        'average_yield': float(yields.mean()),
        'min_yield': float(yields.min()),
        'max_yield': float(yields.max()),
        'samples': int(len(yields)),
        'unit': 'tons/hectare'
    }


def estimate_harvest_quantity(crop: str, area_hectares: float, region: str = None) -> dict:
    """
    Estimate harvest quantity based on historical yield data
    
    Args:
        crop: Crop name
        area_hectares: Area in hectares
        region: Region/State (optional)
    
    Returns:
        dict with estimated_production and confidence
    """
    prediction = get_yield_prediction(crop, state=region)
    
    if 'error' in prediction:
        estimated_production = 0
        confidence = 0
    else:
        avg_yield = prediction.get('average_yield', 0)
        estimated_production = area_hectares * avg_yield
        confidence = min(prediction.get('samples', 1) / 10.0, 1.0)  # Max confidence at 10+ samples
    
    return {
        'crop': crop,
        'area_hectares': area_hectares,
        'estimated_production_tons': estimated_production,
        'confidence': confidence,
        'unit': 'tons'
    }
