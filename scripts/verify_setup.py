"""
Setup Verification Script

This script checks your environment and reports what's configured and working.

Usage:
    python scripts/verify_setup.py
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for running from scripts/
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
os.chdir(parent_dir)  # Change to parent directory for .env access

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def check_mark(status):
    """Return colored check mark based on status."""
    if status:
        return f"{GREEN}✓{RESET}"
    return f"{RED}✗{RESET}"


def status_icon(status):
    """Return status icon."""
    if status == "good":
        return f"{GREEN}●{RESET}"
    elif status == "warning":
        return f"{YELLOW}●{RESET}"
    return f"{RED}●{RESET}"


def check_env_file():
    """Check if .env file exists."""
    return os.path.exists('.env')


def check_env_var(var_name, required=True):
    """Check if environment variable is set."""
    value = os.getenv(var_name)
    is_set = value is not None and value != ""
    
    if required:
        return check_mark(is_set), is_set
    else:
        return check_mark(is_set), is_set


def check_mongodb():
    """Check MongoDB connection."""
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import asyncio
        
        async def test_connection():
            client = AsyncIOMotorClient(os.getenv('MONGODB_URL', 'mongodb://localhost:27017'))
            try:
                await client.admin.command('ping')
                client.close()
                return True
            except:
                return False
        
        return asyncio.run(test_connection())
    except:
        return False


def check_redis():
    """Check Redis connection."""
    try:
        import redis
        r = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
        r.ping()
        return True
    except:
        return False


def main():
    """Run all verification checks."""
    
    print(f"\n{BOLD}{BLUE}═══════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}{BLUE}   IPOP Media Buying Management System - Setup Check{RESET}")
    print(f"{BOLD}{BLUE}═══════════════════════════════════════════════════════{RESET}\n")
    
    # Load .env if it exists
    if check_env_file():
        from dotenv import load_dotenv
        load_dotenv()
        print(f"{check_mark(True)} .env file found\n")
    else:
        print(f"{check_mark(False)} .env file NOT found - using system environment\n")
    
    # Core Requirements
    print(f"{BOLD}Core Requirements:{RESET}")
    print("─" * 55)
    
    secret_key_check, secret_key_set = check_env_var('SECRET_KEY', required=True)
    mongo_check, mongo_set = check_env_var('MONGODB_URL', required=True)
    redis_check, redis_set = check_env_var('REDIS_URL', required=True)
    
    print(f"{secret_key_check} SECRET_KEY: ", end="")
    if secret_key_set:
        secret_len = len(os.getenv('SECRET_KEY', ''))
        if secret_len >= 32:
            print(f"{GREEN}Set ({secret_len} chars){RESET}")
        else:
            print(f"{YELLOW}Set but too short ({secret_len} chars, need 32+){RESET}")
    else:
        print(f"{RED}Not set (REQUIRED){RESET}")
    
    print(f"{mongo_check} MONGODB_URL: ", end="")
    if mongo_set:
        mongo_working = check_mongodb()
        if mongo_working:
            print(f"{GREEN}Connected ✓{RESET}")
        else:
            print(f"{YELLOW}Set but connection failed{RESET}")
    else:
        print(f"{RED}Not set (REQUIRED){RESET}")
    
    print(f"{redis_check} REDIS_URL: ", end="")
    if redis_set:
        redis_working = check_redis()
        if redis_working:
            print(f"{GREEN}Connected ✓{RESET}")
        else:
            print(f"{YELLOW}Set but connection failed{RESET}")
    else:
        print(f"{RED}Not set (REQUIRED){RESET}")
    
    # Platform APIs
    print(f"\n{BOLD}Platform APIs (for real campaign data):{RESET}")
    print("─" * 55)
    
    # Google Ads
    ga_token, ga_token_set = check_env_var('GOOGLE_ADS_DEVELOPER_TOKEN', required=False)
    ga_client, ga_client_set = check_env_var('GOOGLE_ADS_CLIENT_ID', required=False)
    ga_secret, ga_secret_set = check_env_var('GOOGLE_ADS_CLIENT_SECRET', required=False)
    ga_refresh, ga_refresh_set = check_env_var('GOOGLE_ADS_REFRESH_TOKEN', required=False)
    
    google_ads_complete = all([ga_token_set, ga_client_set, ga_secret_set, ga_refresh_set])
    print(f"{status_icon('good' if google_ads_complete else 'bad')} Google Ads API: ", end="")
    if google_ads_complete:
        print(f"{GREEN}Fully configured ✓{RESET}")
    elif any([ga_token_set, ga_client_set, ga_secret_set, ga_refresh_set]):
        print(f"{YELLOW}Partially configured (missing credentials){RESET}")
    else:
        print(f"{RED}Not configured{RESET}")
    
    # Meta
    meta_app, meta_app_set = check_env_var('META_APP_ID', required=False)
    meta_secret, meta_secret_set = check_env_var('META_APP_SECRET', required=False)
    meta_token, meta_token_set = check_env_var('META_ACCESS_TOKEN', required=False)
    
    meta_complete = all([meta_app_set, meta_secret_set, meta_token_set])
    print(f"{status_icon('good' if meta_complete else 'bad')} Meta Marketing API: ", end="")
    if meta_complete:
        print(f"{GREEN}Fully configured ✓{RESET}")
    elif any([meta_app_set, meta_secret_set, meta_token_set]):
        print(f"{YELLOW}Partially configured (missing credentials){RESET}")
    else:
        print(f"{RED}Not configured{RESET}")
    
    # TikTok
    tt_app, tt_app_set = check_env_var('TIKTOK_APP_ID', required=False)
    tt_secret, tt_secret_set = check_env_var('TIKTOK_SECRET', required=False)
    tt_token, tt_token_set = check_env_var('TIKTOK_ACCESS_TOKEN', required=False)
    
    tiktok_complete = all([tt_app_set, tt_secret_set, tt_token_set])
    print(f"{status_icon('good' if tiktok_complete else 'warning')} TikTok Ads API: ", end="")
    if tiktok_complete:
        print(f"{GREEN}Fully configured ✓{RESET}")
    elif any([tt_app_set, tt_secret_set, tt_token_set]):
        print(f"{YELLOW}Partially configured{RESET}")
    else:
        print(f"{YELLOW}Not configured (optional){RESET}")
    
    # LinkedIn
    li_client, li_client_set = check_env_var('LINKEDIN_CLIENT_ID', required=False)
    li_secret, li_secret_set = check_env_var('LINKEDIN_CLIENT_SECRET', required=False)
    li_token, li_token_set = check_env_var('LINKEDIN_ACCESS_TOKEN', required=False)
    
    linkedin_complete = all([li_client_set, li_secret_set, li_token_set])
    print(f"{status_icon('good' if linkedin_complete else 'warning')} LinkedIn Ads API: ", end="")
    if linkedin_complete:
        print(f"{GREEN}Fully configured ✓{RESET}")
    elif any([li_client_set, li_secret_set, li_token_set]):
        print(f"{YELLOW}Partially configured{RESET}")
    else:
        print(f"{YELLOW}Not configured (optional){RESET}")
    
    # Integrators
    print(f"\n{BOLD}Media Buying Integrators (optional):{RESET}")
    print("─" * 55)
    
    integrators = {
        'Revealbot': 'REVEALBOT_API_KEY',
        'AdRoll': 'ADROLL_API_KEY',
        'StackAdapt': 'STACKADAPT_API_KEY',
        'AdEspresso': 'ADESPRESSO_API_KEY',
        'Madgicx': 'MADGICX_API_KEY'
    }
    
    for name, var in integrators.items():
        check, is_set = check_env_var(var, required=False)
        print(f"{check} {name:12} ", end="")
        if is_set:
            print(f"{GREEN}Configured{RESET}")
        else:
            print(f"{YELLOW}Not configured (optional){RESET}")
    
    # Summary
    print(f"\n{BOLD}Status Summary:{RESET}")
    print("─" * 55)
    
    core_ready = all([secret_key_set, mongo_set, redis_set])
    platforms_ready = google_ads_complete or meta_complete
    
    if core_ready and check_mongodb() and check_redis():
        print(f"{GREEN}✓ Core system ready to run{RESET}")
        
        if platforms_ready:
            print(f"{GREEN}✓ At least one platform configured{RESET}")
            print(f"\n{GREEN}{BOLD}System is READY for production use!{RESET}")
        else:
            print(f"{YELLOW}⚠ No platforms configured (will use test data only){RESET}")
            print(f"\n{YELLOW}{BOLD}System ready for TESTING with mock data.{RESET}")
            print(f"{YELLOW}Configure platform APIs for real campaign management.{RESET}")
    else:
        print(f"{RED}✗ Core system not ready{RESET}")
        print(f"\n{RED}{BOLD}Action required:{RESET}")
        if not secret_key_set:
            print(f"  {RED}• Set SECRET_KEY in .env file{RESET}")
        if not mongo_set or not check_mongodb():
            print(f"  {RED}• Fix MongoDB connection{RESET}")
        if not redis_set or not check_redis():
            print(f"  {RED}• Fix Redis connection{RESET}")
    
    # Next Steps
    print(f"\n{BOLD}Next Steps:{RESET}")
    print("─" * 55)
    
    if not core_ready:
        print(f"1. Create .env file: {BLUE}cp .env.example .env{RESET}")
        print(f"2. Set SECRET_KEY (32+ chars)")
        print(f"3. Start services: {BLUE}docker-compose up -d{RESET}")
    elif not platforms_ready:
        print(f"1. Seed test data: {BLUE}docker-compose exec api python -m app.db.seed_test_data{RESET}")
        print(f"2. Access API docs: {BLUE}http://localhost:8000/docs{RESET}")
        print(f"3. Login with: test@testcompany.com / password123")
        print(f"4. Configure platform APIs when ready (see API_KEYS_GUIDE.md)")
    else:
        print(f"1. Start server: {BLUE}docker-compose up -d{RESET}")
        print(f"2. Access API docs: {BLUE}http://localhost:8000/docs{RESET}")
        print(f"3. Test platform connections")
        print(f"4. Run first optimization!")
    
    print(f"\n{BOLD}Documentation:{RESET}")
    print("─" * 55)
    print(f"• Quick Start: {BLUE}QUICKSTART.md{RESET}")
    print(f"• Testing Guide: {BLUE}TESTING_GUIDE.md{RESET}")
    print(f"• API Keys Setup: {BLUE}API_KEYS_GUIDE.md{RESET}")
    print(f"• API Docs: {BLUE}http://localhost:8000/docs{RESET}")
    
    print(f"\n{BOLD}{BLUE}═══════════════════════════════════════════════════════{RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Verification cancelled.{RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{RED}Error during verification: {e}{RESET}\n")
        sys.exit(1)
