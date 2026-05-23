from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.upload_routes import router as upload_router
from app.api.run_routes import router as run_router
from app.api.results_routes import router as results_router

app = FastAPI(
    title="DPVI Parkinson's Disease System",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROUTES
# =========================================================

app.include_router(upload_router)

app.include_router(run_router)

app.include_router(results_router)

# =========================================================
# ROOT
# =========================================================

@app.get("/")
def home():

    return {

        "message": "DPVI Backend Running Successfully"

    }