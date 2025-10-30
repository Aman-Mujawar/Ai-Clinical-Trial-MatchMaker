import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.gzip import GZipMiddleware

from api.handlers import register_exception_handlers
from api.router import api_router
from common import aws_checks
from logger import service as logger_service
from modules.compliance import handlers as compliance_handlers
from modules.questionnaire import handlers as questionnaire_handlers
from modules.email import service as email_service
from modules.event_manager import jobs as event_manager_jobs
from modules.field import handlers as field_handlers
from modules.session import jobs as session_jobs
from rate_limiter import limiter
from version import VersionInfo

log = logger_service.get_logger(__name__)

version_info = VersionInfo()

log.info(f"Starting {version_info}")


# we create the lifespan object
async def lifespan(app: FastAPI):
    scheduler_service.start_scheduler()
    yield
    scheduler_service.stop_scheduler()


# we create the Web API framework
app = FastAPI(
    title="Clinical Match Maker",
    description="Clinical Match Maker documentation!",
    version=version_info.get_full_version(),
    lifespan=lifespan,
    # root_path="/",
    # docs_url=None,
    # openapi_url="/docs/openapi.json",
    # redoc_url="/docs",
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


# remove 422 response from openapi
def custom_openapi():
    if not app.openapi_schema:
        app.openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            terms_of_service=app.terms_of_service,
            contact=app.contact,
            license_info=app.license_info,
            routes=app.routes,
            tags=app.openapi_tags,
            servers=app.servers,
        )
        for _, method_item in app.openapi_schema.get("paths").items():
            for _, param in method_item.items():
                responses = param.get("responses")
                # remove 422 response, also can remove other status code
                if "422" in responses:
                    del responses["422"]
    return app.openapi_schema


app.openapi = custom_openapi

# exception handlers
register_exception_handlers(app)

# rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# gzip middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# we add all API routes to the Web API framework
app.include_router(api_router)

# run any module inits
email_service.init()

# schedule any jobs
event_manager_jobs.init()
session_jobs.init()

# register event handlers
compliance_handlers.init()
field_handlers.init()
questionnaire_handlers.init()

# run any checks
aws_checks.run()

# we run the Web API framework
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
