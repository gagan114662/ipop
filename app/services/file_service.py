# app/services/file_service.py
import os
import uuid
from pathlib import Path
from fastapi import UploadFile
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)

    async def save_upload(self, file: UploadFile) -> Path:
        """Save uploaded file to disk and return its path"""
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        file_path = self.upload_dir / unique_filename

        # Ensure directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # Write file
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            logger.info(f"File saved: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise