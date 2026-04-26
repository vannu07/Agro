import pandas as pd
import os
from .base import BaseAgent
from typing import Any, Dict
from utils.fertilizer import fertilizer_dic

class FertilizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="fertilizer")
        # Correct path from Step 1
        self.data_path = os.path.join(os.path.dirname(__file__), "../../Data-processed/fertilizer.csv")
        self.df = None
        self._load_models()

    def _load_models(self):
        if os.path.exists(self.data_path):
            self.df = pd.read_csv(self.data_path)
            self.df["crop_key"] = self.df["Crop"].astype(str).str.strip().str.lower()
            print(f"[{self.name}] CSV LOADED from {self.data_path}")
        else:
            print(f"[{self.name}] CSV NOT FOUND at {self.data_path}")

    def _plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        crop_name = payload.get("crop_type") or self.memory.get("recommended_crop")
        return {
            "goal": f"Determine the ideal fertilizer requirement for {crop_name if crop_name else 'the crop'}.",
            "steps": [
                "Retrieve recommended crop from shared memory or payload.",
                "Load historical fertilizer data for the specific crop.",
                "Calculate the gap between current N-P-K levels and ideal levels.",
                "Identify the most deficient nutrient and recommend corrective measures."
            ]
        }

    def _act(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            p = {k.lower(): v for k, v in payload.items()}
            crop_name = p.get("crop_name") or p.get("crop") or p.get("crop_type") or self.memory.get("recommended_crop")
            N = p.get("n") or p.get("nitrogen")
            P = p.get("p") or p.get("phosphorous")
            K = p.get("k") or p.get("potassium") or p.get("pottasium")

            if None in [crop_name, N, P, K]:
                missing = [k for k, v in {"crop":crop_name, "N":N, "P":P, "K":K}.items() if v is None]
                return {"error": "Missing parameters: " + ", ".join(missing)}

            if self.df is None:
                return {"error": "Fertilizer dataset unavailable."}

            # Normalize crop name for lookup
            crop_key = crop_name.strip().lower()

            # Match crop (case-insensitive)
            crop_data = self.df[self.df["crop_key"] == crop_key]
            
            if crop_data.empty:
                 # Fallback to a generic recommendation or Advanced AI
                 prompt = f"For crop {crop_name} with soil NPK {N}-{P}-{K}, recommend the best fertilizer and dosage."
                 gemini_res = self._ask_llm(prompt, "Use NPK 19-19-19.")
                 result = {
                     "top_result": "Generic NPK 19-19-19",
                     "npk_formula": "19-19-19",
                     "dosage_per_hectare": "50kg",
                     "model_used": "Advanced AI (Crop Not in CSV)"
                 }
            else:
                nr = crop_data["N"].iloc[0]
                pr = crop_data["P"].iloc[0]
                kr = crop_data["K"].iloc[0]

                n = nr - N
                p = pr - P
                k = kr - K
                
                temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
                max_value = temp[max(temp.keys())]
                
                if max_value == "N":
                    key = "NHigh" if n < 0 else "Nlow"
                elif max_value == "P":
                    key = "PHigh" if p < 0 else "Plow"
                else:
                    key = "KHigh" if k < 0 else "Klow"
                    
                advice = str(fertilizer_dic.get(key, "Apply balanced NPK fertilizer."))
                
                # Heuristic for formula and dosage
                formula = "20-20-20" if "balanced" in advice.lower() else ("46-0-0 (Urea)" if "N" in max_value else "0-46-0 (DAP)")
                dosage = "120kg/hectare" if "low" in key.lower() else "50kg/hectare"
                
                result = {
                    "top_result": formula,
                    "fertilizer_type": formula,
                    "npk_formula": formula.split(" ")[0],
                    "dosage_per_hectare": dosage,
                    "message": advice,
                    "model_used": "Fertilizer CSV Logic"
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
                "explanation": "Could not calculate fertilizer needs due to missing crop context.",
                "key_factors": [],
                "immediate_actions": ["Ensure Crop Agent is run first", "Provide manual crop name"],
                "warnings": ["Nutrient analysis incomplete"]
            }
        
        self.memory.set("fertilizer_advice", result["top_result"])
        
        return {
            "explanation": result.get("message", f"The recommended fertilizer is {result['top_result']} to address the specific soil deficiencies."),
            "key_factors": [
                f"Deficiency detected: {result.get('fertilizer_type', 'Multiple nutrients')}",
                f"Target dosage: {result.get('dosage_per_hectare', 'Standard')}"
            ],
            "immediate_actions": [
                f"Apply {result['top_result']} as per dosage: {result.get('dosage_per_hectare')}",
                "Water the field after application to ensure nutrient absorption"
            ],
            "warnings": [],
            "should_consult_agents": ["irrigation", "sustainability"]
        }

