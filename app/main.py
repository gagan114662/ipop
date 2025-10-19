import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging

from app.database import database
from app.config import settings
# from app.routes import job, upload, download
# from app.routes.upload import router as upload_router
# from app.routes.jobs import router as jobs_router
# from app.routes.download import router as download_router

from app.routes import jobs, uplaod, download
import asyncio
from app.worker.resize_worker import start_worker, stop_worker
from app.utils.exceptions import AppException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)





# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """
#     Lifespan context manager to handle startup and shutdown events.
#     Starts the Redis background worker on startup and stops it on shutdown.
#     """
#     # Startup
#     logger.info("🚀 Starting up the application...")
#     await start_worker()
#     yield
#     # Shutdown
#     logger.info("🛑 Shutting down the application...")
#     await stop_worker()


# Create FastAPI instance
app = FastAPI(
    title="Creative Content Resizer API",
    description="Enterprise-grade creative content resizing service for social media platforms",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    # lifespan=lifespan,
)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting worker in background...")
    asyncio.create_task(start_worker())  # runs worker without blocking

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Stopping background worker...")
    await stop_worker()



origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite
    "http://127.0.0.1:5173",
    "*"  # ← use this only for testing
]


# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """Add request ID and timing"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.time()
    logger.info(f"➡️ Request {request_id}: {request.method} {request.url}")

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    response.headers["X-Request-ID"] = request_id

    logger.info(f"✅ Request {request_id} completed in {process_time:.3f}s")
    return response


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application-specific exceptions"""
    logger.error(f"Application error: {exc.message}", exc_info=exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Unexpected error in request {request_id}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "request_id": request_id
        }
    )


# # Test DB endpoint
# @app.get("/test-db")
# async def test_db():
#     try:
#         await database.command("ping")
#         return {"status": "MongoDB connected!"}
#     except Exception as e:
#         return {"error": str(e)}


# # Health check endpoint
# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy",
#         "version": "1.0.0",
#         "timestamp": time.time()
#     }


@app.get("/")
def root():
    return {"message": "Welcome to Resize Backend!"}


# Include routers
# app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
# app.include_router(job.router, prefix="/api/v1", tags=["Jobs"])
# app.include_router(download.router, prefix="/api/v1", tags=["Download"])

# app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])
# app.include_router(jobs_router, prefix="/api/v1", tags=["Jobs"])
# app.include_router(download_router, prefix="/api/v1", tags=["Download"])

app.include_router(uplaod.router, prefix="/api/v1", tags=["Upload"])
app.include_router(jobs.router, prefix="/api/v1", tags=["Jobs"])
app.include_router(download.router, prefix="/api/v1", tags=["Download"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )