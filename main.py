import uvicorn
from fastapi import FastAPI
from source.modules.user.router import router as user_router

app = FastAPI(
    title="Clinical Trial Matchmaker API",
    description="AI-powered API to match patients with suitable clinical trials.",
    version="1.0"
)

# Include the user/signup/login routes
app.include_router(user_router, prefix="/users", tags=["Users"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
