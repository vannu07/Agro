from .crop_agent import CropAgent
from .fertilizer_agent import FertilizerAgent
from .disease_agent import DiseaseAgent
from .yield_agent import YieldAgent
from .sustainability_agent import SustainabilityAgent
from .irrigation_agent import IrrigationAgent

# This allows for easy importing and a central registry if needed later
__all__ = [
    "CropAgent",
    "FertilizerAgent",
    "DiseaseAgent",
    "YieldAgent",
    "SustainabilityAgent",
    "IrrigationAgent"
]
