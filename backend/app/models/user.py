"""
User Management Models
Comprehensive user system with authentication, subscription tiers, and usage tracking
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
import uuid
import jwt
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserTier(str, Enum):
    """User subscription tiers with different rate limits and features"""
    FREE = "free"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"
    PENDING_VERIFICATION = "pending_verification"

class User(BaseModel):
    """Core user model with authentication and subscription information"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    hashed_password: str
    full_name: Optional[str] = None
    company: Optional[str] = None
    
    # Status and verification
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    email_verified: bool = False
    verification_token: Optional[str] = None
    
    # Subscription information
    tier: UserTier = UserTier.FREE
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
    
    # Usage tracking
    total_analyses: int = 0
    monthly_analyses: int = 0
    last_analysis: Optional[datetime] = None
    
    # Rate limiting
    rate_limit_window_start: Optional[datetime] = None
    rate_limit_count: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password for secure storage"""
        return pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash"""
        return pwd_context.verify(password, self.hashed_password)
    
    def create_access_token(self, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token for authentication"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            "sub": self.email,
            "user_id": self.id,
            "tier": self.tier.value,
            "exp": expire
        }
        
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def get_rate_limits(self) -> Dict[str, int]:
        """Get rate limits based on user tier"""
        limits = {
            UserTier.FREE: {
                "analyses_per_hour": 5,
                "analyses_per_day": 20,
                "analyses_per_month": 100
            },
            UserTier.PROFESSIONAL: {
                "analyses_per_hour": 50,
                "analyses_per_day": 200,
                "analyses_per_month": 2000
            },
            UserTier.ENTERPRISE: {
                "analyses_per_hour": 500,
                "analyses_per_day": 2000,
                "analyses_per_month": 20000
            }
        }
        return limits.get(self.tier, limits[UserTier.FREE])
    
    def is_rate_limited(self) -> bool:
        """Check if user has exceeded rate limits"""
        limits = self.get_rate_limits()
        now = datetime.utcnow()
        
        # Reset rate limit window if it's been more than an hour
        if (self.rate_limit_window_start is None or 
            now - self.rate_limit_window_start > timedelta(hours=1)):
            self.rate_limit_window_start = now
            self.rate_limit_count = 0
            return False
        
        return self.rate_limit_count >= limits["analyses_per_hour"]
    
    def increment_usage(self):
        """Increment usage counters"""
        self.total_analyses += 1
        self.monthly_analyses += 1
        self.rate_limit_count += 1
        self.last_analysis = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def is_subscription_active(self) -> bool:
        """Check if user has an active subscription"""
        if self.tier == UserTier.FREE:
            return True
        
        if not self.subscription_end:
            return False
        
        return datetime.utcnow() < self.subscription_end
    
    def get_subscription_status(self) -> Dict[str, Any]:
        """Get detailed subscription status"""
        return {
            "tier": self.tier.value,
            "is_active": self.is_subscription_active(),
            "start_date": self.subscription_start.isoformat() if self.subscription_start else None,
            "end_date": self.subscription_end.isoformat() if self.subscription_end else None,
            "days_remaining": (self.subscription_end - datetime.utcnow()).days if self.subscription_end else None
        }

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: Optional[str] = None
    company: Optional[str] = None

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Schema for user response (excludes sensitive data)"""
    id: str
    email: str
    full_name: Optional[str]
    company: Optional[str]
    status: UserStatus
    email_verified: bool
    tier: UserTier
    subscription_status: Dict[str, Any]
    total_analyses: int
    monthly_analyses: int
    rate_limits: Dict[str, int]
    created_at: datetime
    last_login: Optional[datetime]

class UserUpdate(BaseModel):
    """Schema for user profile updates"""
    full_name: Optional[str] = None
    company: Optional[str] = None

class PasswordReset(BaseModel):
    """Schema for password reset"""
    email: EmailStr

class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8)

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class UsageStats(BaseModel):
    """User usage statistics"""
    total_analyses: int
    monthly_analyses: int
    last_analysis: Optional[datetime]
    rate_limit_status: Dict[str, Any]
    subscription_status: Dict[str, Any]
    cost_savings: Dict[str, float]  # From caching system

class APIKey(BaseModel):
    """API key for programmatic access"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    key_hash: str
    is_active: bool = True
    last_used: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Check if API key is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

class SessionData(BaseModel):
    """User session data for tracking"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    ip_address: str
    user_agent: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def is_expired(self, timeout_hours: int = 24) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() - self.last_activity > timedelta(hours=timeout_hours)