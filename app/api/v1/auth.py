"""
Authentication API endpoints - JWT-based authentication with refresh tokens.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import secrets
import uuid
from typing import Dict, List, Optional
from urllib.parse import urlencode
import structlog

import httpx
from pydantic import BaseModel

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
from app.core.token_manager import TokenManager

logger = structlog.get_logger(__name__)

router = APIRouter()

OAUTH_META_AUTHORIZE_URL = "https://www.facebook.com/v18.0/dialog/oauth"
OAUTH_META_TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"
OAUTH_LINKEDIN_AUTHORIZE_URL = "https://www.linkedin.com/oauth/v2/authorization"
OAUTH_LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
OAUTH_GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
OAUTH_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


class OAuthAuthorizeResponse(BaseModel):
    """Response containing browser authorization details."""
    provider: str
    authorization_url: str
    state: str
    redirect_uri: str
    scopes: List[str]


class OAuthProviderDetails(BaseModel):
    """Metadata describing a configured OAuth provider."""
    provider: str
    display_name: str
    scopes: List[str]


class OAuthProvidersResponse(BaseModel):
    """Response listing configured OAuth providers."""
    providers: List[OAuthProviderDetails]


class OAuthCallbackResponse(Token):
    """Response issued after completing OAuth flow."""
    provider: str
    platform_access_token: str
    platform_token_expires_in: Optional[int] = None


def _resolve_callback_url(
    request: Request,
    provider: str,
    override: Optional[str] = None
) -> str:
    """
    Build the callback URL that must match provider configuration.
    
    Args:
        request: Current request used to derive base URL when not overridden.
        provider: OAuth provider identifier.
        override: Optional explicit callback URL.
    
    Returns:
        Absolute callback URL for the provider.
    """
    if override:
        return override
    
    if settings.OAUTH_CALLBACK_BASE_URL:
        base_url = settings.OAUTH_CALLBACK_BASE_URL.rstrip("/")
    else:
        base_url = str(request.base_url).rstrip("/")
    
    return f"{base_url}{settings.API_V1_PREFIX}/auth/oauth/{provider}/callback"


def _get_enabled_oauth_providers() -> List[OAuthProviderDetails]:
    """Return provider metadata for providers with credentials configured."""
    providers: List[OAuthProviderDetails] = []
    
    if settings.META_APP_ID and settings.META_APP_SECRET:
        providers.append(
            OAuthProviderDetails(
                provider="meta",
                display_name="Meta (Facebook/Instagram)",
                scopes=settings.META_OAUTH_SCOPES
            )
        )
    
    if settings.LINKEDIN_CLIENT_ID and settings.LINKEDIN_CLIENT_SECRET:
        providers.append(
            OAuthProviderDetails(
                provider="linkedin",
                display_name="LinkedIn Marketing",
                scopes=settings.LINKEDIN_OAUTH_SCOPES
            )
        )
    
    if settings.GOOGLE_ADS_CLIENT_ID and settings.GOOGLE_ADS_CLIENT_SECRET:
        providers.append(
            OAuthProviderDetails(
                provider="google",
                display_name="Google Ads",
                scopes=settings.GOOGLE_ADS_OAUTH_SCOPES
            )
        )
    
    return providers


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


@router.get("/oauth/providers", response_model=OAuthProvidersResponse)
async def list_oauth_providers():
    """
    List configured OAuth providers.
    
    Returns providers that have credentials available in settings.
    """
    providers = _get_enabled_oauth_providers()
    return OAuthProvidersResponse(providers=providers)


@router.get("/oauth/{provider}/authorize", response_model=OAuthAuthorizeResponse)
async def oauth_authorize(
    provider: str,
    request: Request,
    client_id: Optional[str] = Query(
        default=None,
        description="Existing client_id to associate tokens with; optional for manual testing."
    ),
    redirect_uri: Optional[str] = Query(
        default=None,
        description="Override callback URL if hosting differs from the API base URL."
    ),
    state: Optional[str] = Query(
        default=None,
        description="Optional state parameter. When omitted a random state is generated."
    ),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Generate an authorization URL for the requested OAuth provider.
    
    The generated URL can be opened in a browser to complete provider login.
    """
    providers = {p.provider: p for p in _get_enabled_oauth_providers()}
    
    if provider not in providers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider}' is not configured"
        )
    
    if client_id:
        client_exists = await db.clients.find_one({"client_id": client_id})
        if not client_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unknown client_id"
            )
    
    selected_provider = providers[provider]
    resolved_state = state or secrets.token_urlsafe(32)
    
    if client_id:
        resolved_state = f"{client_id}:{resolved_state}"
    
    callback_url = _resolve_callback_url(request, provider, redirect_uri)
    
    if provider == "meta":
        scopes = settings.META_OAUTH_SCOPES
        if not (settings.META_APP_ID and settings.META_APP_SECRET):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meta credentials not configured"
            )
        
        params = {
            "client_id": settings.META_APP_ID,
            "redirect_uri": callback_url,
            "state": resolved_state,
            "response_type": "code",
            "scope": ",".join(scopes)
        }
        authorization_url = f"{OAUTH_META_AUTHORIZE_URL}?{urlencode(params)}"
    elif provider == "linkedin":
        scopes = settings.LINKEDIN_OAUTH_SCOPES
        if not (settings.LINKEDIN_CLIENT_ID and settings.LINKEDIN_CLIENT_SECRET):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LinkedIn credentials not configured"
            )
        
        params = {
            "response_type": "code",
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "redirect_uri": callback_url,
            "state": resolved_state,
            "scope": " ".join(scopes)
        }
        authorization_url = f"{OAUTH_LINKEDIN_AUTHORIZE_URL}?{urlencode(params)}"
    elif provider == "google":
        scopes = settings.GOOGLE_ADS_OAUTH_SCOPES
        if not (settings.GOOGLE_ADS_CLIENT_ID and settings.GOOGLE_ADS_CLIENT_SECRET):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google Ads OAuth credentials not configured"
            )
        
        params = {
            "response_type": "code",
            "client_id": settings.GOOGLE_ADS_CLIENT_ID,
            "redirect_uri": callback_url,
            "state": resolved_state,
            "scope": " ".join(scopes),
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true"
        }
        authorization_url = f"{OAUTH_GOOGLE_AUTHORIZE_URL}?{urlencode(params)}"
    
    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"OAuth provider '{provider}' is not implemented yet"
        )
    
    return OAuthAuthorizeResponse(
        provider=provider,
        authorization_url=authorization_url,
        state=resolved_state,
        redirect_uri=callback_url,
        scopes=selected_provider.scopes
    )


@router.get("/oauth/{provider}/callback", response_model=OAuthCallbackResponse)
async def oauth_callback(
    provider: str,
    request: Request,
    code: str = Query(..., description="Authorization code supplied by the provider."),
    state: Optional[str] = Query(None, description="State parameter returned by the provider."),
    client_id: Optional[str] = Query(
        default=None,
        description="client_id to associate tokens with. When omitted, tries to derive from state."
    ),
    redirect_uri: Optional[str] = Query(
        default=None,
        description="Explicit callback URL. Must match the value used during authorize."
    ),
    error: Optional[str] = Query(None, description="Error code returned by provider."),
    error_description: Optional[str] = Query(None, description="Provider error description."),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    OAuth callback endpoint.
    
    Exchanges the provider code for an access token, stores it, and issues JWTs.
    """
    if error:
        detail = error_description or error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth provider returned error: {detail}"
        )
    
    providers = {p.provider: p for p in _get_enabled_oauth_providers()}
    
    if provider not in providers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider}' is not configured"
        )
    
    derived_client_id = client_id
    
    if not derived_client_id and state and ":" in state:
        derived_client_id = state.split(":", 1)[0]
    
    if not derived_client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="client_id must be provided either directly or encoded in state"
        )
    
    client_doc = await db.clients.find_one({"client_id": derived_client_id})
    if not client_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown client_id"
        )
    
    callback_url = _resolve_callback_url(request, provider, redirect_uri)
    token_manager = TokenManager(db)
    existing_token_doc = await db.platform_tokens.find_one({
        "client_id": derived_client_id,
        "platform": provider
    })
    
    platform_access_token: Optional[str] = None
    platform_expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    
    if provider == "meta":
        if not (settings.META_APP_ID and settings.META_APP_SECRET):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meta credentials not configured"
            )
        
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            exchange_params = {
                "client_id": settings.META_APP_ID,
                "client_secret": settings.META_APP_SECRET,
                "redirect_uri": callback_url,
                "code": code
            }
            
            exchange_response = await http_client.get(
                OAUTH_META_TOKEN_URL,
                params=exchange_params
            )
            
            if exchange_response.status_code != status.HTTP_200_OK:
                logger.error(
                    "meta_oauth_exchange_failed",
                    status_code=exchange_response.status_code,
                    response=exchange_response.text
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange Meta authorization code for token"
                )
            
            exchange_data = exchange_response.json()
            short_lived_token = exchange_data.get("access_token")
            expires_in = exchange_data.get("expires_in")
            
            if not short_lived_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Meta did not return an access_token"
                )
            
            # Attempt to upgrade to a long-lived token for convenience
            long_lived_token = None
            long_lived_expires = None
            try:
                long_lived_params = {
                    "grant_type": "fb_exchange_token",
                    "client_id": settings.META_APP_ID,
                    "client_secret": settings.META_APP_SECRET,
                    "fb_exchange_token": short_lived_token
                }
                long_lived_resp = await http_client.get(
                    OAUTH_META_TOKEN_URL,
                    params=long_lived_params
                )
                if long_lived_resp.status_code == status.HTTP_200_OK:
                    long_data = long_lived_resp.json()
                    long_lived_token = long_data.get("access_token")
                    long_lived_expires = long_data.get("expires_in")
                else:
                    logger.warning(
                        "meta_long_lived_exchange_failed",
                        status_code=long_lived_resp.status_code,
                        response=long_lived_resp.text
                    )
            except Exception as exc:
                logger.warning("meta_long_lived_exchange_error", error=str(exc))
            
            platform_access_token = long_lived_token or short_lived_token
            platform_expires_in = long_lived_expires or expires_in
            refresh_token = long_lived_token or short_lived_token
    
    elif provider == "linkedin":
        if not (settings.LINKEDIN_CLIENT_ID and settings.LINKEDIN_CLIENT_SECRET):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LinkedIn credentials not configured"
            )
        
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": callback_url,
                "client_id": settings.LINKEDIN_CLIENT_ID,
                "client_secret": settings.LINKEDIN_CLIENT_SECRET
            }
            
            token_response = await http_client.post(
                OAUTH_LINKEDIN_TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if token_response.status_code != status.HTTP_200_OK:
                logger.error(
                    "linkedin_oauth_exchange_failed",
                    status_code=token_response.status_code,
                    response=token_response.text
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange LinkedIn authorization code for token"
                )
            
            token_data = token_response.json()
            platform_access_token = token_data.get("access_token")
            platform_expires_in = token_data.get("expires_in")
            refresh_token = token_data.get("refresh_token")
    
    elif provider == "google":
        if not (settings.GOOGLE_ADS_CLIENT_ID and settings.GOOGLE_ADS_CLIENT_SECRET):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google Ads OAuth credentials not configured"
            )
        
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": callback_url,
                "client_id": settings.GOOGLE_ADS_CLIENT_ID,
                "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET
            }
            
            token_response = await http_client.post(
                OAUTH_GOOGLE_TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if token_response.status_code != status.HTTP_200_OK:
                logger.error(
                    "google_oauth_exchange_failed",
                    status_code=token_response.status_code,
                    response=token_response.text
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange Google authorization code for token"
                )
            
            token_data = token_response.json()
            platform_access_token = token_data.get("access_token")
            platform_expires_in = token_data.get("expires_in")
            refresh_token = token_data.get("refresh_token")
    
    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"OAuth provider '{provider}' is not implemented yet"
        )
    
    if not platform_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider did not return an access token"
        )
    
    if not refresh_token and existing_token_doc:
        refresh_token = existing_token_doc.get("refresh_token")
    
    await token_manager.store_token(
        platform=provider,
        client_id=derived_client_id,
        access_token=platform_access_token,
        refresh_token=refresh_token,
        expires_in=platform_expires_in or 3600
    )
    
    logger.info(
        "oauth_token_stored",
        provider=provider,
        client_id=derived_client_id,
        expires_in=platform_expires_in
    )
    
    client = ClientInDB(**client_doc)
    token_payload = {"sub": client.email, "client_id": client.client_id, "roles": ["client"]}
    app_access_token = create_access_token(token_payload)
    app_refresh_token = create_refresh_token(token_payload)
    
    return OAuthCallbackResponse(
        provider=provider,
        access_token=app_access_token,
        refresh_token=app_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        platform_access_token=platform_access_token,
        platform_token_expires_in=platform_expires_in
    )
