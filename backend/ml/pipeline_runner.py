import pandas as pd
import traceback
from ml.config import TARGET_FEATURES

from ml.grid_search_runner import run_parallel_grid_search_cv
import os
import pickle

from ml.data_loader import load_all_datasets
from ml.event_stream import transform_to_event_stream

from ml.dpvi_engine import (
    generate_patient_master_matrix,
    optimize_dpvi_features
)

from ml.label_builder import (
    generate_status_matrix,
    generate_patient_labels,
    merge_features_with_labels
)

from ml.model_trainer import (
    run_parkinsons_elevation_study,
    run_parkinsons_cv_elevation_study,
    run_parkinsons_weighted_elevation_study,
    run_parkinsons_weighted_cv_elevation_study
)

from ml.dashboard_builder import build_dashboard_results

from ml.visualization import (
    build_patient_visualization_data,
    build_all_patient_details
)

# =========================================================
# GLOBAL RESULTS STORAGE
# =========================================================

LATEST_RESULTS = {}


CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "cache"
)

CACHE_FILE = os.path.join(
    CACHE_DIR,
    "latest_results.pkl"
)

# =========================================================
# HELPER: SEND LIVE PROGRESS TO GUI
# =========================================================

def send_progress(callback, message):

    print(message)

    if callback:
        callback(message)

# =========================================================
# frontend helper..
# =========================================================


def get_frontend_safe_results(results):
    hidden_keys = {
        "_master_event_log",
        "_train_ready_df",
        "_terminal_snapshot"
    }

    return {
        key: value
        for key, value in results.items()
        if key not in hidden_keys
    }

# =========================================================
# frontend page specific helper...
# =========================================================

def get_prediction_results():
    results = get_latest_results()

    return {
        "summary": results.get("summary", {}),
        "prediction": results.get("prediction", {}),
        "selection": results.get("selection", {}),
        "grid_search_cv": results.get("grid_search_cv", [])
    }


def get_analysis_results():
    results = get_latest_results()

    return {
        "summary": results.get("summary", {}),
        "analysis": results.get("analysis", {}),
        "selection": results.get("selection", {})
    }


def get_graph_results():
    results = get_latest_results()

    return {
        "graphs": results.get("graphs", {})
    }


def get_ledger_results():
    results = get_latest_results()

    return {
        "ledgers": results.get("ledgers", {})
    }


def get_patient_visualization_results():
    results = get_latest_results()

    return {
        "patient_visualization": results.get("patient_visualization", [])
    }


def get_patient_detail_by_patno(patno):
    results = get_latest_results()
    patient_details = results.get("patient_details", {})

    patno = str(patno).strip()

    if isinstance(patient_details, dict):
        return patient_details.get(patno)

    for patient in patient_details:
        if str(patient.get("patno", patient.get("PATNO"))).strip() == patno:
            return patient

    return None

# =========================================================
# TERMINAL DISPLAY HELPERS
# =========================================================

def print_terminal_section(title, description=None):
    print("\n" + "═" * 80)
    print(title)
    print("═" * 80)

    if description:
        print(f"📌 {description}")

    print("-" * 80)

def print_target_feature_names():
    print_terminal_section(
        "🎯 31 TARGET FEATURES USED FOR DPVI",
        "Same target feature list used for fresh pipeline execution and cached replay."
    )

    print(f"📌 Total Target Features : {len(TARGET_FEATURES)}")

    for index, feature in enumerate(TARGET_FEATURES, start=1):
        print(f"{index:02d}. {feature}")

    print("═" * 80)

def print_dataframe_preview(title, df, description=None, rows=3):
    print_terminal_section(title, description)

    if df is None or df.empty:
        print("⚠️ No data available.")
        print("═" * 80)
        return

    print(f"📊 Shape   : {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"📑 Columns : {list(df.columns[:8])}")

    if df.shape[1] > 8:
        print(f"           + {df.shape[1] - 8} more columns")

    print("\n🔍 Head:")
    print(df.head(rows))
    print("═" * 80)


def print_dataset_group_preview(dataset_dict, group_name, rows=3):
    print_terminal_section(
        f"📂 {group_name.upper()} DATASETS LOADED",
        "Raw CSV files loaded successfully before event-stream conversion."
    )

    if not dataset_dict:
        print("⚠️ No files loaded.")
        print("═" * 80)
        return

    total_rows = sum(df.shape[0] for df in dataset_dict.values())

    print(f"📁 Files Loaded : {len(dataset_dict)}")
    print(f"📊 Total Rows   : {total_rows:,}")

    first_file = list(dataset_dict.keys())[0]
    first_df = dataset_dict[first_file]

    print(f"\n📄 Sample File  : {first_file}")
    print(f"📐 File Shape   : {first_df.shape[0]:,} rows × {first_df.shape[1]} columns")
    print("\n🔍 Head:")
    print(first_df.head(rows))
    print("═" * 80)


def print_label_summary(patient_labels):
    print_dataframe_preview(
        "🏷️ PATIENT LABELS CREATED",
        patient_labels,
        "Final patient status labels generated from diagnosis, questionnaire and disease-stage records.",
        rows=3
    )

    if "FINAL_STATUS" in patient_labels.columns:
        print("\n🎯 Label Distribution:")
        print(patient_labels["FINAL_STATUS"].value_counts())
        print("═" * 80)


def print_feature_summary(df, title, description):
    print_dataframe_preview(title, df, description, rows=3)

    baseline_cols = [c for c in df.columns if c.startswith("BASE_")]
    dpvi_cols = [c for c in df.columns if c.startswith("DPVI_")]

    print(f"📌 Baseline Features : {len(baseline_cols)}")
    print(f"🧠 DPVI Features     : {len(dpvi_cols)}")

    if "FINAL_STATUS" in df.columns:
        print("🎯 Target Column     : FINAL_STATUS")

    print("═" * 80)


def print_gridsearch_summary(grid_search_results):
    print_terminal_section(
        "🔎 GRIDSEARCHCV COMPLETED",
        "Best hyperparameters selected for Random Forest, XGBoost and Gradient Boosting."
    )

    for row in grid_search_results:
        print(f"\n🤖 Model          : {row.get('Model', 'N/A')}")
        print(f"✅ Best CV Score  : {row.get('Best_CV_Score', 'N/A')}")
        print(f"🎯 Test Accuracy  : {row.get('Test_Accuracy', 'N/A')}")
        print("⚙️ Best Parameters:")

        for key, value in row.get("Best_Params", {}).items():
            print(f"   • {key}: {value}")

    print("═" * 80)


def print_experiment_summary(title, result):
    print_terminal_section(
        title,
        "Compact model performance summary."
    )

    ledger = result.get("ledger", [])

    if not ledger:
        print("⚠️ No ledger available.")
        print("═" * 80)
        return

    for row in ledger:
        print(
            f"🤖 {row.get('Model', 'N/A')} | "
            f"{row.get('Approach', 'N/A')} | "
            f"Accuracy: {row.get('Accuracy', 'N/A')} | "
        )

    print("═" * 80)


def print_winner_model_summary(dashboard_results):
    selection = dashboard_results.get("selection", {})
    prediction = dashboard_results.get("prediction", {})

    print_terminal_section(
        "🏆 BEST MODEL SELECTED",
        "Final model selected using the project best model-selection rule."
    )

    print("📌 Selection Rule:")
    print("1. Choose the experiment block with highest average accuracy elevation.")
    print("2. Inside that block, choose the proposed DPVI model with highest accuracy.")
    print("3. Use that model for Prediction and Analysis pages.")
    print("4. Use its matching baseline row for comparison and ablation.")

    print("\n✅ Selected Pipeline :", selection.get("selected_pipeline", "N/A"))
    print("✅ Selected Dataset  :", selection.get("selected_dataset", "N/A"))
    print("🤖 Best Model      :", selection.get("best_model", "N/A"))
    print("📈 Risk Level        :", prediction.get("risk_level", "N/A"))
    print("🧠 DPVI Score        :", prediction.get("dpvi_score", "N/A"))
    print("📊 Accuracy Elevation:", prediction.get("accuracy_elevation_percent", "N/A"))

    print("═" * 80)

def create_terminal_snapshot(
    motor_data,
    non_motor_data,
    digital_sensor_data,
    biospecimen_data,
    medical_history_data,
    master_event_log,
    final_ml_data,
    patient_labels,
    train_ready_df,
    train_ready_df_weighted,
    grid_search_results,
    full_train_test,
    full_cv,
    weighted_train_test,
    weighted_cv,
    dashboard_results,
    patient_visualization,
    patient_details,
    worker_count
):
    def dataset_snapshot(dataset_dict):
        if not dataset_dict:
            return None

        first_file = list(dataset_dict.keys())[0]
        first_df = dataset_dict[first_file]

        return {
            "files_loaded": len(dataset_dict),
            "total_rows": int(sum(df.shape[0] for df in dataset_dict.values())),
            "sample_file": first_file,
            "sample_shape": first_df.shape,
            "sample_head": first_df.head(3)
        }

    return {
        "datasets": {
            "Motor": dataset_snapshot(motor_data),
            "Non-Motor": dataset_snapshot(non_motor_data),
            "Digital Sensor": dataset_snapshot(digital_sensor_data),
            "Biospecimen": dataset_snapshot(biospecimen_data),
            "Medical History": dataset_snapshot(medical_history_data)
        },
        "master_event_log": master_event_log.head(3),
        "master_event_shape": master_event_log.shape,
        "master_unique_patients": int(master_event_log["PATNO"].nunique()),
        "master_unique_measures": int(master_event_log["MEASURE_NAME"].nunique()),
        "master_categories": int(master_event_log["CATEGORY"].nunique()),
        "final_ml_data": final_ml_data.head(3),
        "final_ml_shape": final_ml_data.shape,
        "patient_labels": patient_labels.head(3),
        "patient_label_shape": patient_labels.shape,
        "label_distribution": patient_labels["FINAL_STATUS"].value_counts(),
        "train_ready_df": train_ready_df.head(3),
        "train_ready_shape": train_ready_df.shape,
        "train_ready_df_weighted": train_ready_df_weighted.head(3),
        "weighted_shape": train_ready_df_weighted.shape,
        "grid_search_results": grid_search_results,
        "full_train_test": {"ledger": full_train_test.get("ledger", [])},
        "full_cv": {"ledger": full_cv.get("ledger", [])},
        "weighted_train_test": {"ledger": weighted_train_test.get("ledger", [])},
        "weighted_cv": {"ledger": weighted_cv.get("ledger", [])},
        "dashboard_results": dashboard_results,
        "patient_visualization_count": len(patient_visualization) if patient_visualization else 0,
        "patient_details_count": len(patient_details) if patient_details else 0,
        "worker_count": worker_count
    }

def replay_cached_terminal_flow(results, progress_callback=None):
    snapshot = results.get("_terminal_snapshot")

    if not snapshot:
        print_terminal_section(
            "💾 CACHED RESULTS LOADED",
            "Cache found, but old cache does not contain terminal replay snapshot. Run pipeline once to create it."
        )
        return

    send_progress(progress_callback, "🚀 Starting DPVI Processing Pipeline...")

    send_progress(progress_callback, "📂 Loading Motor Datasets...")
    send_progress(progress_callback, "📂 Loading Non-Motor Datasets...")
    send_progress(progress_callback, "📂 Loading Digital Sensor Datasets...")
    send_progress(progress_callback, "📂 Loading Biospecimen Datasets...")
    send_progress(progress_callback, "📂 Loading Medical History Datasets...")
    send_progress(progress_callback, "✅ All datasets loaded successfully")

    for group_name, data in snapshot["datasets"].items():
        print_terminal_section(
            f"📂 {group_name.upper()} DATASETS LOADED",
            "Loaded from cached terminal snapshot."
        )

        if not data:
            print("⚠️ No data available.")
            print("═" * 80)
            continue

        print(f"📁 Files Loaded : {data['files_loaded']}")
        print(f"📊 Total Rows   : {data['total_rows']:,}")
        print(f"\n📄 Sample File  : {data['sample_file']}")
        print(f"📐 File Shape   : {data['sample_shape'][0]:,} rows × {data['sample_shape'][1]} columns")
        print("\n🔍 Head:")
        print(data["sample_head"])
        print("═" * 80)

    send_progress(progress_callback, "⚙ Creating Master Event Streams...")
    send_progress(progress_callback, f"✅ Master Event Log Created | Rows: {snapshot['master_event_shape'][0]:,}")

    print_dataframe_preview(
        "⚙️ MASTER EVENT LOG CREATED",
        snapshot["master_event_log"],
        "All dataset groups are converted into one longitudinal event-stream table.",
        rows=3
    )

    print(f"👤 Unique Patients : {snapshot['master_unique_patients']:,}")
    print(f"🧪 Unique Measures : {snapshot['master_unique_measures']:,}")
    print(f"📂 Categories      : {snapshot['master_categories']:,}")
    print("═" * 80)

    send_progress(progress_callback, "🧠 Computing Full DPVI Features...")
    send_progress(progress_callback, "🧠 Computed  Full DPVI Features for the dataset...")
    send_progress(progress_callback, f"✅ Full DPVI Dataset Ready | Shape: {snapshot['final_ml_shape']}")

    print_dataframe_preview(
        "🧠 FULL DPVI FEATURE MATRIX CREATED",
        snapshot["final_ml_data"],
        "Each patient is converted into baseline mean features and longitudinal DPVI volatility features.",
        rows=3
    )

    send_progress(progress_callback, "🏷 Generating Patient Labels...")
    send_progress(progress_callback, f"✅ Patient Labels Created | Patients: {snapshot['patient_label_shape'][0]:,}")

    print_dataframe_preview(
        "🏷️ PATIENT LABELS CREATED",
        snapshot["patient_labels"],
        "Final patient status labels generated from diagnosis, questionnaire and disease-stage records.",
        rows=3
    )

    print("\n🎯 Label Distribution:")
    print(snapshot["label_distribution"])
    print("═" * 80)

    send_progress(progress_callback, "🔗 Merging Features With Labels...")
    send_progress(
        progress_callback,
        f"✅ FINAL DIMENSIONS: {snapshot['train_ready_shape'][0]:,} Patients x {snapshot['train_ready_shape'][1]} Columns"
    )

    print_dataframe_preview(
        "🔗 TRAIN-READY FULL DPVI DATASET CREATED",
        snapshot["train_ready_df"],
        "DPVI patient features are merged with final clinical labels for model training.",
        rows=3
    )

    send_progress(progress_callback, "🔎 Running GridSearchCV for 3 models using parallel processes...")
    send_progress(progress_callback, "✅ GridSearchCV Completed for Random Forest, Gradient Boosting and XGBoost")
    print_gridsearch_summary(snapshot["grid_search_results"])

    send_progress(progress_callback, "🤖 Training Full DPVI Train/Test Models...")
    send_progress(progress_callback, "✅ Full DPVI Train/Test Completed")
    print_experiment_summary("🤖 FULL DPVI TRAIN/TEST COMPLETED", snapshot["full_train_test"])

    send_progress(progress_callback, "📊 Running Full DPVI 3-Fold Cross Validation...")
    send_progress(progress_callback, "✅ Full DPVI Cross Validation Completed")
    print_experiment_summary("📊 FULL DPVI 3-FOLD CROSS VALIDATION COMPLETED", snapshot["full_cv"])

    send_progress(progress_callback, "⚡ Generating Weighted DPVI Dataset...")
    send_progress(
        progress_callback,
        f"✅ FINAL DIMENSIONS: {snapshot['weighted_shape'][0]:,} Patients x {snapshot['weighted_shape'][1]} Columns"
    )

    print_dataframe_preview(
        "⚡ WEIGHTED DPVI DATASET CREATED",
        snapshot["train_ready_df_weighted"],
        "Five DPVI components are fused into one weighted DPVI score per clinical signal.",
        rows=3
    )

    send_progress(progress_callback, "🤖 Training Weighted DPVI Train/Test Models...")
    send_progress(progress_callback, "✅ Weighted DPVI Train/Test Completed")
    print_experiment_summary("🤖 WEIGHTED DPVI TRAIN/TEST COMPLETED", snapshot["weighted_train_test"])

    send_progress(progress_callback, "📊 Running Weighted DPVI 3-Fold Cross Validation...")
    send_progress(progress_callback, "✅ Weighted DPVI Cross Validation Completed")
    print_experiment_summary("📊 WEIGHTED DPVI 3-FOLD CROSS VALIDATION COMPLETED", snapshot["weighted_cv"])

    send_progress(progress_callback, "📈 Building Dynamic Prediction and Analysis Results...")
    send_progress(progress_callback, "✅ Dynamic Dashboard Results Created")
    print_winner_model_summary(snapshot["dashboard_results"])

    send_progress(progress_callback, "🧬 Building Patient Progression Visualization Data...")
    send_progress(progress_callback, "✅ Patient Visualization Data Created")

    print_terminal_section(
        "🧬 PATIENT VISUALIZATION DATA CREATED",
        "Patient-level visualization data prepared for frontend pages."
    )
    print(f"📊 Records Prepared : {snapshot['patient_visualization_count']}")
    print("🚫 Graph data not printed because it is displayed on frontend.")
    print("═" * 80)

    send_progress(progress_callback, "📈  Building Patient Progression Detail Visualization Data...")
    send_progress(
        progress_callback,
        f"✅ Patient Detail Visualization Data Created using {snapshot['worker_count']} parallel processes"
    )

    print_terminal_section(
        "📈 PATIENT DETAIL DATA CREATED",
        "Visit-wise patient detail data prepared using parallel processing."
    )
    print(f"⚙️ Parallel Workers : {snapshot['worker_count']}")
    print(f"👤 Patient Details  : {snapshot['patient_details_count']}")
    print("🚫 Full patient detail JSON not printed because it is displayed on frontend.")
    print("═" * 80)

    print_terminal_section(
        "💾 RESULTS LOADED FROM CACHE",
        "Cached backend results restored for faster frontend reload."
    )
    print(f"📁 Cache File : {CACHE_FILE}")
    print("✅ Cache Status: Loaded successfully")
    print("═" * 80)

    send_progress(progress_callback, "🎉 Pipeline Execution Completed Successfully")

def save_latest_results_to_cache(results):
    os.makedirs(
        CACHE_DIR,
        exist_ok=True
    )

    with open(CACHE_FILE, "wb") as file:
        pickle.dump(
            results,
            file
        )


def load_latest_results_from_cache():
    if not os.path.exists(CACHE_FILE):
        return None

    with open(CACHE_FILE, "rb") as file:
        return pickle.load(file)


def has_cached_results():
    return os.path.exists(CACHE_FILE)

# =========================================================
# MAIN PIPELINE
# =========================================================

def run_full_pipeline(progress_callback=None):

    global LATEST_RESULTS

    try:

        send_progress(
            progress_callback,
            "🚀 Starting DPVI Processing Pipeline..."
        )

        # =====================================================
        # STEP 1: LOAD DATASETS
        # =====================================================

        send_progress(progress_callback, "📂 Loading Motor Datasets...")
        send_progress(progress_callback, "📂 Loading Non-Motor Datasets...")
        send_progress(progress_callback, "📂 Loading Digital Sensor Datasets...")
        send_progress(progress_callback, "📂 Loading Biospecimen Datasets...")
        send_progress(progress_callback, "📂 Loading Medical History Datasets...")

        (
            motor_data,
            non_motor_data,
            digital_sensor_data,
            biospecimen_data,
            medical_history_data
        ) = load_all_datasets()

        send_progress(
            progress_callback,
            "✅ All datasets loaded successfully"
        )

        print_dataset_group_preview(motor_data, "Motor")
        print_dataset_group_preview(non_motor_data, "Non-Motor")
        print_dataset_group_preview(digital_sensor_data, "Digital Sensor")
        print_dataset_group_preview(biospecimen_data, "Biospecimen")
        print_dataset_group_preview(medical_history_data, "Medical History")

        # =====================================================
        # STEP 2: CREATE EVENT STREAMS
        # =====================================================

        send_progress(
            progress_callback,
            "⚙ Creating Master Event Streams..."
        )

        stream_1 = transform_to_event_stream(
            motor_data,
            "MOTOR"
        )

        stream_2 = transform_to_event_stream(
            non_motor_data,
            "NON_MOTOR"
        )

        stream_3 = transform_to_event_stream(
            digital_sensor_data,
            "DIGITAL_SENSOR"
        )

        stream_4 = transform_to_event_stream(
            biospecimen_data,
            "BIOSPECIMEN"
        )

        stream_5 = transform_to_event_stream(
            medical_history_data,
            "HISTORY"
        )

        master_event_log = pd.concat(
            [
                stream_1,
                stream_2,
                stream_3,
                stream_4,
                stream_5
            ],
            axis=0
        )

        master_event_log["MEASURE_VALUE"] = pd.to_numeric(
            master_event_log["MEASURE_VALUE"],
            errors="coerce"
        )

        master_event_log = master_event_log.dropna(
            subset=["MEASURE_VALUE"]
        )

        master_event_log["PATNO"] = (
            master_event_log["PATNO"]
            .astype(str)
            .str.strip()
        )

        master_event_log = master_event_log.sort_values(
            by=["PATNO", "EVENT_ID"]
        )

        send_progress(
            progress_callback,
            f"✅ Master Event Log Created | Rows: {len(master_event_log):,}"
        )

        print_dataframe_preview(
            "⚙️ MASTER EVENT LOG CREATED",
            master_event_log,
            "All dataset groups are converted into one longitudinal event-stream table.",
            rows=3
        )

        print(f"👤 Unique Patients : {master_event_log['PATNO'].nunique():,}")
        print(f"🧪 Unique Measures : {master_event_log['MEASURE_NAME'].nunique():,}")
        print(f"📂 Categories      : {master_event_log['CATEGORY'].nunique():,}")
        print("═" * 80)

        # =====================================================
        # STEP 3: GENERATE FULL DPVI DATASET
        # =====================================================

        send_progress(
            progress_callback,
            "🧠 Computing Full DPVI Features..."
        )

        print_target_feature_names()

        final_ml_data = generate_patient_master_matrix(
            master_event_log
        )

        send_progress(
            progress_callback,
            "🧠 Computed  Full DPVI Features for the dataset..."
        )

        send_progress(
            progress_callback,
            f"✅ Full DPVI Dataset Ready | Shape: {final_ml_data.shape}"
        )

        print_feature_summary(
            final_ml_data,
            "🧠 FULL DPVI FEATURE MATRIX CREATED",
            "Each patient is converted into baseline mean features and longitudinal DPVI volatility features."
        )

        # =====================================================
        # STEP 4: GENERATE LABELS
        # =====================================================

        send_progress(
            progress_callback,
            "🏷 Generating Patient Labels..."
        )

        full_status_data = generate_status_matrix()

        patient_labels = generate_patient_labels(
            full_status_data
        )


        send_progress(
            progress_callback,
            f"✅ Patient Labels Created | Patients: {len(patient_labels):,}"
        )

        print_label_summary(patient_labels)

        # =====================================================
        # STEP 5: CREATE TRAIN-READY FULL DPVI DATASET
        # =====================================================

        send_progress(
            progress_callback,
            "🔗 Merging Features With Labels..."
        )

        train_ready_df = merge_features_with_labels(
            final_ml_data,
            patient_labels
        )

        send_progress(
            progress_callback,
            f"✅ FINAL DIMENSIONS: "
            f"{train_ready_df.shape[0]:,} Patients x "
            f"{train_ready_df.shape[1]} Columns"
        )

        print_feature_summary(
            train_ready_df,
            "🔗 TRAIN-READY FULL DPVI DATASET CREATED",
            "DPVI patient features are merged with final clinical labels for model training."
        )

        send_progress(
            progress_callback,
            "🔎 Running GridSearchCV for 3 models using parallel processes..."
        )

        grid_search_results = run_parallel_grid_search_cv(
            train_ready_df,
            max_workers=3
        )

        best_params_map = {
            row["Model"]: row["Best_Params"]
            for row in grid_search_results
        }

        send_progress(
            progress_callback,
            "✅ GridSearchCV Completed for Random Forest, Gradient Boosting and XGBoost"
        )

        # =====================================================
        # PRINT BEST GRIDSEARCH PARAMETERS
        # =====================================================

        print_gridsearch_summary(grid_search_results)


        # =====================================================
        # STEP 6: FULL DPVI TRAIN/TEST EXPERIMENT
        # =====================================================

        send_progress(
            progress_callback,
            "🤖 Training Full DPVI Train/Test Models..."
        )

        full_train_test = run_parkinsons_elevation_study(
            train_ready_df,
            best_params_map=best_params_map
        )

        send_progress(
            progress_callback,
            "✅ Full DPVI Train/Test Completed"
        )

        print_experiment_summary(
            "🤖 FULL DPVI TRAIN/TEST COMPLETED",
            full_train_test
        )

        #=====================================================
        # STEP 7: FULL DPVI CROSS-VALIDATION EXPERIMENT
        # =====================================================

        send_progress(
            progress_callback,
            "📊 Running Full DPVI 3-Fold Cross Validation..."
        )

        full_cv = run_parkinsons_cv_elevation_study(
            train_ready_df,
            best_params_map=best_params_map
        )

        send_progress(
            progress_callback,
            "✅ Full DPVI Cross Validation Completed"
        )

        print_experiment_summary(
            "📊 FULL DPVI 3-FOLD CROSS VALIDATION COMPLETED",
            full_cv
        )

        # =====================================================
        # STEP 8: WEIGHTED DPVI DATASET
        # =====================================================

        send_progress(
            progress_callback,
            "⚡ Generating Weighted DPVI Dataset..."
        )

        train_ready_df_weighted = optimize_dpvi_features(
            train_ready_df
        )

        send_progress(
            progress_callback,
            f"✅ FINAL DIMENSIONS: "
            f"{train_ready_df_weighted.shape[0]:,} Patients x "
            f"{train_ready_df_weighted.shape[1]} Columns"
        )
        print_feature_summary(
            train_ready_df_weighted,
            "⚡ WEIGHTED DPVI DATASET CREATED",
            "Five DPVI components are fused into one weighted DPVI score per clinical signal."
        )


        # =====================================================
        # STEP 9: WEIGHTED DPVI TRAIN/TEST EXPERIMENT
        # =====================================================

        send_progress(
            progress_callback,
            "🤖 Training Weighted DPVI Train/Test Models..."
        )

        weighted_train_test = run_parkinsons_weighted_elevation_study(
            train_ready_df_weighted,
            best_params_map=best_params_map
        )

        send_progress(
            progress_callback,
            "✅ Weighted DPVI Train/Test Completed"
        )
        print_experiment_summary(
            "🤖 WEIGHTED DPVI TRAIN/TEST COMPLETED",
            weighted_train_test
        )

        # =====================================================
        # STEP 10: WEIGHTED DPVI CROSS-VALIDATION EXPERIMENT
        # =====================================================

        send_progress(
            progress_callback,
            "📊 Running Weighted DPVI 3-Fold Cross Validation..."
        )

        weighted_cv = run_parkinsons_weighted_cv_elevation_study(
            train_ready_df_weighted,
            best_params_map=best_params_map
        )

        send_progress(
            progress_callback,
            "✅ Weighted DPVI Cross Validation Completed"
        )

        print_experiment_summary(
            "📊 WEIGHTED DPVI 3-FOLD CROSS VALIDATION COMPLETED",
            weighted_cv
        )

        # =====================================================
        # STEP 11: BUILD DYNAMIC DASHBOARD RESULTS
        # =====================================================

        send_progress(
            progress_callback,
            "📈 Building Dynamic Prediction and Analysis Results..."
        )

        dashboard_results = build_dashboard_results(
            full_train_test=full_train_test,
            full_cv=full_cv,
            weighted_train_test=weighted_train_test,
            weighted_cv=weighted_cv,
            train_ready_df=train_ready_df,
            train_ready_df_weighted=train_ready_df_weighted,
            grid_search_results=grid_search_results
        )

        selected_model = dashboard_results["selection"]["best_model"]
        #selected_pipeline = dashboard_results["selection"]["selected_pipeline"]
        selected_dataset = dashboard_results["selection"]["selected_dataset"]

        if "Weighted DPVI" in selected_dataset:
            prediction_source = weighted_cv
        else:
            prediction_source = full_cv

        patient_predictions_df = pd.DataFrame(
            prediction_source.get("patient_predictions", [])
        )

        train_ready_visualization_df = train_ready_df.copy()
        train_ready_visualization_df["PATNO"] = train_ready_visualization_df["PATNO"].astype(str)

        if not patient_predictions_df.empty:

            patient_predictions_df["PATNO"] = patient_predictions_df["PATNO"].astype(str)

            # -------------------------------
            # DPVI / PROPOSED PREDICTIONS
            # -------------------------------
            dpvi_predictions_df = patient_predictions_df[
                patient_predictions_df["Model"] == selected_model
            ]

            dpvi_predictions_df = dpvi_predictions_df[
                dpvi_predictions_df["Approach"].str.contains("Proposed", case=False, na=False)
            ]

            dpvi_predictions_df = dpvi_predictions_df[
                ["PATNO", "PREDICTED_STATUS", "PREDICTION_CONFIDENCE"]
            ].rename(
                columns={
                    "PREDICTED_STATUS": "DPVI_PREDICTED_STATUS",
                    "PREDICTION_CONFIDENCE": "DPVI_PREDICTION_CONFIDENCE"
                }
            )

            # -------------------------------
            # BASELINE PREDICTIONS
            # -------------------------------
            baseline_predictions_df = patient_predictions_df[
                patient_predictions_df["Model"] == selected_model
            ]

            baseline_predictions_df = baseline_predictions_df[
                baseline_predictions_df["Approach"].str.contains("Baseline", case=False, na=False)
            ]

            baseline_predictions_df = baseline_predictions_df[
                ["PATNO", "PREDICTED_STATUS", "PREDICTION_CONFIDENCE"]
            ].rename(
                columns={
                    "PREDICTED_STATUS": "BASELINE_PREDICTED_STATUS",
                    "PREDICTION_CONFIDENCE": "BASELINE_PREDICTION_CONFIDENCE"
                }
            )

            # -------------------------------
            # MERGE DPVI PREDICTIONS
            # -------------------------------
            train_ready_visualization_df = train_ready_visualization_df.merge(
                dpvi_predictions_df,
                on="PATNO",
                how="left"
            )

            # -------------------------------
            # MERGE BASELINE PREDICTIONS
            # -------------------------------
            train_ready_visualization_df = train_ready_visualization_df.merge(
                baseline_predictions_df,
                on="PATNO",
                how="left"
            )

            # keep old name also, so old code will not break
            train_ready_visualization_df["PREDICTED_STATUS"] = train_ready_visualization_df["DPVI_PREDICTED_STATUS"]
            train_ready_visualization_df["PREDICTION_CONFIDENCE"] = train_ready_visualization_df["DPVI_PREDICTION_CONFIDENCE"]

        send_progress(
            progress_callback,
            "✅ Dynamic Dashboard Results Created"
        )

        print_winner_model_summary(dashboard_results)

        # =====================================================
        # STEP 12: BUILD PATIENT VISUALIZATION DATA
        # =====================================================


        send_progress(
            progress_callback,
            "🧬 Building Patient Progression Visualization Data..."
        )

        patient_visualization = build_patient_visualization_data(
            master_event_log=master_event_log.copy(),
            train_ready_df=train_ready_visualization_df.copy(),
            train_ready_df_weighted=train_ready_df_weighted.copy(),
            dashboard_results=dashboard_results
        )

        send_progress(
            progress_callback,
            "✅ Patient Visualization Data Created"
        )

        print_terminal_section(
            "🧬 PATIENT VISUALIZATION DATA CREATED",
            "Patient-level visualization data prepared for frontend pages."
        )

        print(f"📊 Records Prepared : {len(patient_visualization) if patient_visualization else 0}")
        print("🚫 Graph data not printed because it is displayed on frontend.")
        print("═" * 80)

        send_progress(
            progress_callback,
            "📈  Building Patient Progression Detail Visualization Data..."
        )

        worker_count = min(32, os.cpu_count() or 1)
        patient_details = build_all_patient_details(
            master_event_log=master_event_log.copy(),
            train_ready_df=train_ready_visualization_df.copy(),
            dashboard_results=dashboard_results,
            max_workers=worker_count
        )


        send_progress(
            progress_callback,
            f"✅ Patient Detail Visualization Data Created "
            f"using {worker_count} parallel processes"
        )

        print_terminal_section(
            "📈 PATIENT DETAIL DATA CREATED",
            "Visit-wise patient detail data prepared using parallel processing."
        )

        print(f"⚙️ Parallel Workers : {worker_count}")
        print(f"👤 Patient Details  : {len(patient_details) if patient_details else 0}")
        print("🚫 Full patient detail JSON not printed because it is displayed on frontend.")
        print("═" * 80)

        # =====================================================
        # STEP 13: STORE ALL RESULTS FOR GUI
        # =====================================================

        LATEST_RESULTS = {
            **dashboard_results,

            "summary": {
                "patients": int(train_ready_df.shape[0]),
                "full_dpvi_columns": int(train_ready_df.shape[1]),
                "weighted_dpvi_columns": int(train_ready_df_weighted.shape[1]),
                "best_model": dashboard_results["selection"]["best_model"],
                "selected_pipeline": dashboard_results["selection"]["selected_pipeline"],
                "selected_dataset": dashboard_results["selection"]["selected_dataset"],
                "risk_level": dashboard_results["prediction"]["risk_level"],
                "dpvi_score": dashboard_results["prediction"]["dpvi_score"],
                "average_accuracy_elevation": dashboard_results["prediction"]["average_accuracy_elevation"],
                "average_accuracy_elevation_percent": dashboard_results["prediction"]["average_accuracy_elevation_percent"]
            },

            "graphs": {
                "full_train_test": full_train_test["graphs"],
                "full_cv": full_cv["graphs"],
                "weighted_train_test": weighted_train_test["graphs"],
                "weighted_cv": weighted_cv["graphs"]
            },

            "ledgers": {
                "full_train_test": full_train_test["ledger"],
                "full_cv": full_cv["ledger"],
                "weighted_train_test": weighted_train_test["ledger"],
                "weighted_cv": weighted_cv["ledger"]
            },

            "patient_visualization": patient_visualization,
            "patient_details": patient_details,
            "dashboard": dashboard_results,
            "_master_event_log": master_event_log.copy(),
            "_train_ready_df": train_ready_visualization_df.copy(),
            "grid_search_cv": grid_search_results,
            "_terminal_snapshot": create_terminal_snapshot(
                motor_data=motor_data,
                non_motor_data=non_motor_data,
                digital_sensor_data=digital_sensor_data,
                biospecimen_data=biospecimen_data,
                medical_history_data=medical_history_data,
                master_event_log=master_event_log,
                final_ml_data=final_ml_data,
                patient_labels=patient_labels,
                train_ready_df=train_ready_df,
                train_ready_df_weighted=train_ready_df_weighted,
                grid_search_results=grid_search_results,
                full_train_test=full_train_test,
                full_cv=full_cv,
                weighted_train_test=weighted_train_test,
                weighted_cv=weighted_cv,
                dashboard_results=dashboard_results,
                patient_visualization=patient_visualization,
                patient_details=patient_details,
                worker_count=worker_count
            )
        }

        save_latest_results_to_cache(
            LATEST_RESULTS
        )

        print_terminal_section(
            "💾 RESULTS SAVED TO CACHE",
            "Latest backend results stored for faster frontend reload."
        )

        print(f"📁 Cache File : {CACHE_FILE}")
        print("✅ Cache Status: Saved successfully")
        print("═" * 80)

        send_progress(
            progress_callback,
            "🎉 Pipeline Execution Completed Successfully"
        )

        return {
            "success": True,
            "results": LATEST_RESULTS
        }

    except Exception as e:

        traceback.print_exc()

        send_progress(
            progress_callback,
            f"❌ Pipeline Failed: {str(e)}"
        )

        return {
            "success": False,
            "error": str(e)
        }

# =========================================================
# FETCH RESULTS
# =========================================================
def get_latest_results(progress_callback=None, replay=False):

    global LATEST_RESULTS

    if LATEST_RESULTS:
        if replay:
            replay_cached_terminal_flow(
                LATEST_RESULTS,
                progress_callback=progress_callback
            )

        return get_frontend_safe_results(LATEST_RESULTS)

    cached_results = load_latest_results_from_cache()

    if cached_results is not None:
        LATEST_RESULTS = cached_results

        if replay:
            replay_cached_terminal_flow(
                LATEST_RESULTS,
                progress_callback=progress_callback
            )

        return get_frontend_safe_results(LATEST_RESULTS)

    return LATEST_RESULTS