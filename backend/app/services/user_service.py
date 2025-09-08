"""
User Management Service
Handles user authentication, registration, and database operations
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path
import secrets
import uuid

from app.models.user import (
    User, UserCreate, UserLogin, UserTier, UserStatus, 
    APIKey, SessionData, UsageStats
)
from app.core.config import settings
from app.services.cache_service import CacheService

class UserService:
    """Comprehensive user management service"""
    
    def __init__(self):
        """Initialize user service with file-based storage"""
        self.data_dir = Path(settings.DATA_DIR) / "users"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.users_file = self.data_dir / "users.json"
        self.sessions_file = self.data_dir / "sessions.json"
        self.api_keys_file = self.data_dir / "api_keys.json"
        
        # Initialize files if they don't exist
        for file_path in [self.users_file, self.sessions_file, self.api_keys_file]:
            if not file_path.exists():
                file_path.write_text("[]")
        
        self.cache_service = CacheService()
    
    def _load_users(self) -> List[Dict[str, Any]]:
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_users(self, users: List[Dict[str, Any]]):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2, default=str)
    
    def _load_sessions(self) -> List[Dict[str, Any]]:
        """Load sessions from JSON file"""
        try:
            with open(self.sessions_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_sessions(self, sessions: List[Dict[str, Any]]):
        """Save sessions to JSON file"""
        with open(self.sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2, default=str)
    
    def _load_api_keys(self) -> List[Dict[str, Any]]:
        """Load API keys from JSON file"""
        try:
            with open(self.api_keys_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_api_keys(self, api_keys: List[Dict[str, Any]]):
        """Save API keys to JSON file"""
        with open(self.api_keys_file, 'w') as f:
            json.dump(api_keys, f, indent=2, default=str)
    
    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user account"""
        users = self._load_users()
        
        # Check if email already exists
        if any(u["email"] == user_create.email for u in users):
            raise ValueError("Email already registered")
        
        # Create verification token
        verification_token = secrets.token_urlsafe(32)
        
        # Create user
        user = User(
            email=user_create.email,
            hashed_password=User.hash_password(user_create.password),
            full_name=user_create.full_name,
            company=user_create.company,
            verification_token=verification_token,
            status=UserStatus.PENDING_VERIFICATION
        )
        
        # Add to users list
        user_dict = user.dict()
        users.append(user_dict)
        self._save_users(users)
        
        # TODO: Send verification email
        
        return user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        users = self._load_users()
        
        for user_data in users:
            if user_data["email"] == email:
                user = User(**user_data)
                if user.verify_password(password):
                    if user.status != UserStatus.ACTIVE and user.status != UserStatus.PENDING_VERIFICATION:
                        raise ValueError(f"Account is {user.status.value}")
                    
                    # Update last login
                    user.last_login = datetime.utcnow()
                    await self.update_user(user)
                    
                    return user
                break
        
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        users = self._load_users()
        
        for user_data in users:
            if user_data["id"] == user_id:
                return User(**user_data)
        
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        users = self._load_users()
        
        for user_data in users:
            if user_data["email"] == email:
                return User(**user_data)
        
        return None
    
    async def update_user(self, user: User) -> User:
        """Update user information"""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data["id"] == user.id:
                user.updated_at = datetime.utcnow()
                users[i] = user.dict()
                self._save_users(users)
                return user
        
        raise ValueError("User not found")
    
    async def verify_email(self, token: str) -> bool:
        """Verify user email with token"""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("verification_token") == token:
                users[i]["email_verified"] = True
                users[i]["status"] = UserStatus.ACTIVE.value
                users[i]["verification_token"] = None
                users[i]["updated_at"] = datetime.utcnow().isoformat()
                self._save_users(users)
                return True
        
        return False
    
    async def create_password_reset_token(self, email: str) -> Optional[str]:
        """Create password reset token"""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        reset_token = secrets.token_urlsafe(32)
        # Store reset token with expiration (would be in database in production)
        # For now, we'll use the verification_token field
        user.verification_token = reset_token
        await self.update_user(user)
        
        # TODO: Send password reset email
        
        return reset_token
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password with token"""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("verification_token") == token:
                users[i]["hashed_password"] = User.hash_password(new_password)
                users[i]["verification_token"] = None
                users[i]["updated_at"] = datetime.utcnow().isoformat()
                self._save_users(users)
                return True
        
        return False
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        if not user.verify_password(current_password):
            return False
        
        user.hashed_password = User.hash_password(new_password)
        await self.update_user(user)
        return True
    
    async def upgrade_user_tier(self, user_id: str, new_tier: UserTier, 
                               subscription_months: int = 12) -> User:
        """Upgrade user subscription tier"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.tier = new_tier
        user.subscription_start = datetime.utcnow()
        user.subscription_end = datetime.utcnow() + timedelta(days=30 * subscription_months)
        
        await self.update_user(user)
        return user
    
    async def check_rate_limit(self, user_id: str) -> Dict[str, Any]:
        """Check user rate limit status"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        limits = user.get_rate_limits()
        is_limited = user.is_rate_limited()
        
        # Calculate reset time
        reset_time = None
        if user.rate_limit_window_start:
            reset_time = user.rate_limit_window_start + timedelta(hours=1)
        
        return {
            "is_rate_limited": is_limited,
            "current_usage": user.rate_limit_count,
            "hourly_limit": limits["analyses_per_hour"],
            "daily_limit": limits["analyses_per_day"],
            "monthly_limit": limits["analyses_per_month"],
            "monthly_usage": user.monthly_analyses,
            "reset_time": reset_time.isoformat() if reset_time else None,
            "tier": user.tier.value
        }
    
    async def record_analysis(self, user_id: str) -> bool:
        """Record an analysis for rate limiting and usage tracking"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        if user.is_rate_limited():
            return False
        
        user.increment_usage()
        await self.update_user(user)
        return True
    
    async def get_usage_stats(self, user_id: str) -> UsageStats:
        """Get user usage statistics"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        rate_limit_status = await self.check_rate_limit(user_id)
        
        # Get cost savings from cache service
        cache_stats = await self.cache_service.get_cache_statistics()
        cost_savings = {
            "total_saved": cache_stats.get("total_cost_saved_usd", 0.0),
            "avg_per_analysis": 0.20,  # Estimated savings per cached analysis
            "cache_hit_rate": cache_stats.get("hit_rate_percentage", 0.0)
        }
        
        return UsageStats(
            total_analyses=user.total_analyses,
            monthly_analyses=user.monthly_analyses,
            last_analysis=user.last_analysis,
            rate_limit_status=rate_limit_status,
            subscription_status=user.get_subscription_status(),
            cost_savings=cost_savings
        )
    
    async def create_api_key(self, user_id: str, name: str, 
                           expires_days: Optional[int] = None) -> tuple[APIKey, str]:
        """Create API key for programmatic access"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Generate API key
        raw_key = f"eq_{secrets.token_urlsafe(32)}"
        key_hash = User.hash_password(raw_key)
        
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        api_key = APIKey(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            expires_at=expires_at
        )
        
        # Save to file
        api_keys = self._load_api_keys()
        api_keys.append(api_key.dict())
        self._save_api_keys(api_keys)
        
        return api_key, raw_key
    
    async def validate_api_key(self, raw_key: str) -> Optional[User]:
        """Validate API key and return associated user"""
        api_keys = self._load_api_keys()
        
        for key_data in api_keys:
            api_key = APIKey(**key_data)
            
            if (api_key.is_active and 
                not api_key.is_expired() and 
                pwd_context.verify(raw_key, api_key.key_hash)):
                
                # Update last used
                api_key.last_used = datetime.utcnow()
                # Save updated API key data (simplified for file storage)
                
                # Get and return user
                return await self.get_user_by_id(api_key.user_id)
        
        return None
    
    async def create_session(self, user_id: str, ip_address: str, 
                           user_agent: str) -> SessionData:
        """Create user session"""
        session = SessionData(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        sessions = self._load_sessions()
        sessions.append(session.dict())
        self._save_sessions(sessions)
        
        return session
    
    async def get_active_sessions(self, user_id: str) -> List[SessionData]:
        """Get active sessions for user"""
        sessions = self._load_sessions()
        active_sessions = []
        
        for session_data in sessions:
            session = SessionData(**session_data)
            if (session.user_id == user_id and 
                session.is_active and 
                not session.is_expired()):
                active_sessions.append(session)
        
        return active_sessions
    
    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a user session"""
        sessions = self._load_sessions()
        
        for i, session_data in enumerate(sessions):
            if session_data["session_id"] == session_id:
                sessions[i]["is_active"] = False
                self._save_sessions(sessions)
                return True
        
        return False
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        sessions = self._load_sessions()
        now = datetime.utcnow()
        
        active_sessions = []
        for session_data in sessions:
            session = SessionData(**session_data)
            if not session.is_expired():
                active_sessions.append(session_data)
        
        if len(active_sessions) != len(sessions):
            self._save_sessions(active_sessions)
    
    async def get_user_list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users (admin function)"""
        users = self._load_users()
        user_objects = [User(**user_data) for user_data in users[skip:skip+limit]]
        return user_objects
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide user statistics"""
        users = self._load_users()
        sessions = self._load_sessions()
        
        # Count by tier
        tier_counts = {tier.value: 0 for tier in UserTier}
        status_counts = {status.value: 0 for status in UserStatus}
        
        total_analyses = 0
        for user_data in users:
            user = User(**user_data)
            tier_counts[user.tier.value] += 1
            status_counts[user.status.value] += 1
            total_analyses += user.total_analyses
        
        # Active sessions
        active_sessions = 0
        for session_data in sessions:
            session = SessionData(**session_data)
            if session.is_active and not session.is_expired():
                active_sessions += 1
        
        return {
            "total_users": len(users),
            "users_by_tier": tier_counts,
            "users_by_status": status_counts,
            "total_analyses": total_analyses,
            "active_sessions": active_sessions
        }

# Import pwd_context for API key validation
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")