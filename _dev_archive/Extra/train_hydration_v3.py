import json
import os
from collections import Counter

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier

DATA_PATH = r"D:\Farm-IQ - Copy\Data-processed\cropdata_updated.csv"
MODEL_DIR = r"D:\Farm-IQ - Copy\models"
REPORT_DIR = r"D:\Farm-IQ - Copy\Extra"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


def build_dataset() -> tuple[pd.DataFrame, pd.Series, dict[str, LabelEncoder]]:
    df = pd.read_csv(DATA_PATH)
    encoders: dict[str, LabelEncoder] = {}

    for col in ["crop ID", "soil_type", "Seedling Stage"]:
        encoder = LabelEncoder()
        df[col] = encoder.fit_transform(df[col].astype(str))
        encoders[col] = encoder

    # Feature engineering used by inference.
    df["Moisture_Efficiency"] = df["MOI"] / (df["temp"] + 1.0)
    df["Humidity_Temp_Ratio"] = df["humidity"] / (df["temp"] + 1.0)
    df["Dryness_Index"] = (100.0 - df["humidity"]) + (df["temp"] * 0.5)

    X = df.drop(columns=["result"])
    y = df["result"].astype(int)
    return X, y, encoders


def make_sample_weights(y: pd.Series) -> np.ndarray:
    counts = Counter(y.tolist())
    total = len(y)
    class_weight = {cls: total / (len(counts) * count) for cls, count in counts.items()}
    return np.asarray([class_weight[int(label)] for label in y], dtype=float)


def train_model(X: pd.DataFrame, y: pd.Series) -> dict:
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    sample_weights = make_sample_weights(y_train)

    model = XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        n_estimators=600,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        min_child_weight=1,
        reg_alpha=0.2,
        reg_lambda=1.2,
        gamma=0.0,
        tree_method="hist",
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train_scaled, y_train, sample_weight=sample_weights)

    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "weighted_f1": float(f1_score(y_test, y_pred, average="weighted")),
        "macro_f1": float(f1_score(y_test, y_pred, average="macro")),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, output_dict=True, zero_division=0),
        "probability_mean_max": float(np.mean(np.max(y_proba, axis=1))),
    }

    return {
        "model": model,
        "scaler": scaler,
        "X_columns": X.columns.tolist(),
        "metrics": metrics,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": y_pred,
    }


def main() -> None:
    X, y, encoders = build_dataset()
    result = train_model(X, y)

    joblib.dump(result["model"], os.path.join(MODEL_DIR, "hydration_model.pkl"))
    joblib.dump(result["scaler"], os.path.join(MODEL_DIR, "hydration_scaler.pkl"))
    joblib.dump(encoders, os.path.join(MODEL_DIR, "hydration_encoders.pkl"))
    joblib.dump(result["X_columns"], os.path.join(MODEL_DIR, "hydration_features.pkl"))

    report_path = os.path.join(REPORT_DIR, "hydration_retrain_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result["metrics"], f, indent=2)

    print("Retraining complete.")
    print(f"Accuracy: {result['metrics']['accuracy']:.4f}")
    print(f"Weighted F1: {result['metrics']['weighted_f1']:.4f}")
    print(f"Macro F1: {result['metrics']['macro_f1']:.4f}")
    print(f"Mean max probability: {result['metrics']['probability_mean_max']:.4f}")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
