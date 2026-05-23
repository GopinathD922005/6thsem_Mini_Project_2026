import os
import warnings
from contextlib import redirect_stdout, redirect_stderr
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from xgboost import XGBClassifier


warnings.filterwarnings("ignore")


def _run_single_grid_search(task):
    model_name, X_train, X_test, y_train, y_test = task

    if model_name == "Random Forest":
        model = RandomForestClassifier(random_state=42)

        params = {
        "n_estimators": [50, 100, 150]
    }

    elif model_name == "Gradient Boosting":
        model = GradientBoostingClassifier(random_state=42)

        params = {
        "n_estimators": [90, 100, 110]
    }

    elif model_name == "XGBoost":
        model = XGBClassifier(
            random_state=42,
            eval_metric="logloss",
        )

        params = {
        "n_estimators": [100, 110, 120],
        "learning_rate": [ 0.1]
    }
    else:
        raise ValueError(f"Unsupported model: {model_name}")

    grid = GridSearchCV(
        estimator=model,
        param_grid=params,
        cv=5,
        scoring="accuracy",
        n_jobs=1,        # important: avoid nested multiprocessing lag
        verbose=0
    )

    with open(os.devnull, "w") as devnull:
        with redirect_stdout(devnull), redirect_stderr(devnull):
            grid.fit(X_train, y_train)

    best_model = grid.best_estimator_
    y_pred = best_model.predict(X_test)

    return {
        "Model": model_name,
        "Best_Params": grid.best_params_,
        "Best_CV_Score": round(float(grid.best_score_), 4),
        "Test_Accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
    }


def run_parallel_grid_search_cv(train_ready_df, max_workers=3):
    df = train_ready_df.copy()

    dpvi_features = [
        c for c in df.columns
        if c.startswith("BASE_") or c.startswith("DPVI_")
    ]

    target_col = "FINAL_STATUS"

    X = df[dpvi_features]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    tasks = [
        ("Random Forest", X_train, X_test, y_train, y_test),
        ("Gradient Boosting", X_train, X_test, y_train, y_test),
        ("XGBoost", X_train, X_test, y_train, y_test),
    ]

    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_run_single_grid_search, task)
            for task in tasks
        ]

        for future in as_completed(futures):
            results.append(future.result())

    return sorted(
        results,
        key=lambda row: row["Test_Accuracy"],
        reverse=True
    )