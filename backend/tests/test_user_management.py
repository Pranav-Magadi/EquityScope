"""
Test User Management System
Comprehensive tests for authentication, rate limiting, and user operations
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from app.models.user import (
    User, UserCreate, UserLogin, UserTier, UserStatus,
    PasswordChange, APIKey, SessionData
)
from app.services.user_service import UserService


class TestUserModel:
    """Test User model functionality"""
    
    def test_user_creation(self):
        """Test basic user creation"""
        user = User(
            email="test@example.com",
            hashed_password=User.hash_password("testpassword123"),
            full_name="Test User"
        )
        
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.tier == UserTier.FREE
        assert user.status == UserStatus.PENDING_VERIFICATION
        assert user.total_analyses == 0
        assert user.monthly_analyses == 0
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = User.hash_password(password)
        
        user = User(
            email="test@example.com",
            hashed_password=hashed
        )
        
        assert user.verify_password(password)
        assert not user.verify_password("wrongpassword")
    
    def test_rate_limits_by_tier(self):
        """Test rate limits for different user tiers"""
        # Free tier
        free_user = User(
            email="free@example.com",
            hashed_password="hash",
            tier=UserTier.FREE
        )
        free_limits = free_user.get_rate_limits()
        assert free_limits["analyses_per_hour"] == 5
        assert free_limits["analyses_per_day"] == 20
        assert free_limits["analyses_per_month"] == 100
        
        # Professional tier
        pro_user = User(
            email="pro@example.com",
            hashed_password="hash",
            tier=UserTier.PROFESSIONAL
        )
        pro_limits = pro_user.get_rate_limits()
        assert pro_limits["analyses_per_hour"] == 50
        assert pro_limits["analyses_per_day"] == 200
        assert pro_limits["analyses_per_month"] == 2000
        
        # Enterprise tier
        ent_user = User(
            email="enterprise@example.com",
            hashed_password="hash",
            tier=UserTier.ENTERPRISE
        )
        ent_limits = ent_user.get_rate_limits()
        assert ent_limits["analyses_per_hour"] == 500
        assert ent_limits["analyses_per_day"] == 2000
        assert ent_limits["analyses_per_month"] == 20000
    
    def test_rate_limiting_logic(self):
        """Test rate limiting functionality"""
        user = User(
            email="test@example.com",
            hashed_password="hash",
            tier=UserTier.FREE
        )
        
        # Initially not rate limited
        assert not user.is_rate_limited()
        
        # Simulate hitting rate limit
        user.rate_limit_window_start = datetime.utcnow()
        user.rate_limit_count = 5  # At hourly limit for free tier
        
        assert user.is_rate_limited()
        
        # Test window reset
        user.rate_limit_window_start = datetime.utcnow() - timedelta(hours=2)
        assert not user.is_rate_limited()  # Should reset
    
    def test_subscription_status(self):
        """Test subscription status checking"""
        user = User(
            email="test@example.com",
            hashed_password="hash",
            tier=UserTier.FREE
        )
        
        # Free tier always active
        assert user.is_subscription_active()
        
        # Professional with active subscription
        user.tier = UserTier.PROFESSIONAL
        user.subscription_start = datetime.utcnow() - timedelta(days=30)
        user.subscription_end = datetime.utcnow() + timedelta(days=30)
        assert user.is_subscription_active()
        
        # Expired subscription
        user.subscription_end = datetime.utcnow() - timedelta(days=1)
        assert not user.is_subscription_active()
    
    def test_jwt_token_creation(self):
        """Test JWT token creation"""
        user = User(
            id="test-user-id",
            email="test@example.com",
            hashed_password="hash",
            tier=UserTier.PROFESSIONAL
        )
        
        token = user.create_access_token()
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long
    
    def test_usage_increment(self):
        """Test usage counter increment"""
        user = User(
            email="test@example.com",
            hashed_password="hash"
        )
        
        initial_total = user.total_analyses
        initial_monthly = user.monthly_analyses
        initial_rate_limit = user.rate_limit_count
        
        user.increment_usage()
        
        assert user.total_analyses == initial_total + 1
        assert user.monthly_analyses == initial_monthly + 1
        assert user.rate_limit_count == initial_rate_limit + 1
        assert user.last_analysis is not None


class TestUserService:
    """Test UserService functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def user_service(self, temp_dir):
        """Create UserService with temporary data directory"""
        with patch('app.services.user_service.settings') as mock_settings:
            mock_settings.DATA_DIR = str(temp_dir)
            service = UserService()
            return service
    
    @pytest.mark.asyncio
    async def test_create_user(self, user_service):
        """Test user creation"""
        user_create = UserCreate(
            email="test@example.com",
            password="testpassword123",
            full_name="Test User",
            company="Test Company"
        )
        
        user = await user_service.create_user(user_create)
        
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.company == "Test Company"
        assert user.status == UserStatus.PENDING_VERIFICATION
        assert user.verification_token is not None
    
    @pytest.mark.asyncio
    async def test_create_duplicate_user(self, user_service):
        """Test creating user with duplicate email"""
        user_create = UserCreate(
            email="test@example.com",
            password="testpassword123"
        )
        
        # Create first user
        await user_service.create_user(user_create)
        
        # Try to create duplicate
        with pytest.raises(ValueError, match="Email already registered"):
            await user_service.create_user(user_create)
    
    @pytest.mark.asyncio
    async def test_authenticate_user(self, user_service):
        """Test user authentication"""
        # Create user first
        user_create = UserCreate(
            email="test@example.com",
            password="testpassword123"
        )
        created_user = await user_service.create_user(user_create)
        
        # Authenticate with correct credentials
        user = await user_service.authenticate_user("test@example.com", "testpassword123")
        assert user is not None
        assert user.email == "test@example.com"
        
        # Authenticate with wrong password
        user = await user_service.authenticate_user("test@example.com", "wrongpassword")
        assert user is None
        
        # Authenticate with non-existent email
        user = await user_service.authenticate_user("nonexistent@example.com", "testpassword123")
        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, user_service):
        """Test getting user by ID"""
        # Create user
        user_create = UserCreate(
            email="test@example.com",
            password="testpassword123"
        )
        created_user = await user_service.create_user(user_create)
        
        # Get by ID
        retrieved_user = await user_service.get_user_by_id(created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
        
        # Get non-existent user
        non_existent = await user_service.get_user_by_id("non-existent-id")
        assert non_existent is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, user_service):
        """Test getting user by email"""
        # Create user
        user_create = UserCreate(
            email="test@example.com",
            password="testpassword123"
        )
        created_user = await user_service.create_user(user_create)
        
        # Get by email
        retrieved_user = await user_service.get_user_by_email("test@example.com")
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
        
        # Get non-existent user
        non_existent = await user_service.get_user_by_email("nonexistent@example.com")
        assert non_existent is None
    
    @pytest.mark.asyncio
    async def test_update_user(self, user_service):
        """Test updating user information"""
        # Create user
        user_create = UserCreate(
            email="test@example.com",
            password="testpassword123",
            full_name="Original Name"
        )
        user = await user_service.create_user(user_create)
        
        # Update user
        user.full_name = "Updated Name"
        user.company = "New Company"
        
        updated_user = await user_service.update_user(user)
        
        assert updated_user.full_name == "Updated Name"
        assert updated_user.company == "New Company"
        assert updated_user.updated_at > updated_user.created_at
    
    @pytest.mark.asyncio
    async def test_verify_email(self, user_service):
        """Test email verification"""
        # Create user
        user_create = UserCreate(
            email="test@example.com",
            password="testpassword123"
        )
        user = await user_service.create_user(user_create)
        verification_token = user.verification_token
        
        # Verify email
        success = await user_service.verify_email(verification_token)
        assert success
        
        # Check user status updated
        verified_user = await user_service.get_user_by_email("test@example.com")
        assert verified_user.email_verified
        assert verified_user.status == UserStatus.ACTIVE
        assert verified_user.verification_token is None
        
        # Try invalid token
        success = await user_service.verify_email("invalid-token")
        assert not success
    
    @pytest.mark.asyncio
    async def test_password_reset(self, user_service):
        """Test password reset functionality"""
        # Create user
        user_create = UserCreate(
            email="test@example.com",
            password="originalpassword123"
        )
        await user_service.create_user(user_create)
        
        # Request password reset
        reset_token = await user_service.create_password_reset_token("test@example.com")
        assert reset_token is not None
        
        # Reset password
        new_password = "newpassword123"
        success = await user_service.reset_password(reset_token, new_password)
        assert success
        
        # Test authentication with new password
        user = await user_service.authenticate_user("test@example.com", new_password)
        assert user is not None
        
        # Old password should not work
        user = await user_service.authenticate_user("test@example.com", "originalpassword123")
        assert user is None
    
    @pytest.mark.asyncio
    async def test_change_password(self, user_service):
        """Test password change functionality"""
        # Create user
        user_create = UserCreate(
            email="test@example.com",
            password="originalpassword123"
        )
        user = await user_service.create_user(user_create)
        
        # Change password
        success = await user_service.change_password(
            user.id,
            "originalpassword123",
            "newpassword123"
        )
        assert success
        
        # Test authentication with new password
        auth_user = await user_service.authenticate_user("test@example.com", "newpassword123")
        assert auth_user is not None
        
        # Wrong current password should fail
        success = await user_service.change_password(
            user.id,
            "wrongpassword",
            "anothernewpassword123"
        )
        assert not success
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, user_service):
        """Test rate limiting functionality"""
        # Create user
        user_create = UserCreate(
            email="test@example.com",
            password="testpassword123"
        )
        user = await user_service.create_user(user_create)
        
        # Initially not rate limited
        rate_status = await user_service.check_rate_limit(user.id)
        assert not rate_status["is_rate_limited"]
        assert rate_status["current_usage"] == 0
        assert rate_status["hourly_limit"] == 5  # Free tier
        
        # Record analyses up to limit
        for i in range(5):
            success = await user_service.record_analysis(user.id)
            assert success
        
        # Should be rate limited now
        rate_status = await user_service.check_rate_limit(user.id)
        assert rate_status["is_rate_limited"]
        assert rate_status["current_usage"] == 5
        
        # Further analysis should fail
        success = await user_service.record_analysis(user.id)
        assert not success
    
    @pytest.mark.asyncio
    async def test_upgrade_user_tier(self, user_service):
        """Test user tier upgrade"""
        # Create user
        user_create = UserCreate(
            email="test@example.com",
            password="testpassword123"
        )
        user = await user_service.create_user(user_create)
        
        assert user.tier == UserTier.FREE
        
        # Upgrade to professional
        upgraded_user = await user_service.upgrade_user_tier(
            user.id,
            UserTier.PROFESSIONAL,
            12  # 12 months
        )
        
        assert upgraded_user.tier == UserTier.PROFESSIONAL
        assert upgraded_user.subscription_start is not None
        assert upgraded_user.subscription_end is not None
        
        # Check rate limits changed
        rate_status = await user_service.check_rate_limit(user.id)
        assert rate_status["hourly_limit"] == 50  # Professional tier
    
    @pytest.mark.asyncio
    async def test_api_key_creation(self, user_service):
        """Test API key creation and validation"""
        # Create user
        user_create = UserCreate(
            email="test@example.com",
            password="testpassword123"
        )
        user = await user_service.create_user(user_create)
        
        # Create API key
        api_key, raw_key = await user_service.create_api_key(
            user.id,
            "Test API Key",
            30  # 30 days expiration
        )
        
        assert api_key.user_id == user.id
        assert api_key.name == "Test API Key"
        assert api_key.expires_at is not None
        assert raw_key.startswith("eq_")
        
        # Validate API key
        validated_user = await user_service.validate_api_key(raw_key)
        assert validated_user is not None
        assert validated_user.id == user.id
        
        # Invalid key should return None
        invalid_user = await user_service.validate_api_key("invalid_key")
        assert invalid_user is None
    
    @pytest.mark.asyncio
    async def test_session_management(self, user_service):
        """Test session creation and management"""
        # Create user
        user_create = UserCreate(
            email="test@example.com",
            password="testpassword123"
        )
        user = await user_service.create_user(user_create)
        
        # Create session
        session = await user_service.create_session(
            user.id,
            "192.168.1.1",
            "Mozilla/5.0 Test Browser"
        )
        
        assert session.user_id == user.id
        assert session.ip_address == "192.168.1.1"
        assert session.is_active
        
        # Get active sessions
        sessions = await user_service.get_active_sessions(user.id)
        assert len(sessions) == 1
        assert sessions[0].session_id == session.session_id
        
        # Invalidate session
        success = await user_service.invalidate_session(session.session_id)
        assert success
        
        # Should have no active sessions now
        sessions = await user_service.get_active_sessions(user.id)
        assert len(sessions) == 0
    
    @pytest.mark.asyncio
    async def test_usage_statistics(self, user_service):
        """Test usage statistics"""
        # Create user
        user_create = UserCreate(
            email="test@example.com",
            password="testpassword123"
        )
        user = await user_service.create_user(user_create)
        
        # Record some analyses
        for i in range(3):
            await user_service.record_analysis(user.id)
        
        # Get usage stats
        with patch('app.services.user_service.CacheService') as mock_cache:
            mock_cache.return_value.get_cache_statistics = AsyncMock(return_value={
                "total_cost_saved_usd": 0.60,
                "hit_rate_percentage": 75.0
            })
            
            stats = await user_service.get_usage_statistics(user.id)
            
            assert stats.total_analyses == 3
            assert stats.monthly_analyses == 3
            assert stats.cost_savings["total_saved"] == 0.60
            assert stats.cost_savings["cache_hit_rate"] == 75.0
    
    @pytest.mark.asyncio
    async def test_system_statistics(self, user_service):
        """Test system-wide statistics"""
        # Create multiple users
        for i in range(3):
            user_create = UserCreate(
                email=f"user{i}@example.com",
                password="testpassword123"
            )
            await user_service.create_user(user_create)
        
        # Get system stats
        stats = await user_service.get_system_stats()
        
        assert stats["total_users"] == 3
        assert stats["users_by_tier"]["free"] == 3
        assert stats["users_by_status"]["pending_verification"] == 3
        assert stats["total_analyses"] == 0  # No analyses recorded yet


class TestUserValidation:
    """Test user input validation"""
    
    def test_user_create_validation(self):
        """Test UserCreate model validation"""
        # Valid user creation
        valid_user = UserCreate(
            email="test@example.com",
            password="testpassword123",
            full_name="Test User"
        )
        assert valid_user.email == "test@example.com"
        
        # Invalid email
        with pytest.raises(ValueError):
            UserCreate(
                email="invalid-email",
                password="testpassword123"
            )
        
        # Short password
        with pytest.raises(ValueError):
            UserCreate(
                email="test@example.com",
                password="short"
            )
    
    def test_password_change_validation(self):
        """Test PasswordChange model validation"""
        # Valid password change
        valid_change = PasswordChange(
            current_password="oldpassword123",
            new_password="newpassword123"
        )
        assert valid_change.current_password == "oldpassword123"
        
        # Short new password
        with pytest.raises(ValueError):
            PasswordChange(
                current_password="oldpassword123",
                new_password="short"
            )


class TestApiKeyModel:
    """Test APIKey model functionality"""
    
    def test_api_key_creation(self):
        """Test API key creation"""
        api_key = APIKey(
            user_id="test-user-id",
            name="Test Key",
            key_hash="hashed_key_value"
        )
        
        assert api_key.user_id == "test-user-id"
        assert api_key.name == "Test Key"
        assert api_key.is_active
        assert not api_key.is_expired()
    
    def test_api_key_expiration(self):
        """Test API key expiration"""
        # Expired key
        expired_key = APIKey(
            user_id="test-user-id",
            name="Expired Key",
            key_hash="hashed_key_value",
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        
        assert expired_key.is_expired()
        
        # Active key
        active_key = APIKey(
            user_id="test-user-id",
            name="Active Key",
            key_hash="hashed_key_value",
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        assert not active_key.is_expired()


class TestSessionModel:
    """Test SessionData model functionality"""
    
    def test_session_creation(self):
        """Test session creation"""
        session = SessionData(
            user_id="test-user-id",
            ip_address="192.168.1.1",
            user_agent="Test Browser"
        )
        
        assert session.user_id == "test-user-id"
        assert session.ip_address == "192.168.1.1"
        assert session.is_active
        assert not session.is_expired()
    
    def test_session_expiration(self):
        """Test session expiration"""
        # Create old session
        old_session = SessionData(
            user_id="test-user-id",
            ip_address="192.168.1.1",
            user_agent="Test Browser"
        )
        
        # Manually set old timestamp
        old_session.last_activity = datetime.utcnow() - timedelta(hours=25)
        
        assert old_session.is_expired(timeout_hours=24)
        
        # Recent session
        recent_session = SessionData(
            user_id="test-user-id",
            ip_address="192.168.1.1",
            user_agent="Test Browser"
        )
        
        assert not recent_session.is_expired(timeout_hours=24)
    
    def test_session_activity_update(self):
        """Test session activity update"""
        session = SessionData(
            user_id="test-user-id",
            ip_address="192.168.1.1",
            user_agent="Test Browser"
        )
        
        original_activity = session.last_activity
        session.update_activity()
        
        assert session.last_activity > original_activity


if __name__ == "__main__":
    pytest.main([__file__, "-v"])