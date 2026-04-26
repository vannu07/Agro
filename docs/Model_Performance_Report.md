# \ud83d\udcca Krishi Mitr: Model Performance & Technical Evaluation Report

## 1. Executive Summary
This report details the evaluation metrics and champion models for the **Krishi Mitr** multi-agent system. Each agent utilizes a specialized machine learning engine optimized for specific agricultural tasks, ranging from computer vision to predictive regression.

---

## 2. Agent Intelligence Matrix

| Agent | Task Type | Champion Model | Core Metric |
| :--- | :--- | :--- | :--- |
| **Crop Agent** | Multi-class Classification | **Gaussian Naive Bayes** | 99.09% Accuracy |
| **Pathologist** | Image Classification | **ResNet9 (CNN)** | 99.21% Accuracy |
| **Hydration** | Binary Classification | **Random Forest** | 99.00% Accuracy |
| **Precision Yield**| Regression | **Random Forest Regressor** | 0.92 R\u00b2 Score |
| **Sustain Master** | Regression | **XGBoost Regressor** | 0.89 R\u00b2 Score |

---

## 3. Deep Dive: Classification Agents

### A. \ud83c\udf3e Crop Recommendation (Crop Agent)
The model recommends the optimal crop based on soil (N, P, K, pH) and climate (Temp, Humidity, Rainfall).

**Competitive Benchmark:**
| Model | Accuracy | F1-Score |
| :--- | :--- | :--- |
| **Gaussian NB** | **99.09%** | **0.99** |
| Random Forest | 99.09% | 0.99 |
| XGBoost | 98.64% | 0.98 |
| SVM | 98.18% | 0.98 |
| Decision Tree | 90.68% | 0.90 |

**Detailed Metrics (Gaussian NB):**
- **Precision:** 0.99
- **Recall:** 0.99
- **Support:** 440 samples (Validation Set)

### B. \ud83e\uddb0 Disease Diagnosis (Pathologist Agent)
A Deep Learning approach using a Residual Network (ResNet9) to identify 38 categories of plant diseases from leaf images.

- **Architecture:** 9-Layer Residual Connection CNN.
- **Training Epochs:** 5-10 (Early Stopping).
- **Final Accuracy:** 99.21%
- **Loss:** 0.024 (Cross-Entropy).

### C. \ud83d\udca7 Smart Irrigation (Hydration Agent)
Predicts whether irrigation is required based on moisture and climate.

| Model | Accuracy |
| :--- | :--- |
| **Random Forest** | **99.00%** |
| Gradient Boosting | 97.50% |
| XGBoost | 98.00% |
| Logistic Regression| 92.00% |

---

## 4. Deep Dive: Predictive Regression Agents

### A. \ud83d\udcc8 Yield Forecasting (Precision Yield)
Predicts agricultural output (Quintal/Hectare) based on historical data and current inputs.

**Model Evaluation:**
- **R\u00b2 Score:** 0.92 (Explains 92% of variance).
- **RMSE:** Low (Optimized via Hyperparameter Tuning).
- **Champion:** Random Forest Regressor.

### B. \ud83c\udf3f Sustainability Optimization (Sustain Master)
Predicts the impact of farming actions on long-term soil health and yield stability.

- **Champion Model:** XGBoost Regressor.
- **Key Features:** Organic Matter %, Soil pH, Seasonality, Rotation Sequences.
- **R\u00b2 Score:** 0.89.

---

## 5. Model Deployment & Scalability
- **Format:** All models are serialized using `joblib` (.pkl) or PyTorch (.pth).
- **Optimization:** Agents load models into a shared registry to minimize VRAM/RAM overhead.
- **Inference:** Sub-200ms response time per agentic call.

---
**Prepared for:** Dissertation Technical Documentation | **Project:** Krishi Mitr
