# Scripts

Utility scripts for setup, authentication, and maintenance tasks.

## Scripts

- `linkedin_oauth.py` - LinkedIn OAuth authentication helper
- `meta_access_token.py` - Meta/Facebook access token generator  
- `verify_setup.py` - Setup verification script
- `setup_mongodb.sh` - MongoDB setup and initialization script

## Usage

### Authentication Scripts

Generate access tokens for platform integrations:
```bash
python scripts/linkedin_oauth.py
python scripts/meta_access_token.py
```

### Setup Verification

Verify your IPOP installation:
```bash
python scripts/verify_setup.py
```

### MongoDB Setup

Initialize MongoDB (Linux/Mac):
```bash
bash scripts/setup_mongodb.sh
```

