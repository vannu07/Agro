import torch
import sys
import os

# Add app to path to import ResNet9
sys.path.append(os.path.join(os.getcwd(), 'app'))
from utils.model import ResNet9

def verify():
    print("--- Farm-IQ GPU Verification ---")
    
    # 1. Check CUDA availability
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    
    if cuda_available:
        print(f"GPU Device Count: {torch.cuda.device_count()}")
        print(f"Current GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("Note: CUDA is not available. The project will continue to use CPU.")
        print("If you have an NVIDIA GPU, ensure the latest drivers and CUDA toolkit are installed.")
    
    device = torch.device('cuda' if cuda_available else 'cpu')
    print(f"Target Device: {device}")
    
    # 2. Test Model Loading on Device
    disease_classes_len = 38 # Standard for this project
    disease_model_path = 'models/plant_disease_model.pth'
    
    if os.path.exists(disease_model_path):
        try:
            print(f"Loading disease model on {device}...")
            model = ResNet9(3, disease_classes_len)
            model.load_state_dict(torch.load(disease_model_path, map_location=device, weights_only=False))
            model.to(device)
            model.eval()
            print("SUCCESS: Model loaded and transferred to device successfully.")
            
            # Dummy inference test
            dummy_input = torch.randn(1, 3, 256, 256).to(device)
            with torch.no_grad():
                output = model(dummy_input)
            print(f"SUCCESS: Inference test pass. Output shape: {output.shape}")
            
        except Exception as e:
            print(f"ERROR during model test: {e}")
    else:
        print(f"SKIP: Model file not found at {disease_model_path}")

    print("\n--- Recommendation ---")
    if not cuda_available:
        print("Suggestion: To further speed up presentation, close heavy background apps (Chrome tabs, other IDEs) to free up memory.")
    else:
        print("Suggestion: Optimization successful. The GPU is now handling heavy neural network calculations.")

if __name__ == "__main__":
    verify()
