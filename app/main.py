"""
Main FastAPI application for Media Buying Management System.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog
import time

from app.core.config import settings
from app.core.database import Database
from app.api.v1 import auth, clients, skus, campaigns, metrics, intelligence, creatives, creative_tests

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("application_startup", version=settings.APP_VERSION)
    await Database.connect_db()
    
    # Create database indexes
    try:
        from app.db.create_indexes import create_indexes
        await create_indexes()
        logger.info("database_indexes_created")
    except Exception as e:
        logger.error("database_indexes_creation_failed", error=str(e))
    
    # Start automated scheduler if enabled
    if settings.HOURLY_OPTIMIZATION_ENABLED:
        from app.tasks.scheduler import get_scheduler
        scheduler = get_scheduler()
        scheduler.start()
        logger.info("automated_scheduler_started")
    
    yield
    
    # Shutdown
    logger.info("application_shutdown")
    
    # Stop scheduler
    if settings.HOURLY_OPTIMIZATION_ENABLED:
        from app.tasks.scheduler import get_scheduler
        scheduler = get_scheduler()
        scheduler.stop()
        logger.info("automated_scheduler_stopped")
    
    await Database.close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent API-only media buying management system with multi-tenant support",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting middleware
if settings.RATE_LIMIT_ENABLED:
    from fastapi import HTTPException
    from app.core.rate_limit import get_rate_limiter
    
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        """Apply rate limiting to all requests."""
        # Skip rate limiting for health check and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        try:
            rate_limiter = get_rate_limiter()
            await rate_limiter.check_rate_limit(request)
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
                headers=e.headers or {}
            )
        
        response = await call_next(request)
        
        # Add rate limit headers if available
        if hasattr(request.state, "rate_limit_remaining"):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)
            response.headers["X-RateLimit-Reset"] = str(request.state.rate_limit_reset)
        
        return response
    
    logger.info("rate_limiting_enabled", limit=settings.RATE_LIMIT_PER_MINUTE)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to ms
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    
    # Log slow requests
    if process_time > settings.API_RESPONSE_TIME_MAX_MS:
        logger.warning(
            "slow_request",
            path=request.url.path,
            method=request.method,
            process_time_ms=process_time
        )
    
    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Include API routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"]
)

app.include_router(
    clients.router,
    prefix=f"{settings.API_V1_PREFIX}/clients",
    tags=["Clients"]
)

app.include_router(
    skus.router,
    prefix=f"{settings.API_V1_PREFIX}/skus",
    tags=["SKUs"]
)

app.include_router(
    campaigns.router,
    prefix=f"{settings.API_V1_PREFIX}/campaigns",
    tags=["Campaigns"]
)

app.include_router(
    metrics.router,
    prefix=f"{settings.API_V1_PREFIX}/metrics",
    tags=["Metrics"]
)

app.include_router(
    intelligence.router,
    prefix=f"{settings.API_V1_PREFIX}/intelligence",
    tags=["Intelligence"]
)

app.include_router(
    creatives.router,
    prefix=f"{settings.API_V1_PREFIX}/creatives",
    tags=["Creatives"]
)

app.include_router(
    creative_tests.router,
    prefix=f"{settings.API_V1_PREFIX}/creative-tests",
    tags=["Creative Testing"]
)

# Import and include admin router
from app.api.v1 import admin

app.include_router(
    admin.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
