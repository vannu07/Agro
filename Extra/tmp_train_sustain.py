import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from xgboost import XGBRegressor, XGBClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

# 1. Load Data
data_path = r'D:\Farm-IQ - Copy\Data-raw\new_synthetic_agri_data_india_fixed.csv'
df = pd.read_csv(data_path)

# 2. Preprocessing
le_region = LabelEncoder()
le_season = LabelEncoder()
le_soil = LabelEncoder()
le_rotation = LabelEncoder()
le_crop = LabelEncoder()

df['Region_Enc'] = le_region.fit_transform(df['Region'].astype(str))
df['Season_Enc'] = le_season.fit_transform(df['Season'].astype(str))
df['Soil_Type_Enc'] = le_soil.fit_transform(df['Soil Type'].astype(str))
df['Rotation_Enc'] = le_rotation.fit_transform(df['Rotation Sequence'].astype(str))
df['Crop_Enc'] = le_crop.fit_transform(df['Crop_Planted (Action)'].astype(str))

encoders = {
    'Region': le_region,
    'Season': le_season,
    'Soil Type': le_soil,
    'Rotation Sequence': le_rotation,
    'Crop_Planted (Action)': le_crop
}

# Features for both: 
# Year, Region, Season, Soil Type, Soil pH, Soil Nitrogen, Soil Phosphorus, Soil Potassium, Soil Organic Matter (%), Soil Moisture (%), Avg Rainfall (mm), Solar Radiation Impact (BTU/sqft), Rotation Sequence, Crop_Planted (Action)
feature_cols = ['Year', 'Region_Enc', 'Season_Enc', 'Soil_Type_Enc', 'Soil pH', 'Soil Nitrogen', 'Soil Phosphorus', 'Soil Potassium', 'Soil Organic Matter (%)', 'Soil Moisture (%)', 'Avg Rainfall (mm)', 'Solar Radiation Impact (BTU/sqft)', 'Rotation_Enc']

# --- A. Recommendation Model (Classifier) ---
X_class = df[feature_cols]
y_class = df['Crop_Enc']

X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_class, y_class, test_size=0.2, random_state=42)
scaler_class = StandardScaler()
X_train_c_scaled = scaler_class.fit_transform(X_train_c)

clf = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
clf.fit(X_train_c_scaled, y_train_c)
print(f"✅ Classifier Accuracy: {accuracy_score(y_test_c, clf.predict(scaler_class.transform(X_test_c))):.4f}")

# --- B. Yield Prediction Model (Regressor) ---
# For yield, we also use the Crop_Planted as a feature
feature_cols_yield = feature_cols + ['Crop_Enc']
X_reg = df[feature_cols_yield]
y_reg = df['Simulated Yield (kg/ha)']

X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)
scaler_reg = StandardScaler()
X_train_r_scaled = scaler_reg.fit_transform(X_train_r)

reg = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
reg.fit(X_train_r_scaled, y_train_r)
print("✅ Regressor trained.")

# 4. Export artifacts
model_dir = r'D:\Farm-IQ - Copy\models'
os.makedirs(model_dir, exist_ok=True)

# Exporting everything with clear names
joblib.dump(clf, os.path.join(model_dir, 'sustain_recommend_model.pkl'))
joblib.dump(reg, os.path.join(model_dir, 'sustain_yield_model.pkl'))
joblib.dump(scaler_class, os.path.join(model_dir, 'sustain_class_scaler.pkl'))
joblib.dump(scaler_reg, os.path.join(model_dir, 'sustain_reg_scaler.pkl'))
joblib.dump(encoders, os.path.join(model_dir, 'sustain_encoders.pkl'))
joblib.dump({'class': feature_cols, 'reg': feature_cols_yield}, os.path.join(model_dir, 'sustain_features.pkl'))

print("🚀 Sustainability ML System Exported Successfully.")
