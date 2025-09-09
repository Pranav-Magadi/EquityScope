from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])

class ApiKeyConfig(BaseModel):
    kite_api_key: Optional[str] = None
    kite_api_secret: Optional[str] = None
    kite_access_token: Optional[str] = None
    claude_api_key: Optional[str] = None

class ApiKeyStatus(BaseModel):
    kite_configured: bool
    kite_authenticated: bool
    claude_configured: bool
    last_updated: Optional[str] = None

# In-memory storage for user API keys (in production, use secure database)
user_api_keys: Dict[str, ApiKeyConfig] = {}

def get_current_user_id() -> str:
    """Get current user ID. In production, extract from JWT token."""
    return "default_user"  # For demo purposes

@router.post("/api-keys")
async def update_api_keys(
    config: ApiKeyConfig,
    user_id: str = Depends(get_current_user_id)
):
    """Update user's API key configuration."""
    try:
            # Validate API keys if provided
        if config.kite_api_key and len(config.kite_api_key) < 10:
            raise HTTPException(status_code=400, detail="Invalid Kite API key format")
        
        if config.kite_api_secret and len(config.kite_api_secret) < 20:
            raise HTTPException(status_code=400, detail="Invalid Kite API secret format")
        
        # Require Claude API key for AI features
        if not config.claude_api_key:
            logger.warning("No Claude API key provided - only quantitative analysis will be available")

        # Store configuration (in production, encrypt sensitive data)
        user_api_keys[user_id] = config
        
        logger.info(f"API keys updated for user {user_id}")
        logger.info(f"Stored keys: {list(user_api_keys.keys())}")
        logger.info(f"Claude key configured: {bool(config.claude_api_key)}")
        
        # Determine what features will be available
        ai_features_enabled = bool(config.claude_api_key)
        kite_features_enabled = bool(config.kite_api_key and config.kite_api_secret)
        
        return {
            "message": "API keys updated successfully",
            "status": "success",
            "ai_features_enabled": ai_features_enabled,
            "kite_features_enabled": kite_features_enabled,
            "analysis_mode": "ai_enhanced" if ai_features_enabled else "quantitative_only"
        }
        
    except Exception as e:
        logger.error(f"Failed to update API keys for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update API keys")

@router.get("/api-keys/status", response_model=ApiKeyStatus)
async def get_api_key_status(user_id: str = Depends(get_current_user_id)):
    """Get current API key configuration status."""
    try:
        config = user_api_keys.get(user_id)
        
        if not config:
            # No user config - require user to provide keys
            return ApiKeyStatus(
                kite_configured=False,
                kite_authenticated=False,
                claude_configured=False
            )
        else:
            # Using user-provided keys only
            return ApiKeyStatus(
                kite_configured=bool(config.kite_api_key and config.kite_api_secret),
                kite_authenticated=bool(config.kite_access_token),
                claude_configured=bool(config.claude_api_key)
            )
            
    except Exception as e:
        logger.error(f"Failed to get API key status for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get API key status")

@router.delete("/api-keys")
async def reset_api_keys(user_id: str = Depends(get_current_user_id)):
    """Reset user's API keys to default configuration."""
    try:
        if user_id in user_api_keys:
            del user_api_keys[user_id]
        
        logger.info(f"API keys reset to default for user {user_id}")
        
        return {
            "message": "API keys reset to default configuration",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to reset API keys for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset API keys")

def get_user_api_keys(user_id: str = None) -> Dict[str, Any]:
    """Get API keys for a user - only from user settings, no environment fallback."""
    if not user_id:
        user_id = get_current_user_id()
    
    config = user_api_keys.get(user_id)
    
    logger.info(f"Getting API keys for user {user_id}")
    logger.info(f"Available user keys: {list(user_api_keys.keys())}")
    logger.info(f"Config found: {config is not None}")
    
    if not config:
        # Return empty keys - force user to configure in settings panel
        return {
            "kite_api_key": None,
            "kite_api_secret": None,
            "kite_access_token": None,
            "claude_api_key": None
        }
    else:
        # Return user-provided keys only
        return {
            "kite_api_key": config.kite_api_key,
            "kite_api_secret": config.kite_api_secret,
            "kite_access_token": config.kite_access_token,
            "claude_api_key": config.claude_api_key
        }

@router.get("/deployment-info")
async def get_deployment_info():
    """Get deployment configuration information."""
    return {
        "deployment_mode": "multi-user" if os.getenv("MULTI_USER_MODE") == "true" else "single-user",
        "features": {
            "user_api_keys": True,
            "kite_connect": bool(user_api_keys),
            "claude_integration": True,
            "real_time_data": True,
            "dcf_valuation": True
        },
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }