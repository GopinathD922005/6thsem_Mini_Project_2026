from ml.pipeline_runner import get_latest_results


# =========================================================
# SUMMARY
# =========================================================

def get_summary_data():

    results = get_latest_results()

    return results.get("summary", {})


# =========================================================
# METRICS
# =========================================================

def get_metrics_data():

    results = get_latest_results()

    return results.get("metrics", {})


# =========================================================
# FEATURE IMPORTANCE
# =========================================================

def get_feature_importance_data():

    results = get_latest_results()

    return results.get("feature_importance", [])


# =========================================================
# ABLATION RESULTS
# =========================================================

def get_ablation_data():

    results = get_latest_results()

    return results.get("ablation", {})


# =========================================================
# INSIGHTS
# =========================================================

def get_insight_data():

    results = get_latest_results()

    return results.get("insights", [])


# =========================================================
# CONFUSION MATRIX
# =========================================================

def get_confusion_matrix_data():

    results = get_latest_results()

    return results.get("confusion_matrix", {})


# =========================================================
# COMPLETE RESULTS
# =========================================================

def get_complete_results():

    results = get_latest_results()

    return results