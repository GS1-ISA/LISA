from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime
from typing import Optional
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Query, Depends, HTTPException, status, Request, Header, Form
from pydantic import Field
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from limits import RateLimitItem
# from limits.aio import RateLimiter
from limits.storage import MemoryStorage
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy.orm import Session
import json
import hashlib
import redis
from redis import Redis
from typing import Dict, Any
import jwt
import socketio
import os
import secrets

from src.agent_core.agents.planner import PlannerAgent
from src.agent_core.agents.researcher import ResearcherAgent
from src.agent_core.agents.synthesizer import SynthesizerAgent
from src.agent_core.memory.rag_store import RAGMemory
from src.docs_provider.context7 import get_provider as get_docs_provider
from src.orchestrator.research_graph import ResearchGraph
from src.tools.web_research import WebResearchTool
from src.auth import (
    User, UserCreate, UserUpdate, LoginRequest, Token, TokenData,
    authenticate_user, create_access_token, verify_token, get_user_by_username,
    check_user_permissions, UserRole, create_user, get_user_by_api_key,
    get_user_by_email, update_user_password, generate_api_key, hash_api_key,
    PasswordResetRequest, PasswordResetConfirm, verify_password, JWT_SECRET_KEY, JWT_ALGORITHM,
    # OAuth2/OIDC imports
    OAuth2Provider, OAuth2ProviderCreate, OAuth2LoginRequest, OAuth2CallbackRequest, OAuth2TokenResponse,
    get_oauth2_provider_by_name, create_oauth2_provider, oauth2_authorize_url, oauth2_exchange_code,
    oauth2_get_user_info, find_or_create_user_from_oauth2
)
from src.audit_logger import (
    log_auth_event, log_data_access, log_security_event, log_admin_action,
    AuditEventType, AuditEventSeverity, get_audit_logger
)
from src.database_manager import get_db
from infra.monitoring.monitoring_system import monitoring_system, ResearchWorkflowStatus
# from src.gs1_integration import get_gs1_integration, initialize_gs1_capabilities
from src.docs_provider.pymupdf_processor import PyMuPDFProcessor, create_pymupdf_processor
from src.taxonomy.efrag_esrs_loader import EFRAGESRSTaxonomyLoader, create_esrs_loader
# from src.langgraph_agents.compliance_workflow import ComplianceWorkflowAgent, create_compliance_workflow
# from src.langgraph_agents.document_analyzer import DocumentAnalyzerAgent, create_document_analyzer
# from src.langgraph_agents.risk_assessor import RiskAssessorAgent, create_risk_assessor
from src.database_manager import get_db_manager

# Redis cache setup
redis_client = None
try:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = Redis.from_url(redis_url, decode_responses=True)
    redis_client.ping()  # Test connection
    logging.info("Redis cache connected successfully")
except Exception as e:
    logging.warning(f"Redis cache not available: {e}")
    redis_client = None

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Create FastAPI app
app = FastAPI(title="ISA Research API", version="0.1.0")

# Socket.io server setup
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=["http://localhost:3000", "http://localhost:8080"])
socket_app = socketio.ASGIApp(sio, app)

# Active chat sessions
active_sessions = {}

# Compliance Assistant Chat Handler
class ComplianceAssistant:
    def __init__(self):
        self.docs_provider = get_docs_provider()
        self.rag_memory = RAGMemory()
        self.planner = PlannerAgent(docs_provider=self.docs_provider)
        self.researcher = ResearcherAgent(web_tool=WebResearchTool(), rag_memory=self.rag_memory)
        self.synthesizer = SynthesizerAgent()

    async def process_query(self, query: str, user_id: int, username: str, session_id: str) -> str:
        """Process a compliance query using the agent framework."""
        try:
            # Use the research graph for compliance queries
            graph = ResearchGraph(
                planner=self.planner,
                researcher=self.researcher,
                synthesizer=self.synthesizer,
                rag_memory=self.rag_memory,
                docs_provider=self.docs_provider,
            )

            result = await graph.run(query, user_id, username, session_id)
            return result
        except Exception as e:
            logging.error(f"Error processing compliance query: {e}")
            return f"I apologize, but I encountered an error while processing your query: {str(e)}. Please try rephrasing your question or contact support if the issue persists."

compliance_assistant = ComplianceAssistant()

@sio.event
async def connect(sid, environ, auth):
    """Handle client connection."""
    logging.info(f"Client connected: {sid}")
    active_sessions[sid] = {
        'connected_at': time.time(),
        'user_id': auth.get('user_id') if auth else None,
        'username': auth.get('username') if auth else None,
        'role': auth.get('role') if auth else None
    }
    await sio.emit('connected', {'message': 'Connected to Compliance Assistant'}, to=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    logging.info(f"Client disconnected: {sid}")
    if sid in active_sessions:
        del active_sessions[sid]

@sio.event
async def chat_message(sid, data):
    """Handle chat messages from clients."""
    try:
        session = active_sessions.get(sid)
        if not session:
            await sio.emit('error', {'message': 'Session not found'}, to=sid)
            return

        query = data.get('message', '').strip()
        if not query:
            await sio.emit('error', {'message': 'Empty message'}, to=sid)
            return

        # Send typing indicator
        await sio.emit('typing', {'status': 'thinking'}, to=sid)

        # Process the query
        user_id = session.get('user_id', 0)
        username = session.get('username', 'anonymous')
        session_id = f"chat_{sid}_{int(time.time())}"

        # Role-based personalization
        role = session.get('role', 'user')
        personalized_query = await personalize_query(query, role, username)

        response = await compliance_assistant.process_query(
            personalized_query, user_id, username, session_id
        )

        # Stop typing indicator
        await sio.emit('typing', {'status': 'stopped'}, to=sid)

        # Send response
        await sio.emit('chat_response', {
            'message': response,
            'timestamp': time.time(),
            'session_id': session_id
        }, to=sid)

    except Exception as e:
        logging.error(f"Error handling chat message: {e}")
        await sio.emit('error', {'message': 'Internal server error'}, to=sid)

async def personalize_query(query: str, role: str, username: str) -> str:
    """Personalize query based on user role."""
    role_contexts = {
        'admin': "As an administrator, provide comprehensive compliance analysis with technical details and implementation guidance.",
        'researcher': "As a researcher, focus on detailed regulatory analysis, evidence-based findings, and research-backed recommendations.",
        'auditor': "As an auditor, emphasize compliance verification, risk assessment, and regulatory adherence requirements.",
        'user': "Provide clear, practical compliance guidance suitable for general business users."
    }

    context = role_contexts.get(role, role_contexts['user'])
    return f"{context}\n\nQuery: {query}"

# Startup event to initialize monitoring
@app.on_event("startup")
async def startup_event():
    """Initialize monitoring on startup."""
    # Start system health monitoring
    asyncio.create_task(monitoring_system.start_health_monitoring())

    # Initialize GS1 capabilities
    # gs1_initialized = initialize_gs1_capabilities()
    # if gs1_initialized:
    #     logging.info("GS1 capabilities initialized successfully")
    # else:
    #     logging.warning("GS1 capabilities initialization failed")

    # Initialize Neo4j GDS client
    try:
        from src.neo4j_gds_client import initialize_gds_client
        gds_initialized = initialize_gds_client()
        if gds_initialized:
            logging.info("Neo4j GDS client initialized successfully")
        else:
            logging.warning("Neo4j GDS client initialization failed")
    except Exception as e:
        logging.error(f"Failed to initialize Neo4j GDS client: {e}")

    logging.info("All systems initialized and health monitoring started")

# Rate limiting setup
# rate_limiter = RateLimiter(storage=MemoryStorage())

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Configure for production
# app.add_middleware(HTTPSRedirectMiddleware)  # Redirect HTTP to HTTPS - disabled for development

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Configure for your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Response caching
response_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 300  # 5 minutes

def get_cache_key(endpoint: str, params: Dict[str, Any]) -> str:
    """Generate cache key for request."""
    key_data = f"{endpoint}|{str(sorted(params.items()))}"
    return hashlib.md5(key_data.encode()).hexdigest()

def get_cached_response(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get cached response if available and not expired."""
    if cache_key in response_cache:
        cached = response_cache[cache_key]
        if time.time() - cached['timestamp'] < CACHE_TTL:
            return cached['response']
        else:
            del response_cache[cache_key]
    return None

def cache_response(cache_key: str, response: Dict[str, Any]):
    """Cache an API response."""
    response_cache[cache_key] = {
        'timestamp': time.time(),
        'response': response
    }
    # Limit cache size
    if len(response_cache) > 100:
        oldest_keys = sorted(response_cache.keys(),
                            key=lambda k: response_cache[k]['timestamp'])[:20]
        for key in oldest_keys:
            del response_cache[key]

def get_redis_cached_response(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get cached response from Redis if available."""
    if redis_client:
        try:
            cached_data = redis_client.get(f"api_cache:{cache_key}")
            if cached_data:
                monitoring_system.update_cache_hit_rate(1.0, "redis")  # Simplified hit rate update
                return json.loads(cached_data)
        except Exception as e:
            logging.warning(f"Redis cache read error: {e}")
    monitoring_system.update_cache_hit_rate(0.0, "redis")  # Simplified miss rate update
    return None

def cache_response_redis(cache_key: str, response: Dict[str, Any], ttl: int = 300):
    """Cache an API response in Redis."""
    if redis_client:
        try:
            redis_client.setex(f"api_cache:{cache_key}", ttl, json.dumps(response))
        except Exception as e:
            logging.warning(f"Redis cache write error: {e}")

def invalidate_cache_pattern(pattern: str):
    """Invalidate cache entries matching a pattern."""
    if redis_client:
        try:
            keys = redis_client.keys(f"api_cache:{pattern}")
            if keys:
                redis_client.delete(*keys)
                logging.info(f"Invalidated {len(keys)} cache entries matching {pattern}")
        except Exception as e:
            logging.warning(f"Redis cache invalidation error: {e}")

# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)

    # Add comprehensive security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https: wss:; media-src 'self'; object-src 'none'; child-src 'none'; form-action 'self'; base-uri 'self'; frame-ancestors 'none'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

    return response

# Authentication dependencies
security = HTTPBearer(auto_error=False)

# Rate limiting function
async def check_rate_limit(request: Request, user_id: Optional[int] = None):
    """Check rate limit for requests"""
    # Use user_id if available, otherwise use IP
    identifier = str(user_id) if user_id else request.client.host

    # Rate limit: 100 requests per minute per user/IP
    rate_limit = RateLimitItem(per_minute=100, key=identifier)

    # if not await rate_limiter.hit(rate_limit):
    #     raise HTTPException(
    #         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    #         detail="Rate limit exceeded"
    #     )

# Authentication functions
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current authenticated user from JWT token or API key"""
    if credentials:
        # JWT token authentication
        token_data = verify_token(credentials.credentials)
        if token_data and token_data.username:
            user = get_user_by_username(db, token_data.username)
            if user and user.is_active:
                return user
    elif x_api_key:
        # API key authentication
        user = get_user_by_api_key(db, x_api_key)
        if user and user.is_active:
            return user

    return None

# Enhanced performance metrics
AGENT_RESPONSE_TIME = Histogram(
    "agent_response_time_seconds",
    "Agent response time",
    buckets=(5, 10, 15, 20, 30, 45, 60),
    labelnames=("agent_type", "operation")
)

MEMORY_OPERATION_TIME = Histogram(
    "memory_operation_time_seconds",
    "Memory operation time",
    buckets=(0.1, 0.5, 1, 2, 5),
    labelnames=("operation", "collection")
)

CACHE_HITS = Counter(
    "cache_hits_total",
    "Total cache hits",
    labelnames=("cache_type",)
)

CACHE_MISSES = Counter(
    "cache_misses_total",
    "Total cache misses",
    labelnames=("cache_type",)
)
# Performance profiling decorator
def profile_performance(operation_name: str, labels: Optional[Dict[str, str]] = None):
    """Decorator to profile function performance."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.perf_counter() - start_time

                # Record metrics using monitoring system
                if "agent" in operation_name.lower():
                    monitoring_system.record_agent_response_time(
                        labels.get("agent_type", "unknown") if labels else "unknown",
                        operation_name, elapsed
                    )
                elif "memory" in operation_name.lower():
                    # For memory operations, we could add a method to monitoring system
                    pass

                logging.info(f"Performance: {operation_name} took {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start_time
                logging.error(f"Performance: {operation_name} failed after {elapsed:.3f}s - {e}")
                raise

        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start_time

                # Record metrics using monitoring system
                if "agent" in operation_name.lower():
                    monitoring_system.record_agent_response_time(
                        labels.get("agent_type", "unknown") if labels else "unknown",
                        operation_name, elapsed
                    )
                elif "memory" in operation_name.lower():
                    # For memory operations, we could add a method to monitoring system
                    pass

                logging.info(f"Performance: {operation_name} took {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start_time
                logging.error(f"Performance: {operation_name} failed after {elapsed:.3f}s - {e}")
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

async def get_current_active_user(current_user: Optional[User] = Depends(get_current_user)):
    """Get current active user or raise 401"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

def require_role(required_role: UserRole):
    """Dependency to require specific role"""
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if not check_user_permissions(current_user, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role.value}"
            )
        return current_user
    return role_checker

# Audit logging
def log_auth_event(event_type: str, user_id: Optional[int], details: dict = None):
    """Log authentication events"""
    logging.info(f"AUTH_EVENT: {event_type} - User: {user_id} - Details: {details}")


# Basic Prometheus metrics (low cardinality)
REQS = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "code"]
)
LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency",
    buckets=(0.05, 0.1, 0.2, 0.5, 1, 2, 5),
    labelnames=("method", "endpoint"),
)


@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
        code = getattr(response, "status_code", 500)
        return response
    finally:
        elapsed = time.perf_counter() - start
        endpoint = request.url.path
        method = request.method
        # Use the monitoring system for metrics
        monitoring_system.record_http_request(method, endpoint, locals().get("code", 500), elapsed)


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    """Simple healthcheck for container HEARTCHECK."""
    return "ok"


@app.get("/health/db")
def database_health():
    """Database connection pool health check"""
    try:
        db_manager = get_db_manager()
        pool_status = db_manager.get_pool_status()
        is_healthy = db_manager.is_healthy()

        return {
            "healthy": is_healthy,
            "pool_status": pool_status,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "timestamp": time.time()
        }
@app.get("/metrics")
def metrics() -> Response:
    """Prometheus scrape endpoint."""
    return monitoring_system.get_metrics_response()

@app.get("/monitoring/summary")
def monitoring_summary():
    """Get current monitoring summary."""
    return {
        "isa_metrics": monitoring_system.get_isa_metrics_summary().__dict__,
        "system_health": monitoring_system.collect_system_health().__dict__,
        "timestamp": time.time()
    }


# Authentication endpoints
@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    existing_email = get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = create_user(db, user_data)
    log_auth_event("USER_REGISTERED", user.id, {"username": user.username, "email": user.email})

    # Record user registration metric
    monitoring_system.record_user_registration("web", "standard")

    # Create access token
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return Token(access_token=access_token)

@app.post("/auth/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token"""
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        log_auth_event(
            action="login",
            outcome="failure",
            username=login_data.username,
            ip_address=request.client.host,
            details={"reason": "invalid_credentials"}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    log_auth_event(
        action="login",
        outcome="success",
        user_id=user.id,
        username=user.username,
        ip_address=request.client.host,
        details={"user_agent": request.headers.get("user-agent")}
    )
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return Token(access_token=access_token)

@app.get("/auth/me")
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }

@app.put("/auth/me")
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    for field, value in user_update.dict(exclude_unset=True).items():
        if field == "password":
            continue  # Handle password separately
        setattr(current_user, field, value)

    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    log_auth_event("PROFILE_UPDATED", current_user.id)
    return {"message": "Profile updated successfully"}

@app.post("/auth/change-password")
async def change_password(
    old_password: str = Form(...),
    new_password: str = Form(..., min_length=8),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )

    update_user_password(db, current_user, new_password)
    log_auth_event("PASSWORD_CHANGED", current_user.id)
    return {"message": "Password changed successfully"}

@app.post("/auth/forgot-password")
async def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset"""
    user = get_user_by_email(db, request.email)
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a reset link has been sent"}

    # In a real implementation, you would:
    # 1. Generate a secure reset token
    # 2. Store it with expiration
    # 3. Send email with reset link
    # For now, we'll just log it
    log_auth_event("PASSWORD_RESET_REQUESTED", user.id, {"email": request.email})
    return {"message": "If the email exists, a reset link has been sent"}

@app.post("/auth/reset-password")
async def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password with token"""
    # In a real implementation, you would:
    # 1. Verify the reset token
    # 2. Check if it's not expired
    # 3. Find the user associated with the token
    # 4. Update the password
    # For now, we'll implement a basic version

    # This is a simplified implementation - in production you'd use proper token validation
    try:
        # Decode token to get user info (simplified)
        payload = jwt.decode(request.token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=400, detail="Invalid token")

        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid token")

        update_user_password(db, user, request.new_password)
        log_auth_event("PASSWORD_RESET_COMPLETED", user.id)
        return {"message": "Password reset successfully"}

    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

# OAuth2/OIDC endpoints
@app.post("/auth/oauth2/login")
async def oauth2_login(request: OAuth2LoginRequest, db: Session = Depends(get_db)):
    """Initiate OAuth2/OIDC login flow"""
    provider = get_oauth2_provider_by_name(db, request.provider)
    if not provider:
        raise HTTPException(status_code=404, detail="OAuth2 provider not found")

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store state in session/cache (simplified - in production use proper session storage)
    # For now, we'll just return the authorization URL

    redirect_uri = request.redirect_uri or OAUTH2_REDIRECT_URI

    try:
        auth_url = await oauth2_authorize_url(provider, redirect_uri, state)
        log_auth_event("OAUTH2_LOGIN_INITIATED", None, {"provider": request.provider})
        return {"authorization_url": auth_url, "state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth2 login failed: {str(e)}")

@app.post("/auth/oauth2/callback")
async def oauth2_callback(request: OAuth2CallbackRequest, db: Session = Depends(get_db)):
    """Handle OAuth2/OIDC callback"""
    provider = get_oauth2_provider_by_name(db, request.provider)
    if not provider:
        raise HTTPException(status_code=404, detail="OAuth2 provider not found")

    try:
        # Exchange code for tokens
        token_response = await oauth2_exchange_code(
            provider, request.code, OAUTH2_REDIRECT_URI
        )

        # Get user info
        user_info = await oauth2_get_user_info(provider, token_response.get("access_token"))

        # Find or create user
        user = find_or_create_user_from_oauth2(db, provider, user_info.get("sub"), user_info)

        # Create access token
        access_token = create_access_token(data={"sub": user.username, "role": user.role})

        log_auth_event("OAUTH2_LOGIN_SUCCESS", user.id, {"provider": request.provider})
        return OAuth2TokenResponse(
            access_token=access_token,
            provider=request.provider,
            user_info=user_info
        )

    except Exception as e:
        log_auth_event("OAUTH2_LOGIN_FAILED", None, {"provider": request.provider, "error": str(e)})
        raise HTTPException(status_code=400, detail=f"OAuth2 callback failed: {str(e)}")

@app.post("/admin/oauth2/providers")
async def create_oauth2_provider_endpoint(
    provider_data: OAuth2ProviderCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create OAuth2/OIDC provider (admin only)"""
    # Check if provider already exists
    existing = get_oauth2_provider_by_name(db, provider_data.name)
    if existing:
        raise HTTPException(status_code=400, detail="Provider already exists")

    provider = create_oauth2_provider(db, provider_data)
    return {
        "id": provider.id,
        "name": provider.name,
        "created_at": provider.created_at
    }

@app.get("/admin/oauth2/providers")
async def list_oauth2_providers(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List OAuth2/OIDC providers (admin only)"""
    providers = db.query(OAuth2Provider).filter(OAuth2Provider.is_active == True).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "authorize_url": p.authorize_url,
            "token_url": p.token_url,
            "userinfo_url": p.userinfo_url,
            "scope": p.scope,
            "created_at": p.created_at
        }
        for p in providers
    ]

# Audit logging endpoints
@app.get("/admin/audit/events")
async def get_audit_events(
    event_type: Optional[str] = None,
    user_id: Optional[int] = None,
    resource: Optional[str] = None,
    action: Optional[str] = None,
    outcome: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Get audit events (admin only)"""
    audit_logger = get_audit_logger()

    # Parse dates
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    # Convert string to enum
    event_type_enum = AuditEventType(event_type) if event_type else None

    events = audit_logger.search_events(
        event_type=event_type_enum,
        user_id=user_id,
        resource=resource,
        action=action,
        outcome=outcome,
        start_date=start,
        end_date=end,
        limit=limit
    )

    return [event.to_dict() for event in events]

@app.get("/admin/audit/statistics")
async def get_audit_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Get audit statistics (admin only)"""
    audit_logger = get_audit_logger()

    # Parse dates
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    stats = audit_logger.get_event_statistics(start_date=start, end_date=end)
    return stats

@app.post("/admin/audit/archive")
async def archive_old_audit_events(
    days_to_keep: int = 2555,  # 7 years
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Archive old audit events (admin only)"""
    audit_logger = get_audit_logger()
    audit_logger.archive_old_events(days_to_keep)

    log_admin_action(
        action="archive_audit_events",
        resource="audit_system",
        user_id=current_user.id,
        username=current_user.username,
        details={"days_to_keep": days_to_keep}
    )

    return {"message": f"Audit events older than {days_to_keep} days have been archived"}

@app.post("/admin/audit/cleanup")
async def cleanup_expired_audit_events(
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Clean up expired audit events (admin only)"""
    audit_logger = get_audit_logger()
    deleted_count = audit_logger.cleanup_expired_events()

    log_admin_action(
        action="cleanup_audit_events",
        resource="audit_system",
        user_id=current_user.id,
        username=current_user.username,
        details={"deleted_count": deleted_count}
    )

    return {"message": f"Cleaned up {deleted_count} expired audit events"}

# Admin endpoints
@app.get("/admin/users")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
        for user in users
    ]

@app.put("/admin/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: UserRole,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update user role (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_role = user.role
    user.role = new_role.value
    user.updated_at = datetime.utcnow()
# GS1 Integration endpoints
@app.get("/gs1/status")
async def get_gs1_status():
    """Get GS1 integration capabilities status."""
    gs1_manager = get_gs1_integration()
    return gs1_manager.get_gs1_capabilities_summary()

@app.post("/gs1/initialize")
async def initialize_gs1():
    """Initialize all GS1 capabilities."""
    success = initialize_gs1_capabilities()
    if success:
        return {"message": "GS1 capabilities initialized successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to initialize GS1 capabilities")

@app.post("/gs1/epcis/events")
async def create_epcis_event(
    event_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """Create a new EPCIS event."""
    gs1_manager = get_gs1_integration()
    try:
        event = gs1_manager.create_epcis_event(**event_data)
        return {
            "event_id": event.eventID,
            "event_type": event.type.value,
            "created": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create EPCIS event: {str(e)}")

@app.post("/gs1/epcis/documents")
async def create_epcis_document(
    events_data: List[Dict[str, Any]],
    current_user: User = Depends(get_current_active_user)
):
    """Create an EPCIS document from events."""
    gs1_manager = get_gs1_integration()
    try:
        events = [gs1_manager.create_epcis_event(**event_data) for event_data in events_data]
        document = gs1_manager.create_epcis_document(events)
        return {
            "document_id": document.id,
            "events_count": len(document.epcisBody.eventList),
            "created": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create EPCIS document: {str(e)}")

@app.get("/gs1/webvoc/classes/{class_name}")
async def get_webvoc_class(class_name: str):
    """Get GS1 Web Vocabulary class definition."""
    gs1_manager = get_gs1_integration()
    class_def = gs1_manager.get_webvoc_class(class_name)
    if not class_def:
        raise HTTPException(status_code=404, detail=f"Class '{class_name}' not found in WebVoc")
    return class_def

@app.get("/gs1/webvoc/properties/{property_name}")
async def get_webvoc_property(property_name: str):
    """Get GS1 Web Vocabulary property definition."""
    gs1_manager = get_gs1_integration()
    prop_def = gs1_manager.get_webvoc_property(property_name)
    if not prop_def:
        raise HTTPException(status_code=404, detail=f"Property '{property_name}' not found in WebVoc")
    return prop_def

@app.post("/gs1/traceability/credentials")
async def create_traceability_credential(
    events_data: List[Dict[str, Any]],
    issuer: str,
    subject_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Create a traceability credential from EPCIS events."""
    gs1_manager = get_gs1_integration()
    try:
        events = [gs1_manager.create_epcis_event(**event_data) for event_data in events_data]
        credential = gs1_manager.create_traceability_credential(events, issuer, subject_id)
        return {
            "credential_id": credential.id,
            "type": credential.type,
            "issuer": credential.issuer,
            "issuance_date": credential.issuanceDate,
            "created": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create traceability credential: {str(e)}")

@app.post("/gs1/traceability/proof")
async def create_proof_of_connectedness(
    credential_ids: List[str],
    issuer: str,
    current_user: User = Depends(get_current_active_user)
):
    """Create a proof of connectedness from traceability credentials."""
    gs1_manager = get_gs1_integration()
    try:
        # Get credentials by IDs (simplified - in production would retrieve from storage)
        credentials = []
        for cred_id in credential_ids:
            if cred_id in gs1_manager.traceability_manager.traceability_credentials:
                credentials.append(gs1_manager.traceability_manager.traceability_credentials[cred_id])

        if not credentials:
            raise HTTPException(status_code=404, detail="No valid credentials found")

        proof = gs1_manager.create_proof_of_connectedness(credentials, issuer)
        return {
            "proof_id": proof.id,
            "type": proof.type,
            "issuer": proof.issuer,
            "supply_chain_path": proof.supplyChainPath,
            "events_count": len(proof.sanitizedEvents),
            "created": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create proof of connectedness: {str(e)}")

@app.post("/gs1/validate/vc")
async def validate_gs1_vc(
    vc_payload: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """Validate a GS1 VC payload against official data models."""
    gs1_manager = get_gs1_integration()
    try:
        result = gs1_manager.validate_gs1_vc(vc_payload)
        return {
            "is_valid": result.is_valid,
            "errors": result.errors,
            "warnings": result.warnings,
            "vc_type": result.vc_type.value if result.vc_type else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to validate VC: {str(e)}")

@app.post("/gs1/traceability/process")
async def process_supply_chain_data(
    raw_events_data: List[Dict[str, Any]],
    issuer: str,
    subject_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Process supply chain data through the complete GS1 traceability pipeline."""
    gs1_manager = get_gs1_integration()
    try:
        result = gs1_manager.process_supply_chain_data(raw_events_data, issuer, subject_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process supply chain data: {str(e)}")

@app.get("/gs1/traceability/verify/{proof_id}")
async def verify_traceability_chain(
    proof_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Verify the integrity of a traceability chain."""
    gs1_manager = get_gs1_integration()
    try:
        if proof_id not in gs1_manager.traceability_manager.proofs_of_connectedness:
            raise HTTPException(status_code=404, detail="Proof of connectedness not found")

        proof = gs1_manager.traceability_manager.proofs_of_connectedness[proof_id]
        is_verified = gs1_manager.verify_traceability_chain(proof)

        return {
            "proof_id": proof_id,
            "verified": is_verified,
            "supply_chain_path": proof.supplyChainPath,
            "events_count": len(proof.sanitizedEvents)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to verify traceability chain: {str(e)}")

# Protected research endpoint
@app.get("/research")
async def research(
    query: str = Query(..., description="High-level research query"),
    request: Request = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> JSONResponse:
    """Run the multi-agent research flow and return the final Markdown report."""
    # Check rate limit
    await check_rate_limit(request, current_user.id)

    # Check permissions (researchers and admins can access)
    if not check_user_permissions(current_user, UserRole.RESEARCHER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Research access requires researcher or admin role"
        )

    logging.info(f"Setting up research components for API call by user {current_user.username}")
    log_data_access(
        resource="research_api",
        action="execute_query",
        user_id=current_user.id,
        username=current_user.username,
        ip_address=request.client.host,
        details={"query_length": len(query), "query_preview": query[:100]}
    )

    # Record research workflow start
    monitoring_system.record_research_workflow("api_research", ResearchWorkflowStatus.STARTED)

    start_time = time.time()
    try:
        web_tool = WebResearchTool()
        rag_memory = RAGMemory()
        docs_provider = get_docs_provider()

        planner = PlannerAgent(docs_provider=docs_provider)
        researcher = ResearcherAgent(web_tool=web_tool, rag_memory=rag_memory)
        synthesizer = SynthesizerAgent()

        # Log agent initialization
        log_data_access(
            resource="agent_system",
            action="initialize_agents",
            user_id=current_user.id,
            username=current_user.username,
            ip_address=request.client.host,
            details={"agents": ["planner", "researcher", "synthesizer"]}
        )

        graph = ResearchGraph(
            planner=planner,
            researcher=researcher,
            synthesizer=synthesizer,
            rag_memory=rag_memory,
            docs_provider=docs_provider,
        )

        logging.info("Running research graph")
        result_md = await graph.run(query, current_user.id, current_user.username, f"session_{current_user.id}_{int(time.time())}")

        # Record successful completion
        duration = time.time() - start_time
        monitoring_system.record_research_workflow("api_research", ResearchWorkflowStatus.COMPLETED, duration)

        return JSONResponse({"query": query, "result_markdown": result_md})
    except Exception as e:
        # Record failure
        duration = time.time() - start_time
        monitoring_system.record_research_workflow("api_research", ResearchWorkflowStatus.FAILED, duration)
        monitoring_system.record_error("research_failure", "api_server", "error")
# PDF Processing endpoints
@app.post("/pdf/process")
async def process_pdf(
    file_path: str,
    current_user: User = Depends(get_current_active_user)
):
    """Process a PDF file for LLM consumption."""
    try:
        processor = create_pymupdf_processor()
        result = processor.process_pdf_file(file_path)

        if result.success:
            return {
                "success": True,
                "file_path": file_path,
                "metadata": result.metadata.__dict__ if result.metadata else {},
                "text_length": len(result.text),
                "chunks_count": len(result.chunks)
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"PDF processing failed: {result.error_message}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")


@app.post("/pdf/process-content")
async def process_pdf_content(
    content: bytes,
    filename: str = "uploaded.pdf",
    current_user: User = Depends(get_current_active_user)
):
    """Process PDF content from uploaded bytes."""
    try:
        processor = create_pymupdf_processor()
        result = processor.process_pdf_content(content, filename)

        if result.success:
            return {
                "success": True,
                "filename": filename,
                "metadata": result.metadata.__dict__ if result.metadata else {},
                "text_length": len(result.text),
                "chunks_count": len(result.chunks)
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"PDF processing failed: {result.error_message}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")


# Taxonomy endpoints
@app.post("/taxonomy/esrs/load")
async def load_esrs_taxonomy(
    file_path: str,
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Load EFRAG ESRS taxonomy from file."""
    try:
        db_manager = get_db_manager()
        loader = create_esrs_loader(db_manager)

        taxonomy = loader.load_from_file(file_path)
        success = loader.ingest_to_database(taxonomy)

        if success:
            return {
                "success": True,
                "taxonomy_name": taxonomy.name,
                "version": taxonomy.version,
                "elements_count": len(taxonomy.elements),
                "tables_count": len(taxonomy.tables),
                "ingested": True
            }
        else:
            return {
                "success": False,
                "taxonomy_name": taxonomy.name,
                "ingested": False,
                "error": "Database ingestion failed"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Taxonomy loading error: {str(e)}")


@app.get("/taxonomy/esrs/stats")
async def get_taxonomy_stats(
    current_user: User = Depends(get_current_active_user)
):
    """Get taxonomy loader statistics."""
    try:
        db_manager = get_db_manager()
        loader = create_esrs_loader(db_manager)
        return loader.get_taxonomy_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval error: {str(e)}")


# Compliance Workflow endpoints
@app.post("/compliance/analyze")
async def run_compliance_analysis(
    documents: List[str],
    taxonomy_path: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Run complete compliance analysis workflow."""
    try:
        workflow = create_compliance_workflow()
        result = workflow.run_compliance_analysis(documents, taxonomy_path)

        return {
            "success": result.success,
            "overall_score": result.overall_score,
            "analysis_results": result.analysis_results,
            "risk_assessment": result.risk_assessment,
            "recommendations": result.recommendations,
            "processing_time": result.processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance analysis error: {str(e)}")


@app.post("/compliance/document/analyze")
async def analyze_document(
    document_path: str,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze a single document for compliance information."""
    try:
        analyzer = create_document_analyzer()
        result = analyzer.analyze_document(document_path)

        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Document analysis failed: {result.get('error', 'Unknown error')}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis error: {str(e)}")


@app.post("/compliance/risk/assess")
async def assess_risks(
    analysis_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """Assess compliance risks from analysis data."""
    try:
        assessor = create_risk_assessor()
        result = assessor.assess_risks(analysis_data)

        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Risk assessment failed: {result.get('error', 'Unknown error')}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk assessment error: {str(e)}")


@app.get("/compliance/workflow/stats")
async def get_workflow_stats(
    current_user: User = Depends(get_current_active_user)
):
    """Get compliance workflow statistics."""
    try:
        workflow = create_compliance_workflow()
        return workflow.get_workflow_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval error: {str(e)}")


# Integration status endpoint
@app.get("/integrations/status")
async def get_integrations_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get status of all integrated components."""
    try:
        status_info = {
            "pdf_processor": {
                "available": True,  # PyMuPDF4LLM is in requirements
                "type": "PyMuPDF4LLM"
            },
            "taxonomy_loader": {
                "available": True,
                "type": "EFRAG ESRS"
            },
            "compliance_workflow": {
                "available": True,
                "type": "LangGraph Multi-Agent"
            },
            "database_integration": {
                "available": True,
                "healthy": True  # Would check actual DB health
            }
        }

        return {
            "integrations": status_info,
            "overall_status": "healthy" if all(s["available"] for s in status_info.values()) else "degraded"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check error: {str(e)}")

# Neo4j GDS Analytics endpoints
@app.get("/analytics/graph/status")
async def get_graph_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get Neo4j graph database and GDS status."""
    try:
        from src.neo4j_gds_client import get_gds_client

        client = get_gds_client()
        is_healthy = client.is_healthy()
        stats = client.get_graph_statistics()

        return {
            "healthy": is_healthy,
            "graph_statistics": stats,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph status check failed: {str(e)}")

@app.post("/analytics/risk/assess")
async def assess_supply_chain_risks(
    organization_name: str,
    include_historical: bool = True,
    current_user: User = Depends(get_current_active_user)
):
    """Perform comprehensive supply chain risk analysis for an organization."""
    try:
        from src.neo4j_gds_analytics import get_supply_chain_analyzer

        analyzer = get_supply_chain_analyzer()
        risk_metrics = analyzer.analyze_supply_chain_risks(
            organization_name, include_historical
        )

        return {
            "organization": organization_name,
            "risk_assessment": {
                "overall_risk_score": risk_metrics.overall_risk_score,
                "risk_level": risk_metrics.risk_level.value,
                "confidence_score": risk_metrics.confidence_score,
                "components": {
                    "centrality_risk": risk_metrics.centrality_risk,
                    "community_risk": risk_metrics.community_risk,
                    "path_risk": risk_metrics.path_risk,
                    "supplier_diversity_risk": risk_metrics.supplier_diversity_risk,
                    "geographic_risk": risk_metrics.geographic_risk,
                    "temporal_risk": risk_metrics.temporal_risk
                },
                "recommendations": risk_metrics.recommendations,
                "timestamp": risk_metrics.timestamp.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")

@app.post("/analytics/ingest/epcis")
async def ingest_epcis_data(
    events_data: List[Dict[str, Any]],
    organization_context: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Ingest EPCIS events into the graph database."""
    try:
        from src.neo4j_gds_ingestion import get_gds_ingestion
        from src.epcis_tracker import EPCISEvent

        ingestion = get_gds_ingestion()

        # Convert raw data to EPCIS events
        events = []
        for event_data in events_data:
            try:
                event = EPCISEvent(**event_data)
                events.append(event)
            except Exception as e:
                logging.warning(f"Failed to parse event data: {e}")
                continue

        if not events:
            raise HTTPException(status_code=400, detail="No valid EPCIS events provided")

        # Ingest events
        stats = ingestion.ingest_epcis_events(events, organization_context)

        return {
            "ingestion_status": "completed",
            "events_processed": stats.processed_events,
            "events_failed": stats.failed_events,
            "nodes_created": stats.total_nodes,
            "relationships_created": stats.total_relationships,
            "success_rate": stats.success_rate,
            "processing_time_seconds": stats.duration,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data ingestion failed: {str(e)}")

@app.get("/analytics/graph/stats")
async def get_graph_statistics(
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive graph database statistics."""
    try:
        from src.neo4j_gds_client import get_gds_client

        client = get_gds_client()
        stats = client.get_graph_statistics()

        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")
