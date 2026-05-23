from datetime import datetime


# =========================================================
# GLOBAL PROGRESS STORAGE
# =========================================================

PROGRESS_LOGS = []


# =========================================================
# ADD PROGRESS MESSAGE
# =========================================================

def add_progress(message):

    global PROGRESS_LOGS

    timestamp = datetime.now().strftime("%H:%M:%S")

    log = {

        "time": timestamp,

        "message": message
    }

    print(f"[{timestamp}] {message}")

    PROGRESS_LOGS.append(log)


# =========================================================
# GET ALL PROGRESS
# =========================================================

def get_progress():

    global PROGRESS_LOGS

    return PROGRESS_LOGS


# =========================================================
# CLEAR PROGRESS
# =========================================================

def clear_progress():

    global PROGRESS_LOGS

    PROGRESS_LOGS = []


# =========================================================
# LAST MESSAGE
# =========================================================

def get_latest_progress():

    global PROGRESS_LOGS

    if len(PROGRESS_LOGS) == 0:

        return None

    return PROGRESS_LOGS[-1]