import pandas as pd
import numpy as np
from scipy.stats import entropy
from ml.config import TARGET_FEATURES, DPVI_WEIGHTS


def calculate_dpvi_batch(series):
    """
    Calculates the 5 DPVI components for a patient's entire longitudinal history.
    """
    arr = series.dropna().values
    if len(arr) < 2:
        return [0.0, 0.0, 0.0, 0.0, 0.0]

    std_dev = np.std(arr)
    diffs = np.diff(arr)
    prog_rate = np.mean(diffs) if len(diffs) > 0 else 0.0

    threshold = std_dev if std_dev > 0 else 1.0
    spikes = np.sum(np.abs(diffs) > threshold)

    diff_signs = np.sign(diffs[diffs != 0])
    reversals = np.sum(np.diff(diff_signs) != 0) if len(diff_signs) > 1 else 0

    if std_dev > 0:
        counts, _ = np.histogram(arr, bins=5)
        total_counts = counts.sum()
        prob_dist = counts / total_counts if total_counts > 0 else counts
        ent = entropy(prob_dist)
    else:
        ent = 0.0

    return [std_dev, prog_rate, float(spikes), float(reversals), ent]


def generate_patient_master_matrix(event_log):
    #print(f"🚀 Processing {len(event_log):,} events into Patient-Level Baseline + DPVI Matrix...")

    master_wide = event_log.pivot_table(
        index=["PATNO", "EVENT_ID"],
        columns="MEASURE_NAME",
        values="MEASURE_VALUE",
        aggfunc="mean",
    ).reset_index()

    #print("\n" + "=" * 50)
    #print("📋 MASTER_WIDE DIAGNOSTICS")
    #print(f"Shape: {master_wide.shape[0]} rows x {master_wide.shape[1]} columns")
    #print("-" * 30)
    #print("💡 DataFrame Head:")
    #print(master_wide.head())
    #print("=" * 50 + "\n")

    available_signals = [f for f in TARGET_FEATURES if f in master_wide.columns]
    #print(f"⏳ Processing {len(available_signals)} signals per patient...")

    patient_features = []
    unique_patients = master_wide["PATNO"].unique()

    for patno in unique_patients:
        patient_data = master_wide[master_wide["PATNO"] == patno]
        row = {"PATNO": patno}

        for sig in available_signals:
            row[f"BASE_{sig}_mean"] = patient_data[sig].mean()

            metrics = calculate_dpvi_batch(patient_data[sig])
            row[f"DPVI_{sig}_std"] = metrics[0]
            row[f"DPVI_{sig}_prog_rate"] = metrics[1]
            row[f"DPVI_{sig}_spikes"] = metrics[2]
            row[f"DPVI_{sig}_reversals"] = metrics[3]
            row[f"DPVI_{sig}_entropy"] = metrics[4]

        patient_features.append(row)

    final_patient_matrix = pd.DataFrame(patient_features).fillna(0)
    return final_patient_matrix


def optimize_dpvi_features(df, weights=DPVI_WEIGHTS):
    #print("⚖️ Applying Weighted Feature Fusion to DPVI components...")

    baseline_cols = [c for c in df.columns if c.startswith("BASE_")]
    core_features = [c.replace("BASE_", "").replace("_mean", "") for c in baseline_cols]

    optimized_data = df[["PATNO", "FINAL_STATUS"]].copy()

    # w1: Entropy, w2: Reversals, w3: Spikes, w4: Prog_Rate, w5: Std
    w1, w2, w3, w4, w5 = weights

    for feat in core_features:
        optimized_data[f"BASE_{feat}"] = df[f"BASE_{feat}_mean"]

        v1 = df[f"DPVI_{feat}_entropy"]
        v2 = df[f"DPVI_{feat}_reversals"]
        v3 = df[f"DPVI_{feat}_spikes"]
        v4 = df[f"DPVI_{feat}_prog_rate"]
        v5 = df[f"DPVI_{feat}_std"]

        optimized_data[f"DPVI_{feat}"] = (w1 * v1) + (w2 * v2) + (w3 * v3) + (w4 * v4) + (w5 * v5)

    base_final = [f"BASE_{f}" for f in core_features]
    dpvi_final = [f"DPVI_{f}" for f in core_features]
    final_cols = ["PATNO"] + base_final + dpvi_final + ["FINAL_STATUS"]
    optimized_data = optimized_data[final_cols]

    #print(f"✅ Success! Generated {len(core_features)} Baseline + {len(core_features)} DPVI features.")
    #print(f"Total Columns: {len(optimized_data.columns)}")

    return optimized_data
