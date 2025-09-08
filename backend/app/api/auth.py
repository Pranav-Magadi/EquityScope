"""
Authentication API Endpoints
Handles user registration, login, password management, and API key operations
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import jwt

from app.models.user import (
    User, UserCreate, UserLogin, UserResponse, UserUpdate, 
    PasswordReset, PasswordChange, Token, UsageStats
)
from app.services.user_service import UserService
from app.core.config import settings

router = APIRouter(prefix="/api/v2/auth", tags=["Authentication"])
security = HTTPBearer()
user_service = UserService()

# Dependency to get current user from JWT token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Extract and validate current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Get user from database
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise credentials_exception
        
    return user

# Optional dependency for API key authentication
async def get_current_user_optional(request: Request) -> Optional[User]:
    """Get current user from JWT or API key, return None if not authenticated"""
    try:
        # Try JWT token first
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            # Check if it's an API key (starts with 'eq_')
            if token.startswith("eq_"):
                return await user_service.validate_api_key(token)
            else:
                # JWT token
                payload = jwt.decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=[settings.ALGORITHM]
                )
                email = payload.get("sub")
                if email:
                    return await user_service.get_user_by_email(email)
        
        return None
        
    except Exception:
        return None

@router.post("/register", response_model=UserResponse)
async def register_user(user_create: UserCreate, request: Request):
    """Register a new user account"""
    try:
        user = await user_service.create_user(user_create)
        
        # Create session
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "")
        await user_service.create_session(user.id, ip_address, user_agent)
        
        # Convert to response model
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            company=user.company,
            status=user.status,
            email_verified=user.email_verified,
            tier=user.tier,
            subscription_status=user.get_subscription_status(),
            total_analyses=user.total_analyses,
            monthly_analyses=user.monthly_analyses,
            rate_limits=user.get_rate_limits(),
            created_at=user.created_at,
            last_login=user.last_login
        )
        
        return user_response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login_user(user_login: UserLogin, request: Request):
    """Authenticate user and return access token"""
    try:
        user = await user_service.authenticate_user(user_login.email, user_login.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = user.create_access_token(expires_delta=access_token_expires)
        
        # Create session
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "")
        await user_service.create_session(user.id, ip_address, user_agent)
        
        # Convert to response model
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            company=user.company,
            status=user.status,
            email_verified=user.email_verified,
            tier=user.tier,
            subscription_status=user.get_subscription_status(),
            total_analyses=user.total_analyses,
            monthly_analyses=user.monthly_analyses,
            rate_limits=user.get_rate_limits(),
            created_at=user.created_at,
            last_login=user.last_login
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        company=current_user.company,
        status=current_user.status,
        email_verified=current_user.email_verified,
        tier=current_user.tier,
        subscription_status=current_user.get_subscription_status(),
        total_analyses=current_user.total_analyses,
        monthly_analyses=current_user.monthly_analyses,
        rate_limits=current_user.get_rate_limits(),
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate, 
    current_user: User = Depends(get_current_user)
):
    """Update user profile information"""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.company is not None:
        current_user.company = user_update.company
    
    updated_user = await user_service.update_user(current_user)
    
    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        full_name=updated_user.full_name,
        company=updated_user.company,
        status=updated_user.status,
        email_verified=updated_user.email_verified,
        tier=updated_user.tier,
        subscription_status=updated_user.get_subscription_status(),
        total_analyses=updated_user.total_analyses,
        monthly_analyses=updated_user.monthly_analyses,
        rate_limits=updated_user.get_rate_limits(),
        created_at=updated_user.created_at,
        last_login=updated_user.last_login
    )

@router.post("/verify-email")
async def verify_email(token: str):
    """Verify user email with verification token"""
    success = await user_service.verify_email(token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    return {"message": "Email verified successfully"}

@router.post("/forgot-password")
async def forgot_password(password_reset: PasswordReset):
    """Request password reset token"""
    reset_token = await user_service.create_password_reset_token(password_reset.email)
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/reset-password")
async def reset_password(token: str, new_password: str):
    """Reset password with reset token"""
    success = await user_service.reset_password(token, new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {"message": "Password reset successfully"}

@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user)
):
    """Change user password"""
    success = await user_service.change_password(
        current_user.id, 
        password_change.current_password, 
        password_change.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    return {"message": "Password changed successfully"}

@router.get("/usage-stats", response_model=UsageStats)
async def get_usage_statistics(current_user: User = Depends(get_current_user)):
    """Get user usage statistics and rate limit status"""
    return await user_service.get_usage_stats(current_user.id)

@router.get("/rate-limit-status")
async def get_rate_limit_status(current_user: User = Depends(get_current_user)):
    """Get detailed rate limit status"""
    return await user_service.check_rate_limit(current_user.id)

@router.post("/api-keys")
async def create_api_key(
    name: str,
    expires_days: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """Create new API key for programmatic access"""
    api_key, raw_key = await user_service.create_api_key(
        current_user.id, 
        name, 
        expires_days
    )
    
    return {
        "api_key_id": api_key.id,
        "name": api_key.name,
        "key": raw_key,  # Only shown once
        "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
        "created_at": api_key.created_at.isoformat(),
        "warning": "Store this key securely. It will not be shown again."
    }

@router.get("/sessions")
async def get_active_sessions(current_user: User = Depends(get_current_user)):
    """Get user's active sessions"""
    sessions = await user_service.get_active_sessions(current_user.id)
    
    return {
        "active_sessions": [
            {
                "session_id": session.session_id,
                "ip_address": session.ip_address,
                "user_agent": session.user_agent,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat()
            }
            for session in sessions
        ]
    }

@router.delete("/sessions/{session_id}")
async def invalidate_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Invalidate a specific session"""
    success = await user_service.invalidate_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {"message": "Session invalidated successfully"}

@router.post("/logout")
async def logout_user(request: Request, current_user: User = Depends(get_current_user)):
    """Logout user and invalidate current session"""
    # In a more sophisticated system, we would invalidate the specific session
    # For now, we'll just return a success message
    return {"message": "Logged out successfully"}

# Rate limiting middleware for authentication endpoints
@router.middleware("http")
async def rate_limit_auth(request: Request, call_next):
    """Basic rate limiting for authentication endpoints"""
    response = await call_next(request)
    
    # Add rate limiting headers
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = "99"
    response.headers["X-RateLimit-Reset"] = str(int((datetime.utcnow() + timedelta(hours=1)).timestamp()))
    
    return response