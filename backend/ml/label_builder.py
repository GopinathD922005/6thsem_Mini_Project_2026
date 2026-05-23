import pandas as pd
from ml.config import PATHS, LABEL_FILES


def _find_file(filename):
    for key in ["medical_history", "motor", "non_motor", "digital_sensor", "biospecimen"]:
        candidate = PATHS[key] / filename
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Could not find {filename}. Put it in the correct data subfolder. "
        f"Expected one of: data/medical_history or data/motor."
    )


def preview_label_sources():
    paths = {
        "Diagnosis": _find_file(LABEL_FILES["diagnosis"]),
        "Questionnaire": _find_file(LABEL_FILES["questionnaire"]),
        "UPDRS_III": _find_file(LABEL_FILES["updrs_iii"]),
    }

    df1 = pd.read_csv(paths["Diagnosis"], low_memory=False)
    #print("\n--- Primary Diagnosis ---")
    #print(df1[["PATNO", "EVENT_ID", "PRIMDIAG"]].head())

    df2 = pd.read_csv(paths["Questionnaire"], low_memory=False)
    #print("\n--- Told PD Status ---")
    #print(df2[["PATNO", "EVENT_ID", "TOLDPD"]].head())

    df3 = pd.read_csv(paths["UPDRS_III"], low_memory=False)
    #print("\n--- Hoehn & Yahr Stage ---")
    #print(df3[["PATNO", "EVENT_ID", "NHY"]].head())


def generate_status_matrix():
    #print("🔄 Extracting diagnostic features from clinical records...")

    path_diag = _find_file(LABEL_FILES["diagnosis"])
    path_quest = _find_file(LABEL_FILES["questionnaire"])
    path_updrs = _find_file(LABEL_FILES["updrs_iii"])

    df_diag = pd.read_csv(path_diag, low_memory=False)[["PATNO", "EVENT_ID", "PRIMDIAG"]]
    df_diag.columns = ["patno", "eventno", "PRIMDIAG"]

    df_quest = pd.read_csv(path_quest, low_memory=False)[["PATNO", "EVENT_ID", "TOLDPD"]]
    df_quest.columns = ["patno", "eventno", "TOLDPD"]

    df_updrs = pd.read_csv(path_updrs, low_memory=False)[["PATNO", "EVENT_ID", "NHY"]]
    df_updrs.columns = ["patno", "eventno", "NHY"]

    status_df = pd.merge(df_diag, df_quest, on=["patno", "eventno"], how="outer")
    status_df = pd.merge(status_df, df_updrs, on=["patno", "eventno"], how="outer")

    status_df = status_df.sort_values(by=["patno", "eventno"]).reset_index(drop=True)
    status_df = status_df.fillna(0)

    return status_df


def generate_patient_labels(full_status_data):
    full_status_data = full_status_data.copy()

    full_status_data["is_pd_diag"] = (full_status_data["PRIMDIAG"] == 17).astype(int)
    full_status_data["is_pd_nhy"] = (pd.to_numeric(full_status_data["NHY"], errors="coerce") > 0).astype(int)
    full_status_data["is_pd_told"] = (pd.to_numeric(full_status_data["TOLDPD"], errors="coerce") == 1).astype(int)

    full_status_data["visit_status"] = full_status_data[["is_pd_diag", "is_pd_nhy", "is_pd_told"]].max(axis=1)

    patient_labels = full_status_data.groupby("patno")["visit_status"].max().reset_index()
    patient_labels.columns = ["PATNO", "FINAL_STATUS"]

    return patient_labels


def merge_features_with_labels(final_ml_data, patient_labels):
    final_ml_data = final_ml_data.copy()
    patient_labels = patient_labels.copy()

    final_ml_data["PATNO"] = final_ml_data["PATNO"].astype(str).str.strip()
    patient_labels["PATNO"] = patient_labels["PATNO"].astype(str).str.strip()

    train_ready_df = pd.merge(final_ml_data, patient_labels, on="PATNO", how="inner")
    return train_ready_df
