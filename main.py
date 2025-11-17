import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import os

# Routers
from source.modules.user.router import router as user_router
from source.modules.PatientProfile.router import router as patient_router
from source.modules.symptoms.router import router as symptom_router
from source.modules.matching.router import router as matching_router
from source.modules.chatbot.router import router as chatbot_router
from source.modules.getprofile.router import router as getprofile_router   # ✅ NEW IMPORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("clinical-trial-backend")

app = FastAPI(
    title="Clinical Trial Matchmaker API",
    description="AI-powered API to match patients with suitable clinical trials.",
    version="1.0.0"
)

# Add CORS for frontend (adjust origins in production)
origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router)
app.include_router(patient_router)
app.include_router(symptom_router)
app.include_router(matching_router)
app.include_router(chatbot_router)
app.include_router(getprofile_router)  # ✅ Added getprofile router

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})
    openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Enter your JWT token (without the 'Bearer ' prefix')"
    }
    openapi_schema.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.on_event("startup")
def on_startup():
    logger.info("Starting Clinical Trial Matchmaker API")
    logger.info(f"ENV DATABASE_URL set: {'DATABASE_URL' in os.environ}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True
    )
