from pydantic import BaseModel
from typing import List, Dict, Any, Optional


# =========================================================
# BASIC RESPONSE
# =========================================================

class BasicResponse(BaseModel):

    success: bool

    message: str


# =========================================================
# SUMMARY RESPONSE
# =========================================================

class SummaryResponse(BaseModel):

    patients: int

    full_dpvi_columns: int

    weighted_dpvi_columns: int

    best_model: str

    risk_level: str

    dpvi_score: float

    updrs_prediction: float


# =========================================================
# METRICS RESPONSE
# =========================================================

class MetricsResponse(BaseModel):

    accuracy: float

    precision: float

    recall: float

    f1_score: float

    roc_auc: float

    rmse: float

    mse: float

    r2_score: float


# =========================================================
# FEATURE IMPORTANCE ITEM
# =========================================================

class FeatureImportanceItem(BaseModel):

    feature: str

    importance: float


# =========================================================
# FEATURE IMPORTANCE RESPONSE
# =========================================================

class FeatureImportanceResponse(BaseModel):

    feature_importance: List[FeatureImportanceItem]


# =========================================================
# ABLATION RESPONSE
# =========================================================

class AblationResponse(BaseModel):

    baseline_accuracy: float

    dpvi_accuracy: float

    improvement: float


# =========================================================
# INSIGHT RESPONSE
# =========================================================

class InsightResponse(BaseModel):

    insights: List[str]


# =========================================================
# CONFUSION MATRIX RESPONSE
# =========================================================

class ConfusionMatrixResponse(BaseModel):

    tp: int

    tn: int

    fp: int

    fn: int


# =========================================================
# COMPLETE RESULTS RESPONSE
# =========================================================

class FullResultsResponse(BaseModel):

    success: bool

    results: Dict[str, Any]


# =========================================================
# PROGRESS ITEM
# =========================================================

class ProgressItem(BaseModel):

    time: str

    message: str


# =========================================================
# PROGRESS RESPONSE
# =========================================================

class ProgressResponse(BaseModel):

    success: bool

    progress: List[ProgressItem]


# =========================================================
# PIPELINE STATUS
# =========================================================

class PipelineStatusResponse(BaseModel):

    running: bool