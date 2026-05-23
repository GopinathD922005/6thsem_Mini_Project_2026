import os
import shutil
import zipfile

from app.services.progress_store import add_progress


# =========================================================
# ROOT PATHS
# =========================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../.."
    )
)

DATA_DIR = os.path.join(BASE_DIR, "data")

TEMP_DIR = os.path.join(BASE_DIR, "temp_upload")


# =========================================================
# EXPECTED DATA FOLDERS
# =========================================================

EXPECTED_FOLDERS = [
    "motor",
    "non_motor",
    "digital_sensor",
    "biospecimen",
    "medical_history",
]


# =========================================================
# CREATE TEMP DIRECTORY
# =========================================================

os.makedirs(TEMP_DIR, exist_ok=True)


# =========================================================
# DELETE EXISTING DATA FOLDER
# =========================================================

def delete_existing_data():

    try:

        if os.path.exists(DATA_DIR):

            shutil.rmtree(DATA_DIR)

            add_progress("🗑 Existing data folder deleted")

        os.makedirs(DATA_DIR, exist_ok=True)

        add_progress("📂 Fresh data folder created")

    except Exception as e:

        add_progress(f"❌ Failed deleting data folder: {str(e)}")

        raise


# =========================================================
# FIX NESTED DATA/DATA STRUCTURE
# =========================================================

def fix_nested_data_folder():

    nested_data_dir = os.path.join(DATA_DIR, "data")

    if not os.path.exists(nested_data_dir):

        add_progress("✅ Data folder structure is already correct")

        return

    add_progress("⚠️ Nested data/data folder detected. Fixing structure...")

    for folder_name in EXPECTED_FOLDERS:

        source = os.path.join(nested_data_dir, folder_name)

        destination = os.path.join(DATA_DIR, folder_name)

        if os.path.exists(source):

            if os.path.exists(destination):

                shutil.rmtree(destination)

            shutil.move(source, destination)

            add_progress(f"✅ Moved {folder_name} to data/{folder_name}")

    shutil.rmtree(nested_data_dir)

    add_progress("✅ Nested data folder removed")


# =========================================================
# VALIDATE FINAL DATA STRUCTURE
# =========================================================

def validate_data_structure():

    missing = []

    for folder_name in EXPECTED_FOLDERS:

        folder_path = os.path.join(DATA_DIR, folder_name)

        if not os.path.exists(folder_path):

            missing.append(folder_name)

    if missing:

        raise Exception(
            "Missing required folders after extraction: "
            + ", ".join(missing)
        )

    add_progress("✅ Final data folder structure validated")


# =========================================================
# EXTRACT ZIP FILE
# =========================================================

def extract_uploaded_zip(zip_path):

    try:

        add_progress("📦 Extracting uploaded ZIP...")

        with zipfile.ZipFile(zip_path, "r") as zip_ref:

            zip_ref.extractall(DATA_DIR)

        add_progress("✅ ZIP extraction completed")

        fix_nested_data_folder()

        validate_data_structure()

    except Exception as e:

        add_progress(f"❌ ZIP extraction failed: {str(e)}")

        raise


# =========================================================
# SAVE ZIP FILE
# =========================================================

def save_uploaded_file(upload_file):

    try:

        file_path = os.path.join(
            TEMP_DIR,
            upload_file.filename
        )

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(
                upload_file.file,
                buffer
            )

        add_progress("✅ Uploaded ZIP saved temporarily")

        return file_path

    except Exception as e:

        add_progress(f"❌ Failed saving ZIP: {str(e)}")

        raise


# =========================================================
# REMOVE TEMP FILE
# =========================================================

def remove_temp_zip(zip_path):

    try:

        if os.path.exists(zip_path):

            os.remove(zip_path)

            add_progress("🧹 Temporary ZIP removed")

    except Exception as e:

        add_progress(f"❌ Failed removing temp ZIP: {str(e)}")


# =========================================================
# COMPLETE ZIP PROCESS
# =========================================================

def process_uploaded_zip(upload_file):

    try:

        add_progress("🚀 Starting ZIP processing...")

        if not upload_file.filename.endswith(".zip"):

            return {
                "success": False,
                "message": "Only ZIP files are allowed"
            }

        add_progress("✅ ZIP validation successful")

        zip_path = save_uploaded_file(upload_file)

        delete_existing_data()

        extract_uploaded_zip(zip_path)

        remove_temp_zip(zip_path)

        add_progress("🎉 ZIP processing completed successfully")

        return {
            "success": True,
            "message": "Dataset uploaded successfully"
        }

    except Exception as e:

        add_progress(f"❌ ZIP processing failed: {str(e)}")

        return {
            "success": False,
            "message": str(e)
        }