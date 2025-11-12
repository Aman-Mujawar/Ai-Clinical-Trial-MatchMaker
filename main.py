import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# Routers
from source.modules.user.router import router as user_router
from source.modules.PatientProfile.router import router as patient_router
from source.modules.symptoms.router import router as symptom_router
from source.modules.matching.router import router as matching_router  # Phase 2: Trial Matching
from source.modules.chatbot.router import router as chatbot_router      # Chatbot endpoints

app = FastAPI(
    title="Clinical Trial Matchmaker API",
    description="AI-powered API to match patients with suitable clinical trials.",
    version="1.0.0"
)

# ---------- Include all routers ----------
app.include_router(user_router)
app.include_router(patient_router)
app.include_router(symptom_router)
app.include_router(matching_router)   # Trial matching endpoints
app.include_router(chatbot_router)    # Chatbot endpoints

# ---------- Custom OpenAPI for JWT Bearer Auth ----------
def custom_openapi():
    """
    Adds JWT Bearer auth scheme to OpenAPI for Swagger UI.
    Enables 'Authorize' button for protected endpoints.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add Bearer token security scheme
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})
    openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Enter your JWT token (without the 'Bearer ' prefix)"
    }

    # Apply BearerAuth as global security requirement for all endpoints
    openapi_schema.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ---------- Run the server ----------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
