import os
import pickle
import torch
from torchvision import transforms
from utils.model import ResNet9

class ModelRegistry:
    """
    Centralized lazy-loading registry for ML models.
    Prevents duplicate loading and ensures memory efficiency.
    """
    _instance = None
    _models = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
        return cls._instance

    def _get_path(self, relative_path):
        # Handle different relative paths from app/ or app/agents/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Target should be in [base_dir]/models/[path]
        return os.path.join(base_dir, relative_path)

    def get_crop_model(self):
        if "crop" not in self._models:
            path = self._get_path("models/RandomForest.pkl")
            if os.path.exists(path):
                print(f"[ModelRegistry] Loading Crop Model from {path}...")
                with open(path, "rb") as f:
                    self._models["crop"] = pickle.load(f)
            else:
                self._models["crop"] = None
        return self._models["crop"]

    def get_disease_model(self, classes_count=38):
        if "disease" not in self._models:
            path = self._get_path("models/plant_disease_model.pth")
            if os.path.exists(path):
                print(f"[ModelRegistry] Loading Disease Model from {path}...")
                model = ResNet9(3, classes_count)
                model.load_state_dict(torch.load(path, map_location=torch.device('cpu'), weights_only=False))
                model.eval()
                self._models["disease"] = model
            else:
                self._models["disease"] = None
        return self._models["disease"]

    def get_yield_model(self):
        if "yield" not in self._models:
            path = self._get_path("models/XGBoost.pkl")
            if os.path.exists(path):
                print(f"[ModelRegistry] Loading Yield Model from {path}...")
                with open(path, "rb") as f:
                    self._models["yield"] = pickle.load(f)
            else:
                self._models["yield"] = None
        return self._models["yield"]

# SINGLETON EXPORT
registry = ModelRegistry()
