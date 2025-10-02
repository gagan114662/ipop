# ========================
# Stage 1: Base Image
# ========================
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system deps (for Pillow, ffmpeg etc.)
RUN apt-get update && apt-get install -y \
    git wget curl ffmpeg libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ========================
# Stage 2: Install Python deps
# ========================
# Copy requirements
COPY requirements.txt .

# Upgrade pip + install deps
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ========================
# Stage 3: HuggingFace cache setup
# ========================
RUN mkdir -p /workspace/huggingface
ENV HF_HOME=/workspace/huggingface
ENV HF_HUB_CACHE=/workspace/huggingface
ENV TRANSFORMERS_CACHE=/workspace/huggingface
ENV TMPDIR=/workspace/huggingface/tmp

# ========================
# Stage 4: Copy project
# ========================
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Default startup (using uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# CMD ["python", "serverless_handler.py"]
   