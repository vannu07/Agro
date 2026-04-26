import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

# Paths (using raw strings for Windows)
DATA_PATH = r'D:\Farm-IQ - Copy\Data-processed\cropdata_updated.csv'
MODEL_DIR = r'D:\Farm-IQ - Copy\models'
os.makedirs(MODEL_DIR, exist_ok=True)

# Load
df = pd.read_csv(DATA_PATH)

# Preprocess
encoders = {}
cat_cols = ['crop ID', 'soil_type', 'Seedling Stage']
for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

X = df.drop('result', axis=1)
y = df['result']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train
classifiers = {
    'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
    'XGBoost': XGBClassifier(random_state=42),
    'GradientBoost': GradientBoostingClassifier(random_state=42)
}

results = {}
for name, clf in classifiers.items():
    clf.fit(X_train_scaled, y_train)
    y_pred = clf.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    results[name] = acc
    print(f"{name} Accuracy: {acc:.4f}")

best_model_name = max(results, key=results.get)
print(f"Champion Model: {best_model_name}")

# Export
joblib.dump(classifiers[best_model_name], os.path.join(MODEL_DIR, 'hydration_model.pkl'))
joblib.dump(scaler, os.path.join(MODEL_DIR, 'hydration_scaler.pkl'))
joblib.dump(encoders, os.path.join(MODEL_DIR, 'hydration_encoders.pkl'))
joblib.dump(X.columns.tolist(), os.path.join(MODEL_DIR, 'hydration_features.pkl'))

print("Artifacts exported successfully.")
