# Disease Progression Volatility Index (DPVI) for Parkinson’s Disease

An instability-driven machine learning framework developed for analyzing and predicting Parkinson’s disease progression using longitudinal clinical records.

The project introduces the **Disease Progression Volatility Index (DPVI)** to quantify disease instability and progression dynamics through feature engineering, temporal analysis, explainability, and interactive visualization.

---

## Project Overview

Conventional progression prediction methods focus mainly on classification accuracy and often overlook temporal instability across patient visits.

This project proposes **DPVI (Disease Progression Volatility Index)** to capture:

- Progression Variability
- Progression Rate
- Spikes
- Trend Behavior
- Entropy-based Instability

The generated DPVI features are integrated with machine learning models to improve progression interpretation and prediction.

---

## Key Features

- Longitudinal Patient Data Processing
- Patient-wise Temporal Alignment
- Time-Series Construction
- DPVI Computation
- Feature Fusion
- Dimensionality Reduction (PCA)
- Machine Learning Prediction
- SHAP Explainability
- Risk Classification
- Interactive Visualization Dashboard
- Backend and Frontend Testing

---

## System Workflow

Dataset Upload  
→ Data Integration  
→ Preprocessing  
→ Longitudinal Alignment  
→ Feature Engineering  
→ DPVI Computation  
→ Feature Fusion  
→ PCA  
→ Model Training  
→ Evaluation  
→ Explainability (SHAP)  
→ Prediction & Risk Classification  
→ Dashboard Visualization

---

## Technologies Used

| Component | Technology |
|----------|-----------|
| Programming Language | Python |
| Backend | FastAPI |
| Frontend | React |
| ML Models | Random Forest, XGBoost, Gradient Boosting |
| Data Processing | Pandas, NumPy |
| Explainability | SHAP |
| Visualization | Plotly |
| Feature Reduction | PCA |
| Backend Testing | Pytest |
| Manual API Testing | Swagger UI |
| Frontend Testing | Vitest + React Testing Library |

---

## Project Structure

```bash
project/
│
├── backend/
│   ├── api/
│   ├── models/
│   ├── pipeline/
│   ├── services/
│   └── tests/
│
├── frontend/
│   ├── src/
│   ├── pages/
│   ├── components/
│   └── tests/
│
├── dataset/
├── outputs/
├── docs/
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone <your-repository-url>
cd project
```

### Backend Setup

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn app:app --reload
```

Backend:
```
http://localhost:8000
```

Swagger:
```
http://localhost:8000/docs
```

---

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend:
```
http://localhost:5173
```

---

## Testing

### Backend Automated Testing

```bash
pytest
```

### Backend Manual API Testing

```bash
Swagger UI
```

### Frontend Testing

```bash
npm test
```

or

```bash
npm run test
```

---

## Outputs

The system generates:

- DPVI Scores
- UPDRS Prediction Results
- Stable / Moderate / High Risk Classification
- Patient-wise Progression Analysis
- Multi-feature Visualization
- Performance Metrics
- Explainability Reports
- Dashboard Analytics

---

## Performance Metrics

Classification:
- Accuracy
- Precision
- Recall
- F1 Score
- ROC–AUC
- Specificity

Regression:
- MAE
- RMSE
- R² Score

---
# FINAL NOTE

This system trains BOTH:

1. Full DPVI Dataset
   (5054 x 188)

2. Weighted DPVI Dataset
   (5054 x 64)

and generates explainable progression analytics.
## Future Work

Future work aims to extend DPVI into a low-cost wearable monitoring framework for continuous Parkinson’s disease assessment using sensor-based signal analysis and real-time monitoring.

---

## Authors

- Manoj H R  
- Gopinath D
- K Prerana  
- Department of Computer Science and Engineering, MSRIT

---

## License

Academic / Educational Use
