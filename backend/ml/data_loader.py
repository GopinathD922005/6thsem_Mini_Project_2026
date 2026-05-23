import os
import pandas as pd
from ml.config import PATHS


def ensure_project_folders():
    for path in PATHS.values():
        path.mkdir(parents=True, exist_ok=True)


def load_all_csv(folder):
    data = {}
    folder = str(folder)

    if not os.path.exists(folder):
        #print(f"⚠️ Folder not found: {folder}")
        return data

    for file in os.listdir(folder):
        if file.endswith(".csv"):
            file_path = os.path.join(folder, file)
            try:
                df = pd.read_csv(file_path, low_memory=False)
                data[file] = df
                #print(f"Loaded: {file} | Shape: {df.shape}")
            except Exception as e:
                #print(f"Error loading {file}: {e}")
                pass
    return data


def load_all_datasets():
    ensure_project_folders()

    motor_data = load_all_csv(PATHS["motor"])
    non_motor_data = load_all_csv(PATHS["non_motor"])
    digital_sensor_data = load_all_csv(PATHS["digital_sensor"])
    biospecimen_data = load_all_csv(PATHS["biospecimen"])
    medical_history_data = load_all_csv(PATHS["medical_history"])

    return motor_data, non_motor_data, digital_sensor_data, biospecimen_data, medical_history_data
