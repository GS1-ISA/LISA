"""
Authentication and Authorization Module for ISA_D API Server

This module provides:
- JWT token generation and validation
- Password hashing with bcrypt
- User model with role-based access control
- API key generation and validation
- Database models for user management
"""

import os
import secrets
import string
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

import bcrypt
import jwt

# OAuth2/OIDC imports
from authlib.integrations.base_client import OAuthError
from authlib.integrations.httpx_client import AsyncOAuth2Client
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from src.database_manager import get_db_manager

# Encryption imports
from src.encryption import EncryptedText
from src.shared.paths import DEFAULT_DATABASE_URL

# Database setup with connection pooling
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
db_manager = get_db_manager(DATABASE_URL)
Base = declarative_base()

# SessionLocal for backward compatibility with tests
SessionLocal = db_manager._session_maker
# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# OAuth2/OIDC Configuration
OAUTH2_CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID")
OAUTH2_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET")
OAUTH2_AUTHORIZE_URL = os.getenv("OAUTH2_AUTHORIZE_URL")
OAUTH2_TOKEN_URL = os.getenv("OAUTH2_TOKEN_URL")
OAUTH2_USERINFO_URL = os.getenv("OAUTH2_USERINFO_URL")
OAUTH2_REDIRECT_URI = os.getenv("OAUTH2_REDIRECT_URI", "http://localhost:8000/auth/oauth2/callback")
OAUTH2_SCOPE = os.getenv("OAUTH2_SCOPE", "openid email profile")

# Encryption configuration for sensitive data
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "your-encryption-key-change-in-production")

class UserRole(str, Enum):
    """User roles for role-based access control"""
    ADMIN = "admin"
    RESEARCHER = "researcher"
    VIEWER = "viewer"

class User(Base):
    """Database model for users"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default=UserRole.VIEWER.value, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    api_key = Column(String, unique=True, index=True)
    api_key_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

class APIKey(Base):
    """Database model for API keys"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime)

class OAuth2Provider(Base):
    """Database model for OAuth2/OIDC providers"""
    __tablename__ = "oauth2_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    client_id = Column(String, nullable=False)
    client_secret = Column(EncryptedText, nullable=False)  # Encrypted
    authorize_url = Column(String, nullable=False)
    token_url = Column(String, nullable=False)
    userinfo_url = Column(String, nullable=False)
    scope = Column(String, default="openid email profile")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class OAuth2User(Base):
    """Database model for OAuth2/OIDC user associations"""
    __tablename__ = "oauth2_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    provider_id = Column(Integer, nullable=False)
    provider_user_id = Column(String, nullable=False)
    provider_user_email = Column(String)
    provider_user_name = Column(String)
    access_token = Column(EncryptedText)  # Encrypted
    refresh_token = Column(EncryptedText)  # Encrypted
    token_expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic models for API
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str | None = None
    role: UserRole = UserRole.VIEWER

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None
    role: UserRole | None = None

class LoginRequest(BaseModel):
    username: str
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

# OAuth2/OIDC Pydantic models
class OAuth2ProviderBase(BaseModel):
    name: str
    client_id: str
    client_secret: str
    authorize_url: str
    token_url: str
    userinfo_url: str
    scope: str = "openid email profile"

class OAuth2ProviderCreate(OAuth2ProviderBase):
    pass

class OAuth2ProviderInDB(OAuth2ProviderBase):
    id: int
    is_active: bool
    created_at: datetime

class OAuth2LoginRequest(BaseModel):
    provider: str
    redirect_uri: str | None = None

class OAuth2CallbackRequest(BaseModel):
    code: str
    state: str
    provider: str

class OAuth2TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    provider: str
    user_info: dict[str, Any]

# Authentication functions
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> TokenData | None:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            return None
        return TokenData(username=username, role=UserRole(role) if role else None)
    except jwt.PyJWTError:
        return None

def generate_api_key() -> str:
    """Generate a secure API key"""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(32))

def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage"""
    return bcrypt.hashpw(api_key.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash"""
    return bcrypt.checkpw(plain_key.encode("utf-8"), hashed_key.encode("utf-8"))


# Database operations
# get_db is now imported from database_manager

def get_user_by_username(db: Session, username: str) -> User | None:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_api_key(db: Session, api_key: str) -> User | None:
    """Get user by API key"""
    # Find API key record
    api_key_record = db.query(APIKey).filter(
        APIKey.is_active,
        APIKey.expires_at > datetime.now(timezone.utc) if APIKey.expires_at else True
    ).first()

    if not api_key_record:
        return None

    # Verify the key
    if not verify_api_key(api_key, api_key_record.key_hash):
        return None

    # Update last used
    api_key_record.last_used = datetime.now(timezone.utc)
    db.commit()

    # Return the user
    return db.query(User).filter(User.id == api_key_record.user_id).first()

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    hashed_password = hash_password(user.password)
    api_key = generate_api_key()
    api_key_hash = hash_api_key(api_key)

    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role.value,
        api_key=api_key,
        api_key_hash=api_key_hash
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create API key record
    db_api_key = APIKey(
        key_hash=api_key_hash,
        user_id=db_user.id,
        name="Default API Key"
    )
    db.add(db_api_key)
    db.commit()

    return db_user

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Authenticate a user with username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    return user

def update_user_password(db: Session, user: User, new_password: str):
    """Update user password"""
    user.hashed_password = hash_password(new_password)
    user.updated_at = datetime.now(timezone.utc)
    db.commit()

def check_user_permissions(user: User, required_role: UserRole) -> bool:
    """Check if user has required role permissions"""
    role_hierarchy = {
        UserRole.VIEWER: 1,
        UserRole.RESEARCHER: 2,
        UserRole.ADMIN: 3
    }

    user_level = role_hierarchy.get(UserRole(user.role), 0)
    required_level = role_hierarchy.get(required_role, 0)

    return user_level >= required_level

# OAuth2/OIDC functions
def get_oauth2_provider_by_name(db: Session, name: str) -> OAuth2Provider | None:
    """Get OAuth2 provider by name"""
    return db.query(OAuth2Provider).filter(
        OAuth2Provider.name == name,
        OAuth2Provider.is_active
    ).first()

def create_oauth2_provider(db: Session, provider: OAuth2ProviderCreate) -> OAuth2Provider:
    """Create a new OAuth2 provider"""
    db_provider = OAuth2Provider(
        name=provider.name,
        client_id=provider.client_id,
        client_secret=provider.client_secret,  # Will be encrypted automatically by EncryptedText column
        authorize_url=provider.authorize_url,
        token_url=provider.token_url,
        userinfo_url=provider.userinfo_url,
        scope=provider.scope
    )

    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

def get_oauth2_user_association(db: Session, user_id: int, provider_id: int) -> OAuth2User | None:
    """Get OAuth2 user association"""
    return db.query(OAuth2User).filter(
        OAuth2User.user_id == user_id,
        OAuth2User.provider_id == provider_id
    ).first()

def create_oauth2_user_association(
    db: Session,
    user_id: int,
    provider_id: int,
    provider_user_id: str,
    provider_user_email: str = None,
    provider_user_name: str = None,
    access_token: str = None,
    refresh_token: str = None,
    token_expires_at: datetime = None
) -> OAuth2User:
    """Create OAuth2 user association"""
    db_oauth_user = OAuth2User(
        user_id=user_id,
        provider_id=provider_id,
        provider_user_id=provider_user_id,
        provider_user_email=provider_user_email,
        provider_user_name=provider_user_name,
        access_token=access_token,  # Will be encrypted automatically by EncryptedText column
        refresh_token=refresh_token,  # Will be encrypted automatically by EncryptedText column
        token_expires_at=token_expires_at
    )

    db.add(db_oauth_user)
    db.commit()
    db.refresh(db_oauth_user)
    return db_oauth_user

def update_oauth2_tokens(
    db: Session,
    oauth_user: OAuth2User,
    access_token: str = None,
    refresh_token: str = None,
    token_expires_at: datetime = None
):
    """Update OAuth2 tokens for user association"""
    if access_token:
        oauth_user.access_token = access_token  # Will be encrypted automatically by EncryptedText column
    if refresh_token:
        oauth_user.refresh_token = refresh_token  # Will be encrypted automatically by EncryptedText column
    if token_expires_at:
        oauth_user.token_expires_at = token_expires_at

    oauth_user.updated_at = datetime.now(timezone.utc)
    db.commit()

async def get_oauth2_client(provider: OAuth2Provider) -> AsyncOAuth2Client:
    """Create OAuth2 client for provider"""
    # client_secret is automatically decrypted by EncryptedText column
    client_secret = provider.client_secret

    return AsyncOAuth2Client(
        client_id=provider.client_id,
        client_secret=client_secret,
        authorization_endpoint=provider.authorize_url,
        token_endpoint=provider.token_url,
        userinfo_endpoint=provider.userinfo_url,
    )

async def oauth2_authorize_url(provider: OAuth2Provider, redirect_uri: str, state: str) -> str:
    """Generate OAuth2 authorization URL"""
    client = await get_oauth2_client(provider)

    uri, _ = client.create_authorization_url(
        redirect_uri=redirect_uri,
        scope=provider.scope.split(),
        state=state
    )

    return uri

async def oauth2_exchange_code(
    provider: OAuth2Provider,
    code: str,
    redirect_uri: str
) -> dict[str, Any]:
    """Exchange authorization code for tokens"""
    client = await get_oauth2_client(provider)

    try:
        token = await client.fetch_token(
            code=code,
            redirect_uri=redirect_uri
        )
        return token
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=f"OAuth2 token exchange failed: {str(e)}")

async def oauth2_get_user_info(provider: OAuth2Provider, access_token: str) -> dict[str, Any]:
    """Get user info from OAuth2 provider"""
    client = await get_oauth2_client(provider)

    try:
        user_info = await client.userinfo(token={"access_token": access_token})
        return user_info
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=f"Failed to get user info: {str(e)}")

def find_or_create_user_from_oauth2(
    db: Session,
    provider: OAuth2Provider,
    provider_user_id: str,
    user_info: dict[str, Any]
) -> User:
    """Find existing user or create new one from OAuth2 user info"""
    # Check if user already exists with this OAuth2 association
    existing_oauth_user = db.query(OAuth2User).filter(
        OAuth2User.provider_id == provider.id,
        OAuth2User.provider_user_id == provider_user_id
    ).first()

    if existing_oauth_user:
        return db.query(User).filter(User.id == existing_oauth_user.user_id).first()

    # Try to find user by email
    email = user_info.get("email")
    if email:
        existing_user = get_user_by_email(db, email)
        if existing_user:
            # Associate OAuth2 with existing user
            create_oauth2_user_association(
                db=db,
                user_id=existing_user.id,
                provider_id=provider.id,
                provider_user_id=provider_user_id,
                provider_user_email=email,
                provider_user_name=user_info.get("name")
            )
            return existing_user

    # Create new user
    username = user_info.get("preferred_username") or user_info.get("email") or f"oauth2_{provider.name}_{provider_user_id}"
    full_name = user_info.get("name")

    # Ensure username is unique
    base_username = username
    counter = 1
    while get_user_by_username(db, username):
        username = f"{base_username}_{counter}"
        counter += 1

    user_create = UserCreate(
        email=email or f"{username}@oauth2.local",
        username=username,
        full_name=full_name,
        password=secrets.token_urlsafe(32)  # Random password for OAuth2 users
    )

    user = create_user(db, user_create)

    # Create OAuth2 association
    create_oauth2_user_association(
        db=db,
        user_id=user.id,
        provider_id=provider.id,
        provider_user_id=provider_user_id,
        provider_user_email=email,
        provider_user_name=full_name
    )

    return user

# Initialize database
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=db_manager._engine)

# Call init_db when module is imported
init_db()
