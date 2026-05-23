# DPVI Parkinson's Disease System

FastAPI + React based longitudinal Parkinson’s disease
progression analysis system using:

- Disease Progression Volatility Index (DPVI)
- Longitudinal progression modeling
- Explainable AI analytics
- Weighted DPVI optimization
- Full DPVI vs Weighted DPVI comparison
- Confusion matrix and model metrics
- Risk classification dashboard

---

# PROJECT STRUCTURE

backend/
frontend/
data/

---

# START BACKEND

Open:

backend/start_backend.bat

Backend runs on:

http://127.0.0.1:8000

---

# START FRONTEND

Open:

frontend/start_frontend.bat

Frontend runs on:

http://localhost:5173

---

# DATASET

Upload:

data.zip

through Upload page.

The system automatically:

- Replaces old dataset
- Extracts ZIP
- Processes longitudinal data
- Computes DPVI
- Trains models
- Generates analytics dashboard

---

# ANALYTICS INCLUDED

- DPVI Score
- Risk Classification
- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- RMSE
- MSE
- R²
- Confusion Matrix
- Feature Importance
- Ablation Analysis
- Longitudinal Progression Insights

---

# TECHNOLOGIES

Backend:
- FastAPI
- Python
- Scikit-learn

Frontend:
- React
- Vite
- Recharts
- Framer Motion

---

# FINAL NOTE

This system trains BOTH:

1. Full DPVI Dataset
   (5054 x 188)

2. Weighted DPVI Dataset
   (5054 x 64)

and generates explainable progression analytics.