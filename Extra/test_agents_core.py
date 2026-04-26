from app.orchestrator import Orchestrator
import os

def test_agent(orchestrator, name, payload):
    print(f"\n--- Testing Agent: {name} ---")
    result = orchestrator.dispatch(name, payload)
    print(f"Status: {result['status']}")
    if result['status'] == 'ok':
        print(f"Data: {result['data']}")
    else:
        print(f"Error Message: {result['message']}")
    return result

if __name__ == "__main__":
    # Ensure we are in project root for path resolutions
    orch = Orchestrator()

    # 1. Test Crop Agent (Mock data)
    test_agent(orch, "crop", {
        "N": 90, "P": 42, "K": 43, 
        "temperature": 20.8, "humidity": 82, 
        "ph": 6.5, "rainfall": 202
    })

    # 2. Test Fertilizer Agent
    test_agent(orch, "fertilizer", {
        "crop_name": "rice", "N": 50, "P": 30, "K": 30
    })

    # 3. Test Yield Agent
    test_agent(orch, "yield", {
        "crop": "Rice", "state": "Assam", "season": "Kharif",
        "area": 10, "rainfall": 1200, "fertilizer": 500, "pesticide": 20
    })

    # 4. Test Sustainability Agent
    test_agent(orch, "sustainability", {
        "crop": "rice", "n": 30, "p": 40, "k": 50
    })

    # 5. Test Irrigation Agent
    test_agent(orch, "irrigation", {
        "crop": "rice", "temp": 32, "humidity": 70, "sowing_date": "2026-01-01"
    })

    print("\n--- Agent Verification Complete ---")
