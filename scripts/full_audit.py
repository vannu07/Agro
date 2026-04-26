import os
import sys
import torch
import pandas as pd
import numpy as np
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from orchestrator import Orchestrator
from agents import (
    CropAgent, FertilizerAgent, DiseaseAgent, 
    YieldAgent, SustainabilityAgent, IrrigationAgent
)

def test_component(name, func):
    print(f"\n[TESTING] {name}...")
    try:
        result = func()
        if isinstance(result, dict) and (result.get("status") == "ok" or "top_result" in result or "recommended_crop" in result):
            print(f"PASSED: {name}")
            return True, result
        else:
            print(f"FAILED: {name}: {result}")
            return False, result
    except Exception as e:
        print(f"CRASHED: {name}: {e}")
        return False, str(e)

def run_audit():
    print("=== Farm-IQ Comprehensive Audit ===\n")
    orchestrator = Orchestrator()
    audit_results = {}

    # 1. Model Files Audit
    print("--- Model Files Audit ---")
    models = {
        "Disease Model": "models/plant_disease_model.pth",
        "Crop Model": "models/RandomForest.pkl"
    }
    for m_name, m_path in models.items():
        exists = os.path.exists(m_path)
        print(f"{m_name}: {'FOUND' if exists else 'NOT FOUND'} ({m_path})")
        audit_results[m_name] = exists

    # 2. Agent Tests (Direct via Agents)
    print("\n--- Agent Functional Tests ---")
    
    # Crop Agent
    def test_crop():
        agent = CropAgent()
        return agent.run({
            "nitrogen": 90, "phosphorous": 42, "potassium": 43,
            "temperature": 25, "humidity": 80, "ph": 6.5, "rainfall": 200
        })
    audit_results["Crop Agent"], _ = test_component("Crop Agent", test_crop)

    # Fertilizer Agent
    def test_fert():
        agent = FertilizerAgent()
        return agent.run({
            "crop_name": "rice", "N": 90, "P": 42, "K": 43
        })
    audit_results["Fertilizer Agent"], _ = test_component("Fertilizer Agent", test_fert)

    # Yield Agent
    def test_yield():
        agent = YieldAgent()
        return agent.run({
            "crop": "Rice", "state": "Assam", "season": "Kharif", "area": 1.0
        })
    audit_results["Yield Agent"], _ = test_component("Yield Agent", test_yield)

    # Sustainability Agent
    def test_sustain():
        agent = SustainabilityAgent()
        return agent.run({
            "crop": "Rice", "soil_type": "Alluvial", "n": 60, "p": 30, "k": 30
        })
    audit_results["Sustainability Agent"], _ = test_component("Sustainability Agent", test_sustain)

    # Irrigation Agent
    def test_irrigation():
        agent = IrrigationAgent()
        return agent.run({
            "crop": "Rice", "moi": 15, "temperature": 30, "humidity": 70
        })
    audit_results["Irrigation Agent"], _ = test_component("Irrigation Agent", test_irrigation)

    # Disease Agent (Simulated Small Image or Text)
    def test_disease():
        agent = DiseaseAgent()
        # Test text-based symptom analysis
        return agent.run({
            "symptoms": "Yellowing leaves and brown spots on tomato"
        })
    audit_results["Disease Agent (Text)"], _ = test_component("Disease Agent", test_disease)

    # 3. Chatbot Logic Test
    print("\n--- Chatbot Logic Test ---")
    from chatbot_logic import stream_chat_response
    def test_chat():
        gen = stream_chat_response("Tell me about Farm-IQ", [])
        responses = list(gen)
        return {"status": "ok"} if len(responses) > 0 else {"status": "failed"}
    audit_results["Chatbot RAG"], _ = test_component("Chatbot RAG", test_chat)

    # 4. Orchestrator Smart Dispatch Test
    if orchestrator.gemini:
        print("\n--- Orchestrator Smart Dispatch Test ---")
        def test_smart():
            return orchestrator.smart_dispatch("What crop should I plant if I have high nitrogen?", {})
        audit_results["Smart Dispatcher"], _ = test_component("Smart Dispatcher", test_smart)
    else:
        print("\n[SKIP] Smart Dispatcher (No Gemini API Key)")

    print("\n=== Audit Summary ===")
    total = len(audit_results)
    passed = sum(1 for v in audit_results.values() if v is True)
    print(f"Score: {passed}/{total}")
    if passed == total:
        print("ALL SYSTEMS OPERATIONAL")
    else:
        print("SOME SYSTEMS FAILED")

if __name__ == "__main__":
    run_audit()
