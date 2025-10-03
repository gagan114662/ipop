"""
Authentication API endpoints - JWT-based authentication with refresh tokens.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
import structlog

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    validate_refresh_token,
    get_current_user
)
from app.core.config import settings
from app.models.client import (
    ClientCreate,
    ClientInDB,
    LoginRequest,
    Token,
    TokenRefresh
)

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    client_data: ClientCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Register a new client account.
    
    Creates a new multi-tenant client with hashed password and returns JWT tokens.
    """
    # Check if email already exists
    existing = await db.clients.find_one({"email": client_data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create client document
    client_id = str(uuid.uuid4())
    hashed_pwd = hash_password(client_data.password)
    
    client = ClientInDB(
        client_id=client_id,
        company_name=client_data.company_name,
        email=client_data.email,
        hashed_password=hashed_pwd,
        is_active=client_data.is_active,
        settings=client_data.settings
    )
    
    # Insert into database
    result = await db.clients.insert_one(
        client.dict(by_alias=True, exclude={"id"})
    )
    client.id = result.inserted_id
    
    logger.info("client_registered", client_id=client_id, email=client_data.email)
    
    # Generate tokens
    token_data = {"sub": client.email, "client_id": client_id, "roles": ["client"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login", response_model=Token)
async def login(
    credentials: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Authenticate client and return JWT tokens.
    
    Validates credentials and returns access + refresh tokens.
    """
    # Find client by email
    client_doc = await db.clients.find_one({"email": credentials.email})
    
    if not client_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    client = ClientInDB(**client_doc)
    
    # Verify password
    if not verify_password(credentials.password, client.hashed_password):
        logger.warning("login_failed", email=credentials.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if client is active
    if not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    await db.clients.update_one(
        {"email": credentials.email},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    logger.info("client_logged_in", client_id=client.client_id, email=credentials.email)
    
    # Generate tokens
    token_data = {"sub": client.email, "client_id": client.client_id, "roles": ["client"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Validates refresh token and issues new access + refresh tokens (refresh token rotation).
    """
    # Validate refresh token
    payload = validate_refresh_token(token_data.refresh_token)
    
    email = payload.get("sub")
    client_id = payload.get("client_id")
    
    # Verify client still exists and is active
    client_doc = await db.clients.find_one({"email": email, "client_id": client_id})
    
    if not client_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    client = ClientInDB(**client_doc)
    
    if not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    logger.info("token_refreshed", client_id=client_id)
    
    # Generate new tokens (refresh token rotation)
    new_token_data = {"sub": email, "client_id": client_id, "roles": ["client"]}
    access_token = create_access_token(new_token_data)
    new_refresh_token = create_refresh_token(new_token_data)
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me")
async def get_current_client(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get current authenticated client information.
    """
    client_doc = await db.clients.find_one({"client_id": current_user["client_id"]})
    
    if not client_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    client = ClientInDB(**client_doc)
    
    return {
        "client_id": client.client_id,
        "email": client.email,
        "company_name": client.company_name,
        "is_active": client.is_active,
        "settings": client.settings
    }


from datetime import datetime
