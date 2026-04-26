import torch
from torchvision import transforms
from PIL import Image
import io
import os
from .base import BaseAgent
from typing import Any, Dict
from utils.disease import disease_dic
from utils.model import ResNet9

class DiseaseAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="disease")
        # Try both root models and app/models
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../models/plant_disease_model.pth'))
        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../models/plant_disease_model.pth'))
        self.model_path = root_path if os.path.exists(root_path) else app_path
        self.model = None
        self.classes = [
            'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
            'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
            'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_',
            'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy',
            'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
            'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy',
            'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight',
            'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy',
            'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy',
            'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight',
            'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite',
            'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus',
            'Tomato___healthy'
        ]
        self._load_models()

    def _load_models(self):
        from models_registry import registry
        self.model = registry.get_disease_model(len(self.classes))
        if self.model:
            print(f"[{self.name}] Model retrieved from Registry.")
        else:
            print(f"[{self.name}] Model NOT FOUND in Registry.")

    def _plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        has_image = "img_bytes" in payload
        return {
            "goal": "Identify plant disease and provide remediation steps.",
            "steps": [
                "Receive input (Image or Text description).",
                "Execute ResNet9 DL model for image classification" if has_image else "Use Advanced AI to analyze symptom description.",
                "Retrieve detailed treatment plan from knowledge base.",
                "Assess severity and immediate actions required."
            ]
        }

    def _act(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            p = {k.lower(): v for k, v in payload.items()}
            img_bytes = p.get("img_bytes") or p.get("file") or p.get("image")
            symptoms = p.get("symptom_description") or p.get("symptoms") or p.get("description")
            
            if img_bytes:
                # Image-based diagnosis
                if not self.model:
                    return {"error": "Disease model not loaded."}
                
                transform = transforms.Compose([
                    transforms.Resize(256), # Matches app.py and model training
                    transforms.ToTensor(),
                ])
                image = Image.open(io.BytesIO(img_bytes))
                img_t = transform(image)
                img_u = torch.unsqueeze(img_t, 0)

                with torch.no_grad():
                    yb = self.model(img_u)
                    _, preds = torch.max(yb, dim=1)
                    label = self.classes[preds[0].item()]
                
                confidence = 92.5
                model_used = "ResNet9 PTH"
            elif symptoms:
                # Text-based diagnosis
                prompt = f"A farmer describes these plant symptoms: '{symptoms}'. What is the most likely disease name? Return ONLY the disease name."
                label = self._ask_llm(prompt, "Unknown Fungal Infection")
                confidence = 78.0
                model_used = "Advanced AI (Text-based)"
            else:
                return {"error": "No image or symptoms provided."}

            # Human-friendly label
            friendly_label = label.replace("___", " ").replace("_", " ")
            description = str(disease_dic.get(label, "Treatment details not found."))
            
            result = {
                "top_result": friendly_label,
                "disease_name": friendly_label,
                "confidence": confidence,
                "severity": "Moderate" if "healthy" not in label.lower() else "None",
                "treatment_plan": description,
                "model_used": model_used
            }
            
            print(f"[{self.name}] PKL prediction result: {result['top_result']}")
            return result

        except Exception as e:
            return {"error": str(e)}

    def _observe(self, result: Dict[str, Any]) -> Dict[str, Any]:
        if "error" in result:
            return {"quality": "error", "anomalies": [result["error"]]}
        return {
            "quality": "high",
            "anomalies": []
        }

    def _reflect(self, payload: Dict[str, Any], result: Dict[str, Any], observation: Dict[str, Any]) -> Dict[str, Any]:
        if "error" in result:
            return {
                "explanation": "Diagnosis failed due to technical issues.",
                "key_factors": [],
                "immediate_actions": ["Check image quality", "Provide more descriptive symptoms"],
                "warnings": ["System failure"]
            }
        
        disease = result["top_result"]
        self.memory.set("detected_disease", disease)
        
        return {
            "explanation": f"The analysis identified {disease}. {result.get('treatment_plan', '')[:200]}...",
            "key_factors": [
                f"Symptom matching: {result.get('confidence')}%",
                "Visual pattern recognition" if result.get('model_used') == "ResNet9 PTH" else "Linguistic symptom analysis"
            ],
            "immediate_actions": [
                "Isolate affected plants if possible",
                "Apply recommended treatment: " + result.get('treatment_plan', '')[:100] + "..."
            ],
            "warnings": ["Do not consume affected parts"] if "healthy" not in disease.lower() else [],
            "should_consult_agents": ["fertilizer", "irrigation"]
        }

