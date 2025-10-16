from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
from pathlib import Path
from pydantic import Extra


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "Creative Content Resizer"
    DEBUG: bool = Field(default=False)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # Security
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production")
    ALLOWED_HOSTS: List[str] = Field(default=["*"])
    
    # Database (PostgreSQL - DEPRECATED, using MongoDB now)
    DATABASE_URL: Optional[str] = Field(default=None)
    DB_ECHO: bool = Field(default=False)
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379")
    REDIS_DB: int = Field(default=0)

    # MongoDB
    MONGODB_URL: str = Field(default="mongodb://localhost:27017")
    MONGODB_DB: str = Field(default="creative_resizer")
    
    # File Upload
    MAX_FILE_SIZE: int = Field(default=500 * 1024 * 1024)  # 500MB
    ALLOWED_IMAGE_EXTENSIONS: List[str] = Field(default=[".jpg", ".jpeg", ".png"])
    ALLOWED_VIDEO_EXTENSIONS: List[str] = Field(default=[".mp4", ".mov"])
    UPLOAD_DIR: str = Field(default="uploads")
    OUTPUT_DIR: str = Field(default="outputs")
    
    # Job Processing
    JOB_TIMEOUT: int = Field(default=3600)  # 1 hour
    MAX_CONCURRENT_JOBS: int = Field(default=5)
    CLEANUP_INTERVAL: int = Field(default=86400)  # 24 hours
    
    # External APIs
    FFMPEG_PATH: str = Field(default="ffmpeg")

    # Hugging Face
    HF_TOKEN: str = Field(default="dummy-token", description="Hugging Face API token")
    HF_HOME: str = Field(default="/workspace/huggingface")
    HF_HUB_CACHE: str = Field(default="/workspace/huggingface")
    TRANSFORMERS_CACHE: str = Field(default="/workspace/huggingface")
    TMPDIR: str = Field(default="/workspace/huggingface/tmp")

    # AI Services
    AI_OUTFILL_API_URL: Optional[str] = Field(default=None)
    AI_OUTFILL_API_KEY: Optional[str] = Field(default=None)
    COMFYUI_API_URL: Optional[str] = Field(default="http://localhost:8188")
    
    @validator("UPLOAD_DIR", "OUTPUT_DIR")
    def create_directories(cls, v):
        """Ensure directories exist"""
        Path(v).mkdir(parents=True, exist_ok=True)
        return v
    
    # @validator("DATABASE_URL")
    # def validate_database_url(cls, v):
    #     """Validate database URL format"""
    #     if v and not v.startswith(("postgresql://", "postgresql+asyncpg://")):
    #         raise ValueError("DATABASE_URL must be a PostgreSQL URL")
    #     return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = Extra.allow


# Create settings instance
settings = Settings()
