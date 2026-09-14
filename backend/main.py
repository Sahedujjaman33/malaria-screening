"""
Malaria Screening System - Backend Entry Point
Member 3: Web Application & Deployment

Run locally with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Docs auto-generated at:
    http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import prediction
from services.classification import _load_model

app = FastAPI(
    title="Malaria Screening System API",
    description="AI-assisted screening tool for detecting parasitized RBCs "
                "in thin blood smear images. Research prototype - not a "
                "substitute for professional medical diagnosis.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/results", StaticFiles(directory="results"), name="results")

app.include_router(prediction.router)


@app.on_event("startup")
async def startup_event():
    """
    Server আগে port-এ bind হয়ে health check pass করে ফেলবে,
    তারপর background-এ model download/load শুরু হবে।
    এটাই Cloud Run-এর "container failed to start" সমস্যার সমাধান।
    """
    _load_model()


@app.get("/")
def health_check():
    """Simple health check endpoint - useful to verify deployment is alive."""
    return {
        "status": "ok",
        "service": "malaria-screening-backend",
        "message": "Server is running. See /docs for API documentation."
    }