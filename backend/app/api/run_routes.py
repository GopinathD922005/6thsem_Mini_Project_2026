import threading
import time

from fastapi import APIRouter

from ml.pipeline_runner import (
    run_full_pipeline,
    get_latest_results,
    has_cached_results
)

from app.services.progress_store import (
    clear_progress,
    add_progress,
)


router = APIRouter(
    prefix="/run",
    tags=["Run Pipeline"]
)


# =========================================================
# GLOBAL FLAGS
# =========================================================

PIPELINE_RUNNING = False


# =========================================================
# CACHED PIPELINE THREAD
# =========================================================
def cached_pipeline_thread():

    global PIPELINE_RUNNING

    try:
        results = get_latest_results(
            progress_callback=add_progress,
            replay=True
        )

        if not results:
            add_progress("❌ Pipeline Failed: Cache results could not be loaded")

    except Exception as e:
        add_progress(f"❌ Pipeline Failed: {str(e)}")

    finally:
        PIPELINE_RUNNING = False

        
# =========================================================
# THREAD FUNCTION
# =========================================================

def pipeline_thread():

    global PIPELINE_RUNNING

    try:
        add_progress("🚀 Pipeline Execution Started")

        run_full_pipeline(
            progress_callback=add_progress
        )

        add_progress("🎉 Entire Pipeline Completed")

    except Exception as e:
        add_progress(f"❌ Pipeline Failed: {str(e)}")

    finally:
        PIPELINE_RUNNING = False


# =========================================================
# START PIPELINE
# =========================================================

@router.post("/start")
def start_pipeline():

    global PIPELINE_RUNNING

    if PIPELINE_RUNNING:
        return {
            "success": False,
            "message": "Pipeline already running"
        }

    clear_progress()

    PIPELINE_RUNNING = True

    if has_cached_results():
        thread = threading.Thread(
            target=cached_pipeline_thread
        )

        thread.start()

        return {
            "success": True,
            "message": "Pipeline started successfully"
        }

    thread = threading.Thread(
        target=pipeline_thread
    )

    thread.start()

    return {
        "success": True,
        "message": "Pipeline started successfully"
    }


# =========================================================
# PIPELINE STATUS
# =========================================================

@router.get("/status")
def get_pipeline_status():

    global PIPELINE_RUNNING

    return {
        "running": PIPELINE_RUNNING
    }