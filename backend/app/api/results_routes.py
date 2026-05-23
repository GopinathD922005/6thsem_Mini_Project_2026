from fastapi import APIRouter

from ml.pipeline_runner import get_latest_results

from app.services.progress_store import get_progress

from ml.pipeline_runner import (
    get_prediction_results,
    get_analysis_results,
    get_graph_results,
    get_ledger_results,
    get_patient_visualization_results,
    get_patient_detail_by_patno
)

router = APIRouter(
    prefix="/results",
    tags=["Results"]
)

def _get_public_results(results):
    return {
        key: value
        for key, value in results.items()
        if key not in [
            "_master_event_log",
            "_train_ready_df",
            "patient_visualization"
        ]
    }

# =========================================================
# GET ALL RESULTS
# =========================================================

@router.get("/")
def fetch_results():

    results = get_latest_results()

    return {
        "success": True,
        "results": _get_public_results(results)
    }


# =========================================================
# GET PROCESSING LOGS
# =========================================================

@router.get("/progress")
def fetch_progress():

    progress = get_progress()

    return {

        "success": True,

        "progress": progress
    }


# =========================================================
# QUICK SUMMARY
# =========================================================

@router.get("/summary")
def fetch_summary():

    results = get_latest_results()

    if not results:

        return {

            "success": False,

            "message": "No results available"
        }

    return {

        "success": True,

        "summary": results.get("summary", {})
    }


# =========================================================
# METRICS
# =========================================================

@router.get("/metrics")
def fetch_metrics():

    results = get_latest_results()

    if not results:

        return {

            "success": False,

            "message": "No metrics available"
        }

    return {

        "success": True,

        "metrics": results.get("metrics", {})
    }


# =========================================================
# FEATURE IMPORTANCE
# =========================================================

@router.get("/feature-importance")
def fetch_feature_importance():

    results = get_latest_results()

    if not results:

        return {

            "success": False,

            "message": "No feature importance data"
        }

    return {

        "success": True,

        "feature_importance": results.get(
            "feature_importance",
            []
        )
    }


# =========================================================
# ABLATION RESULTS
# =========================================================

@router.get("/ablation")
def fetch_ablation_results():

    results = get_latest_results()

    if not results:

        return {

            "success": False,

            "message": "No ablation results available"
        }

    return {

        "success": True,

        "ablation": results.get(
            "ablation",
            {}
        )
    }


# =========================================================
# INSIGHTS
# =========================================================

@router.get("/insights")
def fetch_insights():

    results = get_latest_results()

    if not results:

        return {

            "success": False,

            "message": "No insights available"
        }

    return {

        "success": True,

        "insights": results.get(
            "insights",
            []
        )
    }


# =========================================================
# CONFUSION MATRIX
# =========================================================

@router.get("/confusion-matrix")
def fetch_confusion_matrix():

    results = get_latest_results()

    if not results:

        return {

            "success": False,

            "message": "No confusion matrix available"
        }

    return {

        "success": True,

        "confusion_matrix": results.get(
            "confusion_matrix",
            {}
        )
    }


@router.get("/latest")
def get_results():

    results = get_latest_results()

    return {
        "success": True,
        "results": _get_public_results(results)
    }

@router.get("/grid-search-cv")
def fetch_grid_search_cv():

    results = get_latest_results()

    return {
        "success": True,
        "grid_search_cv": results.get("grid_search_cv", [])
    }

@router.get("/prediction")
def prediction_results():
    data = get_prediction_results()

    return {
        "success": True,
        "results": data,
        **data
    }


@router.get("/analysis")
def analysis_results():
    data = get_analysis_results()

    return {
        "success": True,
        **data
    }


@router.get("/graphs")
def graph_results():
    data = get_graph_results()

    return {
        "success": True,
        **data
    }


@router.get("/ledgers")
def ledger_results():
    data = get_ledger_results()

    return {
        "success": True,
        **data
    }


@router.get("/patients")
def patient_visualization_results():
    data = get_patient_visualization_results()

    patient_visualization = data.get("patient_visualization", {})

    if isinstance(patient_visualization, list):
        patient_visualization = {
            "patient_cards": patient_visualization,
            "global_primary_volatility_feature": None
        }

    return {
        "success": True,
        "patients": patient_visualization.get("patient_cards", []),
        "global_primary_volatility_feature": patient_visualization.get(
            "global_primary_volatility_feature"
        )
    }


@router.get("/patient-detail/{patno}")
def patient_detail_result(patno: str):
    patient = get_patient_detail_by_patno(patno)

    if patient is None:
        return {
            "success": False,
            "message": "Patient detail not found"
        }

    return {
        "success": True,
        "patient": patient
    }