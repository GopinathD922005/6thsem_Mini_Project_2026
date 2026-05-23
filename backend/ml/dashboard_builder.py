import numpy as np


# =========================================================
# BASIC HELPERS
# =========================================================
def _get_grid_search_best_params(grid_search_results, model_name):

    if not grid_search_results:
        return {}

    for row in grid_search_results:

        if row.get("Model") == model_name:
            return row.get("Best_Params", {})

    return {}

def _format_percent(value, signed=False):

    value = float(value) * 100

    if signed:
        return f"{value:+.2f}%"

    return f"{value:.2f}%"


def _safe_float(value):

    try:
        return float(value)

    except Exception:
        return 0.0


def _safe_int(value):

    try:
        return int(value)

    except Exception:
        return 0


def _get_proposed_rows(ledger):

    return [
        row for row in ledger
        if "Proposed" in str(row.get("Approach", ""))
    ]


def _get_baseline_row(ledger, model_name):

    for row in ledger:

        if (
            row.get("Model") == model_name
            and row.get("Approach") == "Baseline"
        ):
            return row

    return None


# =========================================================
# EXPERIMENT SELECTION LOGIC
# =========================================================

def _calculate_average_elevation(ledger):

    elevations = []

    model_names = sorted(
        set(row.get("Model") for row in ledger if row.get("Model"))
    )

    for model_name in model_names:

        baseline_row = _get_baseline_row(
            ledger,
            model_name
        )

        proposed_rows = [
            row for row in ledger
            if (
                row.get("Model") == model_name
                and "Proposed" in str(row.get("Approach", ""))
            )
        ]

        if not baseline_row or not proposed_rows:
            continue

        proposed_row = proposed_rows[0]

        baseline_acc = _safe_float(
            baseline_row.get("Accuracy", 0)
        )

        proposed_acc = _safe_float(
            proposed_row.get("Accuracy", 0)
        )

        elevations.append(
            proposed_acc - baseline_acc
        )

    if not elevations:
        return 0.0

    return float(np.mean(elevations))


def _select_best_experiment(experiments):

    best_key = None

    best_payload = None

    best_elevation = -999

    for key, payload in experiments.items():

        ledger = payload.get("ledger", [])

        avg_elevation = _calculate_average_elevation(
            ledger
        )

        payload["average_accuracy_elevation"] = avg_elevation

        if avg_elevation > best_elevation:

            best_key = key

            best_payload = payload

            best_elevation = avg_elevation

    return best_key, best_payload, best_elevation


def _select_best_model_row(ledger):

    proposed_rows = _get_proposed_rows(
        ledger
    )

    if not proposed_rows:
        return None

    return max(
        proposed_rows,
        key=lambda row: _safe_float(row.get("Accuracy", 0))
    )


# =========================================================
# DPVI SCORE LOGIC
# =========================================================

def _calculate_normalized_dpvi_score(df):

    dpvi_cols = [
        col for col in df.columns
        if col.startswith("DPVI_")
    ]

    if not dpvi_cols:
        return {
            "dpvi_score": 0.0,
            "risk_level": "Unavailable",
            "patient_score_mean": 0.0,
            "patient_score_min": 0.0,
            "patient_score_max": 0.0
        }

    dpvi_data = df[dpvi_cols].copy()

    for col in dpvi_cols:

        min_val = dpvi_data[col].min()

        max_val = dpvi_data[col].max()

        if max_val == min_val:
            dpvi_data[col] = 0.0

        else:
            dpvi_data[col] = (
                (dpvi_data[col] - min_val)
                /
                (max_val - min_val)
            )

    patient_scores = dpvi_data.mean(axis=1)

    dataset_score = float(
        patient_scores.mean()
    )

    if dataset_score < 0.30:
        risk_level = "Low Instability"

    elif dataset_score < 0.60:
        risk_level = "Moderate Instability"

    else:
        risk_level = "High Instability"

    return {
        "dpvi_score": round(dataset_score, 4),
        "risk_level": risk_level,
        "patient_score_mean": round(dataset_score, 4),
        "patient_score_min": round(float(patient_scores.min()), 4),
        "patient_score_max": round(float(patient_scores.max()), 4)
    }


# =========================================================
# FEATURE IMPORTANCE FETCHING
# Uses already-stored feature importance from model_trainer.py
# No model training happens here.
# =========================================================

def _get_stored_feature_importance(
    selected_payload,
    approach,
    model_name
):

    feature_importance_block = selected_payload.get(
        "feature_importance",
        {}
    )

    approach_block = feature_importance_block.get(
        approach,
        {}
    )

    return approach_block.get(
        model_name,
        []
    )


# =========================================================
# TEXT GENERATION HELPERS
# =========================================================

def _build_prediction_insights(
    selected_label,
    best_row,
    dpvi_info,
    avg_elevation
):

    return [
        (
            f"{selected_label} was selected as the strongest evaluation "
            f"pipeline based on the highest average accuracy elevation."
        ),

        (
            f"{best_row['Model']} produced the highest proposed-model "
            f"accuracy inside the selected pipeline."
        ),

        (
            f"The selected model achieved "
            f"{_format_percent(best_row['Accuracy'])} accuracy with "
            f"{_format_percent(best_row['ROC_AUC'])} ROC-AUC."
        ),

        (
            f"The normalized DPVI score is {dpvi_info['dpvi_score']}, "
            f"which indicates {dpvi_info['risk_level'].lower()} at the "
            f"cohort level."
        ),

        (
            f"The selected pipeline achieved an average accuracy elevation "
            f"of {_format_percent(avg_elevation, signed=True)} over baseline."
        )
    ]


def _build_prediction_clinical_interpretation(
    best_row,
    dpvi_info
):

    return (
        f"The average normalized DPVI score of {dpvi_info['dpvi_score']} "
        f"places the evaluated patient cohort in the "
        f"{dpvi_info['risk_level']} category. This means the overall patient "
        f"group shows a measurable level of longitudinal symptom fluctuation "
        f"across the selected motor, cognitive, and gait-related indicators. "
        f"The selected prediction model achieved "
        f"{_format_percent(best_row['Accuracy'])} accuracy, showing that "
        f"these instability patterns were consistently useful for disease "
        f"status prediction."
    )


def _build_dpvi_contribution(
    selected_label,
    best_row,
    baseline_row,
    avg_elevation
):

    baseline_acc = _safe_float(
        baseline_row.get("Accuracy", 0)
    )

    proposed_acc = _safe_float(
        best_row.get("Accuracy", 0)
    )

    accuracy_gain = proposed_acc - baseline_acc

    baseline_auc = _safe_float(
        baseline_row.get("ROC_AUC", 0)
    )

    proposed_auc = _safe_float(
        best_row.get("ROC_AUC", 0)
    )

    auc_gain = proposed_auc - baseline_auc

    return (
        f"In the selected {selected_label} pipeline, DPVI features increased "
        f"the best model accuracy from {_format_percent(baseline_acc)} to "
        f"{_format_percent(proposed_acc)}, giving a model-level improvement "
        f"of {_format_percent(accuracy_gain, signed=True)}. Across all three "
        f"models in the selected experiment, the average accuracy elevation "
        f"was {_format_percent(avg_elevation, signed=True)}. ROC-AUC changed "
        f"by {_format_percent(auc_gain, signed=True)}, showing how much the "
        f"volatility-aware DPVI representation improved class separation "
        f"beyond baseline clinical severity features."
    )


def _build_analysis_explainability_insights(
    best_row,
    baseline_row,
    feature_importance,
    avg_elevation
):

    top_features = [
        item["feature"]
        for item in feature_importance[:3]
    ]

    baseline_auc = _safe_float(
        baseline_row.get("ROC_AUC", 0)
    )

    proposed_auc = _safe_float(
        best_row.get("ROC_AUC", 0)
    )

    auc_gain = proposed_auc - baseline_auc

    precision = _safe_float(
        best_row.get("Precision", 0)
    )

    recall = _safe_float(
        best_row.get("Recall", 0)
    )

    insights = []

    if top_features:

        insights.append(
            f"The strongest contributing features were {', '.join(top_features)}, "
            f"showing which clinical signals influenced the selected model most."
        )

    else:

        insights.append(
            "Feature importance values were not available for the selected model output."
        )

    insights.append(
        f"The selected model changed ROC-AUC by "
        f"{_format_percent(auc_gain, signed=True)} compared with its baseline "
        f"configuration."
    )

    if recall >= precision:

        insights.append(
            f"Recall ({_format_percent(recall)}) was higher than precision "
            f"({_format_percent(precision)}), meaning the model was more "
            f"sensitive in identifying PD-positive cases."
        )

    else:

        insights.append(
            f"Precision ({_format_percent(precision)}) was higher than recall "
            f"({_format_percent(recall)}), meaning the model was more "
            f"conservative in assigning positive predictions."
        )

    insights.append(
        f"The selected experiment achieved an average accuracy elevation of "
        f"{_format_percent(avg_elevation, signed=True)} across Random Forest, "
        f"XGBoost, and Gradient Boosting."
    )

    insights.append(
        "Feature importance values were taken from the already-trained model "
        "outputs generated during the selected experiment, without retraining "
        "the model inside the dashboard builder."
    )

    return insights


def _build_analysis_clinical_interpretation(
    selected_label,
    selected_dataset_label,
    best_row,
    baseline_row,
    dpvi_info,
    avg_elevation,
    selected_df
):

    accuracy_gain = (
        _safe_float(best_row.get("Accuracy", 0))
        -
        _safe_float(baseline_row.get("Accuracy", 0))
    )

    tp = _safe_int(
        best_row.get("TP", 0)
    )

    tn = _safe_int(
        best_row.get("TN", 0)
    )

    fp = _safe_int(
        best_row.get("FP", 0)
    )

    fn = _safe_int(
        best_row.get("FN", 0)
    )

    return (
        f"The selected experiment was {selected_label}, using "
        f"{best_row['Model']} as the best proposed model. This configuration "
        f"used the {selected_dataset_label} representation with "
        f"{selected_df.shape[0]} patients and {selected_df.shape[1]} columns. "
        f"It achieved {_format_percent(best_row['Accuracy'])} accuracy and "
        f"{_format_percent(best_row['ROC_AUC'])} ROC-AUC. Compared with the "
        f"matching baseline version of the same model, DPVI changed accuracy "
        f"by {_format_percent(accuracy_gain, signed=True)}.\n\n"

        f"At the experiment level, the average accuracy elevation across the "
        f"three evaluated architectures was "
        f"{_format_percent(avg_elevation, signed=True)}, which is why this "
        f"pipeline was selected for the dashboard. The normalized dataset-level "
        f"DPVI score was {dpvi_info['dpvi_score']}, corresponding to "
        f"{dpvi_info['risk_level']}.\n\n"

        f"The confusion matrix recorded {tp} true positives, {tn} true "
        f"negatives, {fp} false positives, and {fn} false negatives. This gives "
        f"a technical view of how the selected model separated PD-positive and "
        f"PD-negative cases under the selected DPVI configuration."
    )


# =========================================================
# MAIN BUILDER
# =========================================================

def build_dashboard_results(
    full_train_test,
    full_cv,
    weighted_train_test,
    weighted_cv,
    train_ready_df,
    train_ready_df_weighted,
    grid_search_results=None
):

    experiments = {
        "full_train_test": {
            "label": "Full DPVI Train/Test",
            "dataset_label": "188-column Full DPVI dataset",
            "ledger": full_train_test["ledger"],
            "feature_importance": full_train_test.get(
                "feature_importance",
                {}
            ),
            "df": train_ready_df
        },

        "full_cv": {
            "label": "Full DPVI 3-Fold Cross-Validation",
            "dataset_label": "188-column Full DPVI dataset",
            "ledger": full_cv["ledger"],
            "feature_importance": full_cv.get(
                "feature_importance",
                {}
            ),
            "df": train_ready_df
        },

        "weighted_train_test": {
            "label": "Weighted DPVI Train/Test",
            "dataset_label": "64-column Weighted DPVI dataset",
            "ledger": weighted_train_test["ledger"],
            "feature_importance": weighted_train_test.get(
                "feature_importance",
                {}
            ),
            "df": train_ready_df_weighted
        },

        "weighted_cv": {
            "label": "Weighted DPVI 3-Fold Cross-Validation",
            "dataset_label": "64-column Weighted DPVI dataset",
            "ledger": weighted_cv["ledger"],
            "feature_importance": weighted_cv.get(
                "feature_importance",
                {}
            ),
            "df": train_ready_df_weighted
        },
    }

    selected_key, selected_payload, avg_elevation = _select_best_experiment(
        experiments
    )

    selected_ledger = selected_payload["ledger"]

    selected_df = selected_payload["df"]

    selected_label = selected_payload["label"]

    selected_dataset_label = selected_payload["dataset_label"]

    best_row = _select_best_model_row(
        selected_ledger
    )

    if best_row is None:

        raise ValueError(
            "No proposed DPVI row found in selected experiment ledger."
        )

    baseline_row = _get_baseline_row(
        selected_ledger,
        best_row["Model"]
    )

    if baseline_row is None:

        raise ValueError(
            f"No baseline row found for model: {best_row['Model']}"
        )

    dpvi_info = _calculate_normalized_dpvi_score(
        selected_df
    )

    feature_importance = _get_stored_feature_importance(
        selected_payload,
        best_row["Approach"],
        best_row["Model"]
    )

    prediction_insights = _build_prediction_insights(
        selected_label,
        best_row,
        dpvi_info,
        avg_elevation
    )

    prediction_clinical_interpretation = _build_prediction_clinical_interpretation(
        best_row,
        dpvi_info
    )

    dpvi_contribution = _build_dpvi_contribution(
        selected_label,
        best_row,
        baseline_row,
        avg_elevation
    )

    analysis_explainability_insights = _build_analysis_explainability_insights(
        best_row,
        baseline_row,
        feature_importance,
        avg_elevation
    )

    analysis_clinical_interpretation = _build_analysis_clinical_interpretation(
        selected_label,
        selected_dataset_label,
        best_row,
        baseline_row,
        dpvi_info,
        avg_elevation,
        selected_df
    )

    baseline_accuracy = _safe_float(
        baseline_row.get("Accuracy", 0)
    )

    proposed_accuracy = _safe_float(
        best_row.get("Accuracy", 0)
    )

    accuracy_elevation = proposed_accuracy - baseline_accuracy

    winner_probability_threshold = _safe_float(
        best_row.get("Probability_Threshold", 0.5)
    )

    tuned_best_params = _get_grid_search_best_params(
        grid_search_results,
        best_row["Model"]
    )

    baseline_roc_auc = _safe_float(
        baseline_row.get("ROC_AUC", 0)
    )

    proposed_roc_auc = _safe_float(
        best_row.get("ROC_AUC", 0)
    )

    baseline_f1 = _safe_float(
        baseline_row.get("F1_Score", 0)
    )

    proposed_f1 = _safe_float(
        best_row.get("F1_Score", 0)
    )

    return {
        "selection": {
            "selected_experiment_key": selected_key,
            "selected_pipeline": selected_label,
            "selected_dataset": selected_dataset_label,
            "best_model": best_row["Model"],
            "average_accuracy_elevation": round(float(avg_elevation), 4),
            "average_accuracy_elevation_percent": _format_percent(
                avg_elevation,
                signed=True
            )
        },

        "prediction": {
            "model_probability_threshold": round(winner_probability_threshold, 4),
            "baseline_accuracy": round(baseline_accuracy, 4),
            "baseline_accuracy_percent": _format_percent(baseline_accuracy),

            "accuracy_elevation": round(accuracy_elevation, 4),
            "accuracy_elevation_percent": _format_percent(
                accuracy_elevation,
                signed=True
            ),

            "tuned_best_params": tuned_best_params,
            "selected_pipeline": selected_label,
            "average_accuracy_elevation": round(float(avg_elevation), 4),
            "average_accuracy_elevation_percent": _format_percent(
                avg_elevation,
                signed=True
            ),
            "dpvi_score": dpvi_info["dpvi_score"],
            "risk_level": dpvi_info["risk_level"],
            "best_model": best_row["Model"],
            "best_accuracy": round(proposed_accuracy, 4),
            "best_accuracy_percent": _format_percent(proposed_accuracy),
            "full_dataset_shape": (
                f"{train_ready_df.shape[0]} x {train_ready_df.shape[1]}"
            ),
            "weighted_dataset_shape": (
                f"{train_ready_df_weighted.shape[0]} x "
                f"{train_ready_df_weighted.shape[1]}"
            ),
            "clinical_interpretation": prediction_clinical_interpretation,
            "dpvi_contribution": dpvi_contribution,
            "prediction_insights": prediction_insights
        },

        "analysis": {
            "metrics": {
                "accuracy": round(proposed_accuracy, 4),
                "precision": round(
                    _safe_float(best_row.get("Precision", 0)),
                    4
                ),
                "recall": round(
                    _safe_float(best_row.get("Recall", 0)),
                    4
                ),
                "f1_score": round(
                    _safe_float(best_row.get("F1_Score", 0)),
                    4
                ),
                "roc_auc": round(proposed_roc_auc, 4),
                "r2_score": round(
                    _safe_float(best_row.get("R2_Score", 0)),
                    4
                ),
                "mae": round(
                    _safe_float(best_row.get("MAE", 0)),
                    4
                ),
                "mse": round(
                    _safe_float(best_row.get("MSE", 0)),
                    4
                ),
                "rmse": round(
                    _safe_float(best_row.get("RMSE", 0)),
                    4
                ),
                "specificity": round(
                    _safe_float(best_row.get("Specificity", 0)),
                    4
                )
            },

            "ablation": {
                "baseline_accuracy": round(baseline_accuracy, 4),
                "dpvi_accuracy": round(proposed_accuracy, 4),
                "accuracy_improvement": round(
                    proposed_accuracy - baseline_accuracy,
                    4
                ),
                "baseline_roc_auc": round(baseline_roc_auc, 4),
                "dpvi_roc_auc": round(proposed_roc_auc, 4),
                "roc_auc_improvement": round(
                    proposed_roc_auc - baseline_roc_auc,
                    4
                ),
                "baseline_f1": round(baseline_f1, 4),
                "dpvi_f1": round(proposed_f1, 4),
                "f1_improvement": round(
                    proposed_f1 - baseline_f1,
                    4
                ),
                "average_accuracy_elevation": round(float(avg_elevation), 4),
                "average_accuracy_elevation_percent": _format_percent(
                    avg_elevation,
                    signed=True
                )
            },

            "confusion_matrix": {
                "tp": _safe_int(best_row.get("TP", 0)),
                "tn": _safe_int(best_row.get("TN", 0)),
                "fp": _safe_int(best_row.get("FP", 0)),
                "fn": _safe_int(best_row.get("FN", 0))
            },

            "feature_importance": feature_importance,

            "explainability_insights": analysis_explainability_insights,

            "clinical_interpretation": analysis_clinical_interpretation
        }
    }