import numpy as np
import pandas as pd

from concurrent.futures import ProcessPoolExecutor, as_completed
import os

TARGET_FEATURES = [
    "NP3TOT", "NP3BRADY", "NP3GAIT", "NP3PSTBL", "NP3FRZGT", "NP3RIGN",
    "NP2WALK", "NP2PTOT", "MCATOT", "CVStrideTime", "CVStepTime",
    "CVSteplength", "SampEntropyV", "SampEntropyML", "SampEntropyAP",
    "stepAsymV", "stepAsymML", "stepAsymAP", "rmsV", "rmsML", "rmsAP",
    "StepVelocitycmsec", "StepCount", "STR_CV_U", "STEP_REG_U",
    "STEP_SYM_U", "JERK_T_U", "NP1COG", "NP1DPRS", "NP1ANXS", "NP1APAT"
]


REQUIRED_EVENT_COLUMNS = [
    "PATNO",
    "EVENT_ID",
    "MEASURE_NAME",
    "MEASURE_VALUE"
]


def _empty_event_log():
    return pd.DataFrame(columns=REQUIRED_EVENT_COLUMNS)


def _normalize_event_log(df):
    if df is None or df.empty:
        return _empty_event_log()

    df = df.copy()

    for col in REQUIRED_EVENT_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan

    df = df[REQUIRED_EVENT_COLUMNS]

    df["PATNO"] = df["PATNO"].astype(str).str.strip()
    df["EVENT_ID"] = df["EVENT_ID"].astype(str).str.strip()
    df["MEASURE_NAME"] = df["MEASURE_NAME"].astype(str).str.strip()

    df["MEASURE_VALUE"] = pd.to_numeric(
        df["MEASURE_VALUE"],
        errors="coerce"
    )

    df = df.dropna(subset=["MEASURE_VALUE"])

    return df


def _status_text(value):
    if pd.isna(value):
        return "Unknown"

    try:
        return "Present" if int(value) == 1 else "Absent"
    except Exception:
        return "Unknown"


def _prediction_result(actual, predicted):
    if actual == "Unknown" or predicted == "Unknown":
        return "Unknown"

    return "Correct" if actual == predicted else "Misclassified"


def _instability_label(dpvi):
    if pd.isna(dpvi):
        return "Unavailable"

    if dpvi < 0.34:
        return "STABLE"

    if dpvi < 0.67:
        return "MODERATE"

    return "HIGH VOLATILITY"


def _trend_summary(dpvi):
    if pd.isna(dpvi):
        return "Insufficient longitudinal data for instability analysis."

    if dpvi < 0.34:
        return "Stable progression with minimal fluctuations."

    if dpvi < 0.67:
        return "Moderate fluctuations detected across visits."

    return "Frequent fluctuations with unstable progression."


def _safe_round(value, digits=4):
    if pd.isna(value):
        return None

    try:
        return round(float(value), digits)
    except Exception:
        return None


def _get_dpvi_columns(df):
    return [
        col for col in df.columns
        if col.startswith("DPVI_")
        and not col.startswith("DPVI_WEIGHTED")
    ]


def _find_global_primary_volatility_feature(train_ready_df):
    dpvi_cols = _get_dpvi_columns(train_ready_df)

    if not dpvi_cols:
        return "NP3TOT"

    winners = []

    for _, row in train_ready_df.iterrows():
        values = pd.to_numeric(
            row[dpvi_cols],
            errors="coerce"
        )

        if values.isna().all():
            continue

        min_val = values.min()
        max_val = values.max()

        if pd.isna(min_val) or pd.isna(max_val):
            continue

        if max_val == min_val:
            scaled = values.fillna(0)
        else:
            scaled = (values - min_val) / (max_val - min_val)

        winning_col = scaled.idxmax()

        matched_feature = None

        for feature in TARGET_FEATURES:
            if feature in winning_col:
                matched_feature = feature
                break

        if matched_feature:
            winners.append(matched_feature)

    if not winners:
        return "NP3TOT"

    return pd.Series(winners).value_counts().idxmax()


def _build_feature_series(patient_log, feature_name):
    patient_log = _normalize_event_log(patient_log)

    if patient_log.empty:
        return []

    feature_log = patient_log[
        patient_log["MEASURE_NAME"] == feature_name
    ].copy()

    if feature_log.empty:
        return []

    feature_log = feature_log.sort_values("EVENT_ID")

    return [
        {
            "visit": str(row["EVENT_ID"]),
            "value": _safe_round(row["MEASURE_VALUE"]),
        }
        for _, row in feature_log.iterrows()
        if not pd.isna(row["MEASURE_VALUE"])
    ]


def _build_multi_feature_graph(patient_log):
    patient_log = _normalize_event_log(patient_log)

    if patient_log.empty:
        return {
            "union_visits": [],
            "feature_series": {
                feature: []
                for feature in TARGET_FEATURES
            }
        }

    union_visits = sorted(
        patient_log["EVENT_ID"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    feature_series = {}

    for feature in TARGET_FEATURES:
        f_log = patient_log[
            patient_log["MEASURE_NAME"] == feature
        ][["EVENT_ID", "MEASURE_VALUE"]].copy()

        value_map = {
            str(row["EVENT_ID"]): _safe_round(row["MEASURE_VALUE"])
            for _, row in f_log.iterrows()
            if not pd.isna(row["MEASURE_VALUE"])
        }

        feature_series[feature] = [
            {
                "visit": visit,
                "value": value_map.get(visit, None)
            }
            for visit in union_visits
        ]

    return {
        "union_visits": union_visits,
        "feature_series": feature_series
    }


def _build_visit_table(patient_log):
    patient_log = _normalize_event_log(patient_log)

    if patient_log.empty:
        return []

    pivot = patient_log.pivot_table(
        index="EVENT_ID",
        columns="MEASURE_NAME",
        values="MEASURE_VALUE",
        aggfunc="mean"
    ).reset_index()

    available_cols = [
        col for col in ["EVENT_ID"] + TARGET_FEATURES
        if col in pivot.columns
    ]

    pivot = pivot[available_cols]

    return pivot.replace({np.nan: None}).to_dict(orient="records")


def build_patient_visualization_data(
    master_event_log,
    train_ready_df,
    train_ready_df_weighted=None,
    dashboard_results=None
):
    master_event_log = _normalize_event_log(master_event_log)

    train_ready_df = train_ready_df.copy()
    train_ready_df["PATNO"] = train_ready_df["PATNO"].astype(str).str.strip()

    primary_feature = _find_global_primary_volatility_feature(
        train_ready_df
    )

    allowed_patnos = train_ready_df["PATNO"].unique().tolist()

    dpvi_cols = _get_dpvi_columns(train_ready_df)

    primary_feature_log = master_event_log[
        master_event_log["MEASURE_NAME"] == primary_feature
    ].copy()

    patient_log_groups = {
        str(patno): group.copy()
        for patno, group in primary_feature_log.groupby("PATNO")
    }

    patient_cards = []

    for patno in allowed_patnos:
        patient_row = train_ready_df[
            train_ready_df["PATNO"] == patno
        ].iloc[0]

        patient_log = patient_log_groups.get(
            str(patno),
            _empty_event_log()
        )

        actual_status = _status_text(
            patient_row.get("FINAL_STATUS", np.nan)
        )
        dpvi_predicted_status = _status_text(
            patient_row.get("DPVI_PREDICTED_STATUS", np.nan)
        )

        baseline_predicted_status = _status_text(
            patient_row.get("BASELINE_PREDICTED_STATUS", np.nan)
        )


        prediction_confidence = patient_row.get(
            "PREDICTION_CONFIDENCE",
            np.nan
        )

        if dpvi_cols:
            dpvi_values = pd.to_numeric(
                patient_row[dpvi_cols],
                errors="coerce"
            )
            dpvi_score = dpvi_values.mean()
        else:
            dpvi_score = np.nan

        instability = _instability_label(dpvi_score)

        primary_graph = _build_feature_series(
            patient_log,
            primary_feature
        )

        visit_count = (
            int(patient_log["EVENT_ID"].nunique())
            if not patient_log.empty and "EVENT_ID" in patient_log.columns
            else 0
        )

        card = {
            "dpvi_predicted_status": dpvi_predicted_status,
            "baseline_predicted_status": baseline_predicted_status,
            "patno": str(patno),
            "actual_status": actual_status,
            "dpvi_prediction_result": _prediction_result(
                actual_status,
                dpvi_predicted_status
            ),

            "baseline_prediction_result": _prediction_result(
                actual_status,
                baseline_predicted_status
            ),
            "prediction_confidence": _safe_round(
                prediction_confidence,
                4
            ),
            "dpvi_score": _safe_round(dpvi_score, 4),
            "instability": instability,
            "primary_volatility_feature": primary_feature,
            "trend_summary": _trend_summary(dpvi_score),
            "visit_count": visit_count,
            "brief_graph": {
                "feature": primary_feature,
                "points": primary_graph
            }
        }

        patient_cards.append(card)

    return {
        "global_primary_volatility_feature": primary_feature,
        "patient_cards": patient_cards
    }


def build_single_patient_detail(
    master_event_log,
    train_ready_df,
    patno
):
    master_event_log = _normalize_event_log(master_event_log)

    train_ready_df = train_ready_df.copy()
    train_ready_df["PATNO"] = train_ready_df["PATNO"].astype(str).str.strip()

    patno = str(patno).strip()

    patient_row = train_ready_df[
        train_ready_df["PATNO"] == patno
    ]

    if patient_row.empty:
        return None

    patient_row = patient_row.iloc[0]

    patient_log = master_event_log[
        master_event_log["PATNO"] == patno
    ].copy()

    if patient_log.empty:
        patient_log = _empty_event_log()

    primary_feature = _find_global_primary_volatility_feature(
        train_ready_df
    )

    dpvi_cols = _get_dpvi_columns(train_ready_df)

    return _build_patient_detail_from_prepared_data(
        patno=patno,
        patient_row=patient_row,
        patient_log=patient_log,
        primary_feature=primary_feature,
        dpvi_cols=dpvi_cols
    )

def _get_winner_model_context(dashboard_results, train_ready_df):
    dashboard_results = dashboard_results or {}

    selection = dashboard_results.get("selection", {})
    analysis = dashboard_results.get("analysis", {})
    prediction = dashboard_results.get("prediction", {})

    feature_importance = analysis.get("feature_importance", [])[:5]

    thresholds = []

    for item in feature_importance:
        feature = item.get("feature")

        thresholds.append({
            "feature": feature,
            "importance": item.get("importance"),
            "threshold_value": _safe_round(
                item.get("model_threshold"),
                4
            )
        })

    return {
        "selected_pipeline": selection.get("selected_pipeline"),
        "winner_model": selection.get("best_model"),
        "selection_rule": [
            "Among 4 experiment blocks, choose the block with highest average accuracy elevation.",
            "Inside that chosen block, choose the proposed DPVI model with highest accuracy.",
            "Use that model’s metrics for Prediction page and Analysis page.",
            "Use its matching baseline row for comparison and ablation."
        ],
        "model_probability_threshold": prediction.get(
            "model_probability_threshold"
        ),
        "average_accuracy_elevation_percent": selection.get(
            "average_accuracy_elevation_percent"
        ),
        "baseline_accuracy_percent": prediction.get(
            "baseline_accuracy_percent"
        ),
        "accuracy_elevation_percent": prediction.get(
            "accuracy_elevation_percent"
        ),
        "feature_thresholds": thresholds
    }


def _build_patient_feature_thresholds(patient_row, winner_context):
    rows = []

    for item in winner_context.get("feature_thresholds", []):
        feature = item.get("feature")
        threshold = item.get("threshold_value")

        patient_value = _safe_round(
            patient_row.get(feature, np.nan),
            4
        )

        if patient_value is None or threshold is None:
            relation = "Unavailable"
        elif patient_value >= threshold:
            relation = "Above best-model reference cut-off"
        else:
            relation = "Below best-model reference cut-off"

        rows.append({
            "feature": feature,
            "patient_value": patient_value,
            "threshold_value": threshold,
            "relation": relation
        })

    return rows


def _build_patient_interpretation(
    actual_status,
    dpvi_predicted_status,
    baseline_predicted_status,
    dpvi_prediction_result,
    baseline_prediction_result,
    dpvi_score,
    prediction_confidence,
    instability,
    primary_feature,
    winner_context
):
    winner_model = winner_context.get("winner_model", "selected DPVI model")
    selected_pipeline = winner_context.get("selected_pipeline", "selected pipeline")

    if (
        baseline_prediction_result == "Misclassified"
        and dpvi_prediction_result == "Correct"
    ):
        correlation_text = (
            "For this patient, the baseline model failed to match the actual "
            "clinical status, while the DPVI model matched it correctly. This "
            "shows that longitudinal DPVI features added useful patient-specific "
            "progression information."
        )
    else:
        correlation_text = (
            "This patient-level comparison shows how baseline and DPVI predictions "
            "relate to the actual clinical status."
        )

    return {
        "correlation_of_status": correlation_text,

        "clinical_interpretation": (
            f"The patient is clinically marked as {actual_status}. The DPVI "
            f"prediction is {dpvi_predicted_status}, while the baseline prediction "
            f"is {baseline_predicted_status}. The DPVI score is {dpvi_score}, "
            f"indicating {instability.lower()} behaviour."
        ),

        "dpvi_contribution": (
            f"DPVI contributes by using longitudinal volatility features instead "
            f"of relying only on static baseline values. The primary observed "
            f"volatility feature for this patient is {primary_feature}."
        ),

        "prediction_insights": (
            f"The winning model used for dashboard prediction is {winner_model} "
            f"from the {selected_pipeline}. The winner-model probability threshold of "
            f"{winner_context.get('model_probability_threshold')} is "
            f"used to separate disease present and disease absent classes."
        ),

        "explainability_insights": (
            "The displayed feature thresholds are reference thresholds derived "
            "from the important features of the winning model. They help explain "
            "whether this patient's DPVI feature values are above or below the "
            "model-level reference pattern."
        ),

        "ablation_analysis": (
            f"The matching baseline accuracy is "
            f"{winner_context.get('baseline_accuracy_percent', 'N/A')}, and the "
            f"DPVI accuracy elevation is "
            f"{winner_context.get('accuracy_elevation_percent', 'N/A')}. This "
            f"shows the effect of adding DPVI features over the baseline setup."
        )
    }

def _build_patient_detail_from_prepared_data(
    patno,
    patient_row,
    patient_log,
    primary_feature,
    dpvi_cols,
    winner_context=None
):
    if patient_log is None or patient_log.empty:
        patient_log = _empty_event_log()

    if dpvi_cols:
        dpvi_values = pd.to_numeric(
            patient_row[dpvi_cols],
            errors="coerce"
        )
        dpvi_score = dpvi_values.mean()
    else:
        dpvi_score = np.nan

    actual_status = _status_text(
        patient_row.get("FINAL_STATUS", np.nan)
    )

    dpvi_predicted_status = _status_text(
        patient_row.get("DPVI_PREDICTED_STATUS", np.nan)
    )

    baseline_predicted_status = _status_text(
        patient_row.get("BASELINE_PREDICTED_STATUS", np.nan)
    )

    primary_graph = _build_feature_series(
        patient_log,
        primary_feature
    )

    visit_count = (
        int(patient_log["EVENT_ID"].nunique())
        if not patient_log.empty and "EVENT_ID" in patient_log.columns
        else 0
    )

    winner_context = winner_context or {}

    dpvi_prediction_result = _prediction_result(
        actual_status,
        dpvi_predicted_status
    )

    baseline_prediction_result = _prediction_result(
        actual_status,
        baseline_predicted_status
    )

    patient_feature_thresholds = _build_patient_feature_thresholds(
        patient_row,
        winner_context
    )

    patient_interpretation = _build_patient_interpretation(
        actual_status=actual_status,
        dpvi_predicted_status=dpvi_predicted_status,
        baseline_predicted_status=baseline_predicted_status,
        dpvi_prediction_result=dpvi_prediction_result,
        baseline_prediction_result=baseline_prediction_result,
        dpvi_score=_safe_round(dpvi_score, 4),
        prediction_confidence=_safe_round(
            patient_row.get("PREDICTION_CONFIDENCE", np.nan),
            4
        ),
        instability=_instability_label(dpvi_score),
        primary_feature=primary_feature,
        winner_context=winner_context
    )


    return {
        "patno": str(patno),
        "actual_status": actual_status,
        "dpvi_predicted_status": dpvi_predicted_status,
        "baseline_predicted_status": baseline_predicted_status,
        "dpvi_prediction_result": dpvi_prediction_result,
        "baseline_prediction_result": baseline_prediction_result,
        "prediction_confidence": _safe_round(
            patient_row.get("PREDICTION_CONFIDENCE", np.nan),
            4
        ),
        "dpvi_score": _safe_round(dpvi_score, 4),
        "instability": _instability_label(dpvi_score),
        "primary_volatility_feature": primary_feature,
        "trend_summary": _trend_summary(dpvi_score),
        "visit_count": visit_count,
        "primary_graph": {
            "feature": primary_feature,
            "points": primary_graph
        },
        "multi_feature_graph": _build_multi_feature_graph(
            patient_log
        ),
        "visit_table": _build_visit_table(
            patient_log
        ),
        "dpvi_metrics": {
            "dpvi_score": _safe_round(dpvi_score, 4),
            "available_dpvi_features": len(dpvi_cols),
        },
        "winner_model_context": winner_context,
        "patient_feature_thresholds": patient_feature_thresholds,
        "patient_interpretation": patient_interpretation
    }


def _build_single_patient_detail_parallel(task):
    (
        patno,
        patient_row_dict,
        patient_log,
        primary_feature,
        dpvi_cols,
        winner_context
    ) = task

    patient_row = pd.Series(patient_row_dict)

    patient_detail = _build_patient_detail_from_prepared_data(
        patno=patno,
        patient_row=patient_row,
        patient_log=patient_log,
        primary_feature=primary_feature,
        dpvi_cols=dpvi_cols,
        winner_context=winner_context
    )

    return str(patno), patient_detail


def build_all_patient_details(
    master_event_log,
    train_ready_df,
    dashboard_results=None,
    max_workers=None
):
    master_event_log = _normalize_event_log(master_event_log)

    train_ready_df = train_ready_df.copy()
    train_ready_df["PATNO"] = train_ready_df["PATNO"].astype(str).str.strip()

    primary_feature = _find_global_primary_volatility_feature(
        train_ready_df
    )

    dpvi_cols = _get_dpvi_columns(train_ready_df)

    winner_context = _get_winner_model_context(
        dashboard_results,
        train_ready_df
    )

    patient_log_groups = {
        str(patno): group.copy()
        for patno, group in master_event_log.groupby("PATNO")
    }

    tasks = []

    for _, row in train_ready_df.iterrows():
        patno = str(row["PATNO"]).strip()

        tasks.append(
            (
                patno,
                row.to_dict(),
                patient_log_groups.get(patno, _empty_event_log()),
                primary_feature,
                dpvi_cols,
                winner_context
            )
        )

    if max_workers is None:
        max_workers = min(32, os.cpu_count() or 1)

    max_workers = max(1, int(max_workers))

    patient_details = {}

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_build_single_patient_detail_parallel, task)
            for task in tasks
        ]

        for future in as_completed(futures):
            patno, patient_detail = future.result()

            if patient_detail is not None:
                patient_details[str(patno)] = patient_detail

    return patient_details