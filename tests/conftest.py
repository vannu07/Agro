"""
Shared pytest fixtures for Farm-IQ / Krishi Mitr test suite.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Ensure the app directory is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def mock_registry():
    """Mock the ModelRegistry so tests don't need actual .pkl/.pth model files."""
    with patch.dict('sys.modules', {
        'models_registry': MagicMock(),
        'utils.disease': MagicMock(disease_dic={}),
        'utils.model': MagicMock(),
    }):
        yield


@pytest.fixture
def sample_crop_payload():
    """Standard crop recommendation payload."""
    return {
        'nitrogen': 90,
        'phosphorous': 42,
        'pottasium': 43,
        'temperature': 20.87,
        'humidity': 82.0,
        'ph': 6.5,
        'rainfall': 202.93,
    }


@pytest.fixture
def sample_fertilizer_payload():
    """Standard fertilizer recommendation payload."""
    return {
        'nitrogen': 37,
        'phosphorous': 0,
        'pottasium': 0,
        'cropname': 'rice',
        'soiltype': 'Loamy',
    }


@pytest.fixture
def sample_yield_payload():
    """Standard yield prediction payload."""
    return {
        'state': 'Kerala',
        'crop': 'Rice',
        'season': 'Kharif',
        'area': 100,
        'rainfall': 2500,
        'fertilizer': 150,
        'pesticide': 50,
    }


@pytest.fixture
def sample_irrigation_payload():
    """Standard irrigation planning payload."""
    return {
        'crop_type': 'Rice',
        'soil_type': 'Clay',
        'area': 2.5,
        'temperature': 32,
        'humidity': 65,
        'rainfall': 100,
    }
