import joblib
import pickle
import torch
import os

models = [
    'app/models/RandomForest.pkl',
    'models/XGBoost.pkl',
    'models/SVMClassifier.pkl',
    'models/RandomForest.pkl',
    'models/NBClassifier.pkl',
    'models/DecisionTree.pkl',
    'models/plant_disease_model.pth',
    'app/models/plant_disease_model.pth'
]

def verify_model(path):
    if not os.path.exists(path):
        print(f"FAILED: {path} DOES NOT EXIST")
        return False
    
    try:
        if path.endswith('.pkl'):
            try:
                m = joblib.load(path)
                print(f"LOADED OK (joblib): {path} -> {type(m)}")
            except:
                with open(path, 'rb') as f:
                    m = pickle.load(f)
                print(f"LOADED OK (pickle): {path} -> {type(m)}")
        elif path.endswith('.pth'):
            m = torch.load(path, map_location='cpu', weights_only=False)
            print(f"LOADED OK (torch): {path} -> {type(m)}")
        return True
    except Exception as e:
        print(f"FAILED: {path} -> {str(e)}")
        return False

if __name__ == "__main__":
    results = []
    for model in models:
        results.append(verify_model(model))
    
    if all(results):
        print("\nALL MODELS VERIFIED SUCCESSFULLY")
    else:
        print("\nSOME MODELS FAILED TO LOAD")
