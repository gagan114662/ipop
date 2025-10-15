# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field, Extra
from dotenv import load_dotenv
from typing import List, Optional

# Load .env manually
load_dotenv() 

class Settings(BaseSettings):
    # Explicitly map environment variables to fields
    MONGODB_URL: str = Field(..., env="MONGODB_URL")
    DATABASE_NAME: str = Field("resizebackend", env="DATABASE_NAME")


        # Application
    APP_NAME: str = "Creative Content Resizer"
    DEBUG: bool = Field(default=False)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # Security
    SECRET_KEY: str = Field(...)
    ALLOWED_HOSTS: List[str] = Field(default=["*"])
    
    # Database
    # DATABASE_URL: str = Field(...)
    # DB_ECHO: bool = Field(default=False)
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379")
    REDIS_DB: int = Field(default=0)
    
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

    class Config:
        env_file = ".env"
        # env_file_encoding = "utf-8"
        case_sensitive = True
        extra = Extra.allow

# Create settings instance
settings = Settings()

