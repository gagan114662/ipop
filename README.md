uvicorn app.main:app --reload


brew services start postgresql@14
psql -U paras postgres
-- Create the "postgres" role with login and password
CREATE ROLE postgres WITH LOGIN PASSWORD 'password';

-- Optionally grant superuser privileges (or limit to specific permissions)
ALTER ROLE postgres WITH SUPERUSER;

-- Or: CREATE DATABASE privilege only
-- ALTER ROLE postgres CREATEDB;


uvicorn app.main:app --reload


After fix
psql -U postgres
CREATE DATABASE creative_resizer;
CREATE DATABASE creative_resizer ENCODING 'UTF8' LC_COLLATE 'en_US.UTF-8' LC_CTYPE 'en_US.UTF-8' TEMPLATE template0;
CREATE USER resizer_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE creative_resizer TO resizer_user;


# 1. Build and start all services
docker-compose up --build

# 2. Run database migrations (if needed)
docker-compose exec api alembic upgrade head

# 3. Access the application
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Flower: http://localhost:5555


# 1. Clone the repository
git clone <repository-url>
cd creative-resizer-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements-dev.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# 5. Start services (PostgreSQL & Redis)
docker-compose up db redis -d

# 6. Run database migrations
alembic upgrade head

# 7. Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 8. Start background worker (in another terminal)
python start_worker.py 
<!-- python -m app.workers.resize_worker -->


curl -X POST \
  'http://localhost:8000/api/v1/upload' \
  -H 'accept: application/json' \
  -F 'file=@testing_video.mp4;type=video/mp4' \
  -F 'platforms=["tiktok_short","instagram_reel","facebook_story","youtube_short","google_display_banner"]'


curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/upload' \
  -H 'accept: application/json' \
  -F 'file=@your_image.jpg;type=image/jpeg' \
  -F 'platforms=["instagram_feed","facebook_feed","google_display_banner"]'


# Upload an Image with use_ai_outfill=true

curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/upload' \
  -H 'accept: application/json' \
  -F 'file=@picofme.png;type=image/png' \
  -F 'platforms=["instagram_feed","facebook_feed","google_display_banner"]' \
   -F 'use_ai_outfill=true'



# init migrations
 alembic init migrations

# Generate migration
alembic revision --autogenerate -m "Add ai_output_fill to job table"

# Apply migration
alembic upgrade head


docker build -t rehmat11872/creative-resizer:latest .

# Secret key

-type python in terminal
-import secrets
-print(secrets.token_urlsafe(50))


docker buildx build --platform linux/amd64,linux/arm64 -t rehmat11872/creative-resizer:latest --push .


# First, completely clear all Hugging Face caches
rm -rf ~/.cache/huggingface
rm -rf /root/.cache/huggingface
rm -rf /workspace/huggingface
rm -rf /workspace/flux_model

# Set environment variables to redirect ALL Hugging Face operations
export HF_HOME="/workspace/hf_cache"
export HUGGINGFACE_HUB_CACHE="/workspace/hf_cache"
export TRANSFORMERS_CACHE="/workspace/hf_cache" 
export HF_DATASETS_CACHE="/workspace/hf_cache"
export TMPDIR="/workspace/temp"
export TMP="/workspace/temp"
export TEMP="/workspace/temp"

# Create the directories
mkdir -p /workspace/hf_cache
mkdir -p /workspace/temp
mkdir -p /workspace/flux_model

# Now download
python -c "
import os
from huggingface_hub import snapshot_download

# Verify environment variables are set
print('HF_HOME:', os.environ.get('HF_HOME'))
print('TMPDIR:', os.environ.get('TMPDIR'))

snapshot_download(
    'black-forest-labs/FLUX.1-Fill-dev',
    cache_dir='/workspace/flux_model',
    token=os.environ.get('HF_TOKEN'),
    resume_download=False
)
"

ls -lh /workspace/flux_model

ls /workspace/flux_model/models--black-forest-labs--FLUX.1-Fill-dev/snapshots/