"""
Core configuration for the Media Buying Management System.
"""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "IPOP Media Buying Management System"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Security & JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "ipop_media_buying"
    MONGODB_MAX_CONNECTIONS: int = 100
    MONGODB_MIN_CONNECTIONS: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 1000
    RATE_LIMIT_ENABLED: bool = True
    
    # Performance Thresholds
    API_RESPONSE_TIME_MAX_MS: int = 500
    INTELLIGENCE_DECISION_MAX_MS: int = 2000
    
    # Intelligence Settings
    IMPRESSION_THRESHOLD: int = 1000
    EXPLORE_BUDGET_PERCENTAGE: int = 20
    EXPLOIT_BUDGET_PERCENTAGE: int = 5
    MIN_CAMPAIGN_BUDGET_USD: float = 100.0
    EXPLORE_MODE_DAYS: int = 7
    
    # GCP
    GCP_PROJECT_ID: Optional[str] = None
    GCP_SECRET_MANAGER_ENABLED: bool = False
    
    # Platform Credentials
    GOOGLE_ADS_DEVELOPER_TOKEN: Optional[str] = None
    GOOGLE_ADS_CLIENT_ID: Optional[str] = None
    GOOGLE_ADS_CLIENT_SECRET: Optional[str] = None
    GOOGLE_ADS_REFRESH_TOKEN: Optional[str] = None
    
    META_APP_ID: Optional[str] = None
    META_APP_SECRET: Optional[str] = None
    META_ACCESS_TOKEN: Optional[str] = None
    
    TIKTOK_APP_ID: Optional[str] = None
    TIKTOK_SECRET: Optional[str] = None
    TIKTOK_ACCESS_TOKEN: Optional[str] = None
    
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_ACCESS_TOKEN: Optional[str] = None
    
    # Integrator Keys
    REVEALBOT_API_KEY: Optional[str] = None
    ADROLL_API_KEY: Optional[str] = None
    ADROLL_API_SECRET: Optional[str] = None
    STACKADAPT_API_KEY: Optional[str] = None
    ADESPRESSO_API_KEY: Optional[str] = None
    MADGICX_API_KEY: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    
    # Geographic
    DEFAULT_TIMEZONE: str = "UTC"
    SUPPORTED_REGIONS: List[str] = ["NA", "EU"]
    CURRENCY_USD: str = "USD"
    
    # Scheduler
    HOURLY_OPTIMIZATION_ENABLED: bool = True
    OPTIMIZATION_CRON: str = "0 * * * *"
    
    # Testing
    TEST_DATABASE_NAME: str = "ipop_test"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience instance
settings = get_settings()
