# Predictive Machine Learning Engine Documentation

## 🤖 Driver Underperformance Risk Prediction Model

### 1. Problem Statement
Identify drivers who are at risk of underperforming (low customer rating, low revenue generation, or low trip completion) to enable proactive coaching and operational intervention.

### 2. Feature Engineering (`agentic_ai/ml/feature_engineering.py`)
Features extracted from `gold.dim_driver` and `gold.fact_trip`:
- `rating`: Driver customer rating (numeric 1.0 - 5.0)
- `total_trips`: Total completed trips count
- `total_revenue`: Aggregate trip fare revenue ($)
- `average_fare`: Mean fare per trip ($)
- `average_distance`: Mean trip distance (miles)
- `average_duration`: Mean trip duration (minutes)

Target Label (`underperformance_risk`):
- `1` (High Risk) if rating is below median threshold
- `0` (Normal) otherwise

### 3. Model Architecture & Persistence (`train_model.py`)
- Algorithm: `scikit-learn` `RandomForestClassifier` (100 estimators, max depth 5).
- Model artifact saved to: `models/driver_underperformance_model.joblib`.
- Metadata artifact saved to: `models/driver_underperformance_meta.json`.

### 4. Inference Tool (`agentic_ai/tools/ml_tool.py`)
- `predict_driver_risk(driver_id)`: Retrieves driver features from Gold warehouse, executes model inference, and returns risk probability (0.0 to 1.0) and risk level (High, Medium, Low).
