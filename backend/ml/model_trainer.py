import pandas as pd
import numpy as np

import io
import base64
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, KFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    mean_absolute_error,
    r2_score,
    mean_squared_error,
)

try:
    from xgboost import XGBClassifier
except ImportError as exc:
    raise ImportError(
        "xgboost is required. Install it using: pip install xgboost"
    ) from exc

def _architectures(best_params_map=None):
    if best_params_map is None:
        best_params_map = {}

    return {
        "Random Forest": RandomForestClassifier(
            **best_params_map["Random Forest"],
            random_state=42
        ),

        "XGBoost": XGBClassifier(
            **best_params_map["XGBoost"],
            random_state=42,
            eval_metric="logloss"
        ),

        "Gradient Boosting": GradientBoostingClassifier(
            **best_params_map["Gradient Boosting"],
            random_state=42
        ),
    }

def _epoch_model(model_name, epoch):
    if model_name == "Random Forest":
        return RandomForestClassifier(
            n_estimators=epoch,
            random_state=42
        )

    if model_name == "XGBoost":
        return XGBClassifier(
            n_estimators=epoch,
            learning_rate=0.1,
            random_state=42,
            eval_metric="logloss"
        )

    if model_name == "Gradient Boosting":
        return GradientBoostingClassifier(
            n_estimators=epoch,
            random_state=42
        )

    raise ValueError(f"Unsupported model: {model_name}")

def _safe_specificity(tn, fp):
    return tn / (tn + fp) if (tn + fp) > 0 else 0

def _extract_optimal_probability_threshold(y_true, y_prob):
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)

    valid_thresholds = thresholds[np.isfinite(thresholds)]

    if len(valid_thresholds) == 0:
        return 0.5

    youden_scores = tpr[:len(thresholds)] - fpr[:len(thresholds)]

    best_index = int(np.argmax(youden_scores))
    best_threshold = thresholds[best_index]

    if not np.isfinite(best_threshold):
        return 0.5

    return round(float(best_threshold), 4)

def _figure_to_base64(fig):
    buffer = io.BytesIO()

    fig.savefig(
        buffer,
        format="png",
        bbox_inches="tight",
        dpi=140
    )

    buffer.seek(0)

    image_base64 = base64.b64encode(
        buffer.read()
    ).decode("utf-8")

    plt.close(fig)

    return image_base64


def _extract_feature_importance(model, feature_names, top_n=10):

    if not hasattr(model, "feature_importances_"):
        return []

    importances = model.feature_importances_

    feature_rows = [
        {
            "feature": feature_names[i],
            "importance": round(float(importances[i]), 4)
        }
        for i in range(len(feature_names))
    ]

    feature_rows = sorted(
        feature_rows,
        key=lambda row: row["importance"],
        reverse=True
    )

    return feature_rows[:top_n]

def _extract_model_feature_thresholds(model, feature_names, top_features):
    threshold_map = {}

    top_features = [item.get("feature") for item in top_features]

    # Random Forest / Gradient Boosting sklearn trees
    if hasattr(model, "estimators_"):
        estimators = np.ravel(model.estimators_)

        for feature in top_features:
            if feature not in feature_names:
                continue

            feature_index = feature_names.index(feature)
            thresholds = []

            for estimator in estimators:
                tree = estimator.tree_

                node_mask = tree.feature == feature_index
                feature_thresholds = tree.threshold[node_mask]

                feature_thresholds = feature_thresholds[
                    feature_thresholds != -2
                ]

                thresholds.extend(feature_thresholds.tolist())

            threshold_map[feature] = (
                round(float(np.median(thresholds)), 4)
                if thresholds
                else None
            )

    # XGBoost trees
    elif hasattr(model, "get_booster"):
        booster_df = model.get_booster().trees_to_dataframe()

        for feature in top_features:
            feature_rows = booster_df[
                booster_df["Feature"] == feature
            ]

            splits = pd.to_numeric(
                feature_rows["Split"],
                errors="coerce"
            ).dropna()

            threshold_map[feature] = (
                round(float(splits.median()), 4)
                if not splits.empty
                else None
            )

    return threshold_map

def _average_feature_importance(
    fold_importances,
    feature_names,
    top_n=10
):

    if not fold_importances:
        return []

    avg_importance = np.mean(
        np.array(fold_importances),
        axis=0
    )

    feature_rows = [
        {
            "feature": feature_names[i],
            "importance": round(float(avg_importance[i]), 4)
        }
        for i in range(len(feature_names))
    ]

    feature_rows = sorted(
        feature_rows,
        key=lambda row: row["importance"],
        reverse=True
    )

    return feature_rows[:top_n]


def _create_train_test_graph(
    mode,
    name,
    y_test,
    y_prob,
    tn,
    fp,
    fn,
    tp,
    acc,
    auc_val,
    epoch_range,
    epoch_accuracies
):

    fig, (ax1, ax2, ax3) = plt.subplots(
        1,
        3,
        figsize=(20, 5)
    )

    sns.heatmap(
        [[tn, fp], [fn, tp]],
        annot=True,
        fmt="d",
        cmap="Blues" if "Baseline" in mode else "Purples",
        ax=ax1
    )

    ax1.set_title(f"CM: {mode} {name}")
    ax1.set_xlabel("Predicted")
    ax1.set_ylabel("Actual")

    fpr, tpr, _ = roc_curve(
        y_test,
        y_prob
    )

    ax2.plot(
        fpr,
        tpr,
        color="darkorange",
        lw=2,
        label=f"ROC curve (area = {auc_val:.2f})"
    )

    ax2.plot(
        [0, 1],
        [0, 1],
        color="navy",
        lw=2,
        linestyle="--"
    )

    ax2.set_xlim([0.0, 1.0])
    ax2.set_ylim([0.0, 1.05])
    ax2.set_xlabel("False Positive Rate")
    ax2.set_ylabel("True Positive Rate")
    ax2.set_title(f"ROC: {mode} {name}")
    ax2.legend(loc="lower right")

    ax3.plot(
        epoch_range,
        epoch_accuracies,
        linewidth=2
    )

    ax3.set_title(f"Accuracy vs Epochs: {mode} {name}")
    ax3.set_xlabel("Epochs / Number of Estimators")
    ax3.set_ylabel("Accuracy")
### ax3.set_ylim(0, 1)
    ax3.grid(True, linestyle="--", alpha=0.6)

    fig.text(
        0.5,
        0.02,
        f"MODEL ACCURACY: {acc:.2%}",
        ha="center",
        fontsize=12,
        fontweight="bold",
        bbox=dict(
            facecolor="white",
            edgecolor="gray",
            boxstyle="round,pad=0.5"
        )
    )

    plt.tight_layout(
        rect=[0, 0.05, 1, 1]
    )

    return _figure_to_base64(fig)

def _create_cv_graph(
    mode,
    name,
    df_len,
    agg_tn,
    agg_fp,
    agg_fn,
    agg_tp,
    mean_fpr,
    tprs,
    m_acc,
    m_auc,
    epoch_range,
    epoch_accuracy_mean
):

    fig, (ax1, ax2, ax3) = plt.subplots(
        1,
        3,
        figsize=(20, 5)
    )

    sns.heatmap(
        [[agg_tn, agg_fp], [agg_fn, agg_tp]],
        annot=True,
        fmt="d",
        cmap="Blues" if "Baseline" in mode else "Purples",
        ax=ax1
    )

    ax1.set_title(
        f"Aggregated CM: {mode} {name}\n(N={df_len})"
    )

    ax1.set_xlabel("Predicted")
    ax1.set_ylabel("Actual")

    tprs_arr = np.array(tprs)
    mean_tpr = tprs_arr.mean(axis=0)
    std_tpr = tprs_arr.std(axis=0)

    ax2.plot(
        mean_fpr,
        mean_tpr,
        color="darkorange",
        lw=2,
        label=f"Mean ROC (AUC={m_auc:.2f})"
    )

    ax2.fill_between(
        mean_fpr,
        mean_tpr - std_tpr,
        mean_tpr + std_tpr,
        color="gray",
        alpha=0.2,
        label="Std. Dev."
    )

    ax2.plot(
        [0, 1],
        [0, 1],
        color="navy",
        linestyle="--"
    )

    ax2.set_xlim([0.0, 1.0])
    ax2.set_ylim([0.0, 1.05])
    ax2.set_title(f"Mean ROC: {mode} {name}")
    ax2.legend(loc="lower right")

    ax3.plot(
        epoch_range,
        epoch_accuracy_mean,
        linewidth=2
    )

    ax3.set_title(f"Accuracy vs Epochs: {mode} {name}")
    ax3.set_xlabel("Epochs / Number of Estimators")
    ax3.set_ylabel("Mean CV Accuracy")
    ax3.set_ylim(0, 1)
    ax3.grid(True, linestyle="--", alpha=0.6)

    fig.text(
        0.5,
        0.02,
        f"3-FOLD MEAN CV ACCURACY: {m_acc:.2%}",
        ha="center",
        fontsize=12,
        fontweight="bold",
        bbox=dict(
            facecolor="white",
            edgecolor="gray",
            boxstyle="round,pad=0.5"
        )
    )

    plt.tight_layout(
        rect=[0, 0.05, 1, 1]
    )

    return _figure_to_base64(fig)

def _run_train_test(df, proposed_label, best_params_map=None):

    baseline_features = [
        c for c in df.columns
        if c.startswith("BASE_")
    ]

    dpvi_features = [
        c for c in df.columns
        if c.startswith("BASE_") or c.startswith("DPVI_")
    ]

    target_col = "FINAL_STATUS"

    X_train_b, X_test_b, y_train, y_test = train_test_split(
        df[baseline_features],
        df[target_col],
        test_size=0.2,
        random_state=42
    )

    X_train_p, X_test_p, _, _ = train_test_split(
        df[dpvi_features],
        df[target_col],
        test_size=0.2,
        random_state=42
    )

    results_data = []

    graph_data = []

    feature_importance_data = {}

    for name, model in _architectures(best_params_map).items():

        for mode, X_tr, X_te, feature_names in [

            (
                "Baseline",
                X_train_b,
                X_test_b,
                baseline_features
            ),

            (
                proposed_label,
                X_train_p,
                X_test_p,
                dpvi_features
            )
        ]:

            #print(f"🔄 Training {mode} {name}...")

            model.fit(
                X_tr,
                y_train
            )

            y_pred = model.predict(
                X_te
            )

            y_prob = model.predict_proba(
                X_te
            )[:, 1]

            probability_threshold = _extract_optimal_probability_threshold(
                y_test,
                y_prob
            )

            tn, fp, fn, tp = confusion_matrix(
                y_test,
                y_pred
            ).ravel()

            acc = accuracy_score(
                y_test,
                y_pred
            )

            f1 = f1_score(
                y_test,
                y_pred
            )

            auc_val = roc_auc_score(
                y_test,
                y_prob
            )

            epoch_range = list(range(1, 101))
            epoch_accuracies = []

            for epoch in epoch_range:
                epoch_model = _epoch_model(name, epoch)

                epoch_model.fit(
                    X_tr,
                    y_train
                )

                epoch_pred = epoch_model.predict(
                    X_te
                )

                epoch_acc = accuracy_score(
                    y_test,
                    epoch_pred
                )

                epoch_accuracies.append(epoch_acc)


            graph_image = _create_train_test_graph(
                mode,
                name,
                y_test,
                y_prob,
                tn,
                fp,
                fn,
                tp,
                acc,
                auc_val,
                epoch_range,
                epoch_accuracies
            )

            feature_importance_data.setdefault(
                mode,
                {}
            )

            top_importance = _extract_feature_importance(
                model,
                feature_names,
                top_n=10
            )

            model_thresholds = _extract_model_feature_thresholds(
                model,
                feature_names,
                top_importance[:5]
            )

            for item in top_importance:
                item["model_threshold"] = model_thresholds.get(
                    item.get("feature")
                )

            feature_importance_data[mode][name] = top_importance

            results_data.append({
                "Model": name,
                "Approach": mode,
                "Accuracy": acc,
                "F1_Score": f1,
                "ROC_AUC": auc_val,
                "R2_Score": r2_score(y_test, y_pred),
                "MAE": mean_absolute_error(y_test, y_pred),
                "RMSE": np.sqrt(mean_squared_error(y_test, y_pred)),
                "MSE": mean_squared_error(y_test, y_pred),
                "Precision": precision_score(y_test, y_pred),
                "Recall": recall_score(y_test, y_pred),
                "Specificity": _safe_specificity(tn, fp),
                "TP": int(tp),
                "TN": int(tn),
                "FP": int(fp),
                "FN": int(fn),
                "Probability_Threshold": probability_threshold
            })

            graph_data.append({
                "model": name,
                "approach": mode,
                "accuracy": float(acc),
                "accuracy_percent": f"{acc:.2%}",
                "roc_auc": float(auc_val),
                "roc_auc_percent": f"{auc_val:.2%}",
                "tp": int(tp),
                "tn": int(tn),
                "fp": int(fp),
                "fn": int(fn),
                "image": graph_image,
            })

    report_df = pd.DataFrame(
        results_data
    )

    return {
        "ledger": report_df.round(4).to_dict(orient="records"),
        "graphs": graph_data,
        "feature_importance": feature_importance_data
    }


def _run_cv(df, proposed_label, best_params_map=None):

    baseline_features = [
        c for c in df.columns
        if c.startswith("BASE_")
    ]

    dpvi_features = [
        c for c in df.columns
        if c.startswith("BASE_") or c.startswith("DPVI_")
    ]

    target_col = "FINAL_STATUS"

    kf = KFold(
        n_splits=3,
        shuffle=True,
        random_state=42
    )

    results_data = []

    graph_data = []

    feature_importance_data = {}

    patient_prediction_rows = []
    for name, model in _architectures(best_params_map).items():

        for mode, feature_set in [

            (
                "Baseline",
                baseline_features
            ),

            (
                proposed_label,
                dpvi_features
            )
        ]:

            #print(f"🔄 Cross-Validating {mode} {name}...")

            fold_metrics = {
                "acc": [],
                "f1": [],
                "auc": [],
                "r2": [],
                "mae": [],
                "mse": [],
                "prec": [],
                "rec": [],
                "spec": [],
                "threshold": []
            }

            agg_tn = 0
            agg_fp = 0
            agg_fn = 0
            agg_tp = 0

            mean_fpr = np.linspace(
                0,
                1,
                100
            )

            tprs = []

            fold_importances = []

            epoch_range = list(range(1, 101))
            epoch_accuracy_sum = np.zeros(len(epoch_range))

            for train_idx, test_idx in kf.split(df):

                X_train = df.iloc[train_idx][feature_set]

                X_test = df.iloc[test_idx][feature_set]

                y_train = df.iloc[train_idx][target_col]

                y_test = df.iloc[test_idx][target_col]

                model.fit(
                    X_train,
                    y_train
                )

                y_pred = model.predict(
                    X_test
                )

                y_prob = model.predict_proba(
                    X_test
                )[:, 1]

                fold_threshold = _extract_optimal_probability_threshold(
                    y_test,
                    y_prob
                )

                fold_metrics["threshold"].append(fold_threshold)


                test_patnos = df.iloc[test_idx]["PATNO"].astype(str).values

                for patno, actual, pred, prob in zip(
                    test_patnos,
                    y_test.values,
                    y_pred,
                    y_prob
                ):
                    patient_prediction_rows.append({
                        "PATNO": str(patno),
                        "Model": name,
                        "Approach": mode,
                        "FINAL_STATUS": int(actual),
                        "PREDICTED_STATUS": int(pred),
                        "PREDICTION_CONFIDENCE": float(prob),
                    })

                if hasattr(
                    model,
                    "feature_importances_"
                ):
                    fold_importances.append(
                        model.feature_importances_
                    )

                tn, fp, fn, tp = confusion_matrix(
                    y_test,
                    y_pred
                ).ravel()

                agg_tn += int(tn)
                agg_fp += int(fp)
                agg_fn += int(fn)
                agg_tp += int(tp)

                fold_metrics["acc"].append(
                    accuracy_score(y_test, y_pred)
                )

                fold_metrics["f1"].append(
                    f1_score(y_test, y_pred)
                )

                fold_metrics["auc"].append(
                    roc_auc_score(y_test, y_prob)
                )

                fold_metrics["r2"].append(
                    r2_score(y_test, y_pred)
                )

                fold_metrics["mae"].append(
                    mean_absolute_error(y_test, y_pred)
                )

                fold_metrics["mse"].append(
                    mean_squared_error(y_test, y_pred)
                )

                fold_metrics["prec"].append(
                    precision_score(y_test, y_pred)
                )

                fold_metrics["rec"].append(
                    recall_score(y_test, y_pred)
                )

                fold_metrics["spec"].append(
                    _safe_specificity(tn, fp)
                )

                fpr, tpr, _ = roc_curve(
                    y_test,
                    y_prob
                )

                interp_tpr = np.interp(
                    mean_fpr,
                    fpr,
                    tpr
                )

                interp_tpr[0] = 0.0

                tprs.append(
                    interp_tpr
                )

                for i, epoch in enumerate(epoch_range):
                    epoch_model = _epoch_model(name, epoch)

                    epoch_model.fit(
                        X_train,
                        y_train
                    )

                    epoch_pred = epoch_model.predict(
                        X_test
                    )

                    epoch_accuracy_sum[i] += accuracy_score(
                        y_test,
                        epoch_pred
                    )

            epoch_accuracy_mean = epoch_accuracy_sum / kf.get_n_splits()

            m_acc = np.mean(
                fold_metrics["acc"]
            )

            m_auc = np.mean(
                fold_metrics["auc"]
            )

            graph_image = _create_cv_graph(
                mode,
                name,
                len(df),
                agg_tn,
                agg_fp,
                agg_fn,
                agg_tp,
                mean_fpr,
                tprs,
                m_acc,
                m_auc,
                epoch_range,
                epoch_accuracy_mean
            )

            feature_importance_data.setdefault(
                mode,
                {}
            )

            top_importance = _average_feature_importance(
                fold_importances,
                feature_set,
                top_n=10
            )

            model_thresholds = _extract_model_feature_thresholds(
                model,
                feature_set,
                top_importance[:5]
            )

            for item in top_importance:
                item["model_threshold"] = model_thresholds.get(
                    item.get("feature")
                )

            feature_importance_data[mode][name] = top_importance

            results_data.append({
                "Model": name,
                "Approach": mode,
                "Accuracy": m_acc,
                "F1_Score": np.mean(fold_metrics["f1"]),
                "ROC_AUC": m_auc,
                "R2_Score": np.mean(fold_metrics["r2"]),
                "MAE": np.mean(fold_metrics["mae"]),
                "RMSE": np.sqrt(np.mean(fold_metrics["mse"])),
                "MSE": np.mean(fold_metrics["mse"]),
                "Precision": np.mean(fold_metrics["prec"]),
                "Recall": np.mean(fold_metrics["rec"]),
                "Specificity": np.mean(fold_metrics["spec"]),
                "TP": int(agg_tp),
                "TN": int(agg_tn),
                "FP": int(agg_fp),
                "FN": int(agg_fn),
                "Probability_Threshold": float(np.mean(fold_metrics["threshold"]))
            })

            graph_data.append({
                "model": name,
                "approach": mode,
                "accuracy": float(m_acc),
                "accuracy_percent": f"{m_acc:.2%}",
                "roc_auc": float(m_auc),
                "roc_auc_percent": f"{m_auc:.2%}",
                "tp": int(agg_tp),
                "tn": int(agg_tn),
                "fp": int(agg_fp),
                "fn": int(agg_fn),
                "image": graph_image,
            })

    report_df = pd.DataFrame(
        results_data
    )

    return {
        "ledger": report_df.round(4).to_dict(orient="records"),
        "graphs": graph_data,
        "feature_importance": feature_importance_data,
        "patient_predictions": patient_prediction_rows
    }


def run_parkinsons_elevation_study(df, best_params_map=None):
    return _run_train_test(df, "Proposed (DPVI)", best_params_map)


def run_parkinsons_cv_elevation_study(df, best_params_map=None):
    return _run_cv(df, "Proposed (DPVI)", best_params_map)

def run_parkinsons_weighted_elevation_study(df, best_params_map=None):
    return _run_train_test(df, "Proposed (Weighted DPVI)", best_params_map)


def run_parkinsons_weighted_cv_elevation_study(df, best_params_map=None):
    return _run_cv(df, "Proposed (Weighted DPVI)", best_params_map)