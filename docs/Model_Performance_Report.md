# Model Performance & Comparison Report 📊

This report summarizes the performance of various machine learning models trained across the Krishi Mitr ecosystem.

## 1. Crop Recommendation Agent
**Goal**: Predict the best crop for a specific plot based on soil NPK, temperature, humidity, pH, and rainfall.

| Model | Accuracy (%) | Note |
| :--- | :---: | :--- |
| **Random Forest** | **99.09%** | **Champion Model** |
| Gaussian Naive Bayes | 99.09% | Highly competitive |
| XGBoost | 98.64% | - |
| Support Vector Machine (SVC) | 98.18% | - |
| Logistic Regression | 94.77% | - |
| Decision Tree | 90.68% | Baseline |

---

## 2. Hydration & Irrigation Agent
**Goal**: Predict water requirements based on soil moisture and growth stage.

| Model | Performance | Status |
| :--- | :---: | :--- |
| **Random Forest** | **Best Fit** | **Selected for Deployment** |
| Gradient Boosting | High Accuracy | - |
| Logistic Regression | Lower Accuracy | Used for comparison |

---

## 3. Precision Yield Forecaster
**Goal**: Estimate crop yield (tons/hectare) for harvest planning.

| Model | R² Score | Error (MSE) |
| :--- | :---: | :---: |
| **Random Forest Regressor** | **0.98** | **Low** |
| Ridge Regression | 0.85 | Moderate |

---

## 4. Sustain Master (Sustainability Agent)
**Goal**: Optimize resource usage for long-term soil health.

- **Champion Model**: **XGBoost Regressor**
- **Validation**: Achieved high precision in resource efficiency metrics.

---

## 5. Plant Disease Pathologist
**Goal**: Classify 38 different plant disease categories from leaf images.

- **Architecture**: **ResNet9 (Convolutional Neural Network)**
- **Accuracy**: **~99.2%** on the validation set.
- **Capabilities**: Real-time inference via PyTorch.

---

## Summary of Champion Models
1. **Crop Recommendation**: Random Forest
2. **Irrigation**: Random Forest
3. **Yield Forecasting**: Random Forest Regressor
4. **Sustainability**: XGBoost
5. **Disease Detection**: ResNet9
