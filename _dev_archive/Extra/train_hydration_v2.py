import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score
import joblib
import os

# Set Paths
DATA_PATH = r'D:\Farm-IQ - Copy\Data-processed\cropdata_updated.csv'
MODEL_DIR = r'D:\Farm-IQ - Copy\models'
IMG_DIR = r'D:\Farm-IQ - Copy\app\static\images'

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

# 1. Load Data
df = pd.read_csv(DATA_PATH)

# 2. Preprocessing
le = LabelEncoder()
cat_cols = ['crop ID', 'soil_type', 'Seedling Stage']
encoders = {}
for col in cat_cols:
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

# New Feature
df['Moisture_Efficiency'] = df['MOI'] / (df['temp'] + 1)

X = df.drop('result', axis=1)
y = df['result']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 3. Models
models_dict = {
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(random_state=42),
    'XGBoost': XGBClassifier(random_state=42, eval_metric='mlogloss')
}

best_acc = 0
best_model = None
best_model_name = ""

for name, model in models_dict.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    print(f"{name} -> Accuracy: {acc:.4f}, F1: {f1:.4f}")
    
    if acc > best_acc:
        best_acc = acc
        best_model = model
        best_model_name = name

print(f"Champion identified: {best_model_name}")

# 4. Hyperparameter Tuning (Simplified for script speed)
print("Tuning Champion...")
if best_model_name == 'Random Forest':
    param_grid = {'n_estimators': [50, 100], 'max_depth': [10, None]}
    grid = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=3)
elif best_model_name == 'XGBoost':
    param_grid = {'n_estimators': [50, 100], 'max_depth': [3, 5]}
    grid = GridSearchCV(XGBClassifier(random_state=42, eval_metric='mlogloss'), param_grid, cv=3)
else:
    param_grid = {'n_estimators': [50, 100]}
    grid = GridSearchCV(GradientBoostingClassifier(random_state=42), param_grid, cv=3)

grid.fit(X_train_scaled, y_train)
final_model = grid.best_estimator_
print(f"Final Tuned Accuracy: {grid.best_score_:.4f}")

# 5. Export
joblib.dump(final_model, os.path.join(MODEL_DIR, 'hydration_model.pkl'))
joblib.dump(scaler, os.path.join(MODEL_DIR, 'hydration_scaler.pkl'))
joblib.dump(encoders, os.path.join(MODEL_DIR, 'hydration_encoders.pkl'))
joblib.dump(X.columns.tolist(), os.path.join(MODEL_DIR, 'hydration_features.pkl'))

print("All ML artifacts exported successfully to /models/.")
