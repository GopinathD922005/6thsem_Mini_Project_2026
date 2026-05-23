from fastapi import APIRouter, UploadFile, File

from app.services.zip_service import process_uploaded_zip


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


# =========================================================
# UPLOAD DATASET ZIP
# =========================================================

@router.post("/")
async def upload_dataset(
    file: UploadFile = File(...)
):

    result = process_uploaded_zip(file)

    return result