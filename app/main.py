from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import uuid
from contextlib import asynccontextmanager
from app.config.settings import settings
from app.config.database import init_db
# from app.api.routes import upload, jobs, download, outpaint
from app.api.routes import upload, jobs, download

from app.services.redis_service import RedisService
from app.utils.exceptions import AppException
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Creative Resizer Backend...")
    await init_db()
    
    # Initialize Redis connection
    redis_service = RedisService()
    await redis_service.connect()
    app.state.redis = redis_service

    # Preload HuggingFace pipeline in background
    try:
        from app.api.routes.outpaint import load_pipeline
        asyncio.create_task(load_pipeline())
        logger.info("📦 Outpaint preload task scheduled ✅ (loading in background)")
    except Exception as e:
        logger.error(f"❌ Failed to schedule Outpaint preload: {e}")

    logger.info("✅ Application startup complete")
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    if hasattr(app.state, 'redis'):
        await app.state.redis.disconnect()
    logger.info("👋 Application shutdown complete")


# Create FastAPI instance
app = FastAPI(
    title="Creative Content Resizer API",
    description="Enterprise-grade creative content resizing service for social media platforms",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
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
    
    # Add request ID to logs
    logger.info(f"➡️ Request {request_id}: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
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


# Health check endpoint
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    }


# Include routers
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(jobs.router, prefix="/api/v1", tags=["Jobs"])
app.include_router(download.router, prefix="/api/v1", tags=["Download"])
# app.include_router(outpaint.router, prefix="/api/v1", tags=["Outpaint"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
