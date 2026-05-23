from pathlib import Path


# =========================================================
# ROOT DIRECTORY
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]


# =========================================================
# DATA DIRECTORY
# =========================================================

DATA_DIR = BASE_DIR / "data"


# =========================================================
# DATASET FOLDERS
# =========================================================

MOTOR_DIR = DATA_DIR / "motor"

NON_MOTOR_DIR = DATA_DIR / "non_motor"

DIGITAL_SENSOR_DIR = DATA_DIR / "digital_sensor"

BIOSPECIMEN_DIR = DATA_DIR / "biospecimen"

MEDICAL_HISTORY_DIR = DATA_DIR / "medical_history"


# =========================================================
# OUTPUT DIRECTORY
# =========================================================

OUTPUT_DIR = DATA_DIR / "outputs"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# MODEL OUTPUT FILES
# =========================================================

FULL_DPVI_RESULTS = OUTPUT_DIR / "full_dpvi_results.csv"

WEIGHTED_DPVI_RESULTS = OUTPUT_DIR / "weighted_dpvi_results.csv"

FEATURE_IMPORTANCE_RESULTS = OUTPUT_DIR / "feature_importance.csv"

CV_RESULTS = OUTPUT_DIR / "cross_validation_results.csv"


# =========================================================
# APP CONFIG
# =========================================================

APP_NAME = "DPVI Parkinson's Disease System"

APP_VERSION = "1.0.0"

DEBUG = True


# =========================================================
# PATHS DICTIONARY FOR DATA_LOADER
# =========================================================

PATHS = {
    "motor": MOTOR_DIR,
    "non_motor": NON_MOTOR_DIR,
    "digital_sensor": DIGITAL_SENSOR_DIR,
    "biospecimen": BIOSPECIMEN_DIR,
    "medical_history": MEDICAL_HISTORY_DIR,
}


# =========================================================
# TARGET FEATURES FROM FULL_CODE.PDF
# 31 biological / clinical / gait signals used for DPVI
# =========================================================

TARGET_FEATURES = [
    "NP3TOT",
    "NP3BRADY",
    "NP3GAIT",
    "NP3PSTBL",
    "NP3FRZGT",
    "NP3RIGN",

    "NP2WALK",
    "NP2PTOT",

    "MCATOT",

    "CVStrideTime",
    "CVStepTime",
    "CVSteplength",

    "SampEntropyV",
    "SampEntropyML",
    "SampEntropyAP",

    "stepAsymV",
    "stepAsymML",
    "stepAsymAP",

    "rmsV",
    "rmsML",
    "rmsAP",

    "StepVelocitycmsec",
    "StepCount",

    "STR_CV_U",
    "STEP_REG_U",
    "STEP_SYM_U",
    "JERK_T_U",

    "NP1COG",
    "NP1DPRS",
    "NP1ANXS",
    "NP1APAT",
]


# =========================================================
# WEIGHTED DPVI FUSION WEIGHTS FROM FULL_CODE.PDF
#
# Order:
# w1 = entropy
# w2 = reversals
# w3 = spikes
# w4 = progression rate
# w5 = standard deviation
# =========================================================

DPVI_WEIGHTS = [
    0.45,
    0.25,
    0.15,
    0.10,
    0.05
]


# =========================================================
# DPVI COMPONENT NAMES
# =========================================================

DPVI_COMPONENTS = [
    "entropy",
    "reversals",
    "spikes",
    "prog_rate",
    "std",
]


# =========================================================
# LABEL FILES USED FOR FINAL_STATUS CREATION
# Keys are lowercase because label_builder.py expects them
# =========================================================

LABEL_FILES = {
    "diagnosis": MEDICAL_HISTORY_DIR / "Primary_Research_Diagnosis_07Apr2026.csv",

    "questionnaire": MOTOR_DIR / "Participant_Motor_Function_Questionnaire_02Apr2026.csv",

    "updrs_iii": MOTOR_DIR / "MDS-UPDRS_Part_III_02Apr2026.csv",
}