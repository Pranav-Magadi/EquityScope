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
    perplexity_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

class ApiKeyStatus(BaseModel):
    kite_configured: bool
    kite_authenticated: bool
    claude_configured: bool
    perplexity_configured: bool
    openai_configured: bool
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
        
        if config.openai_api_key and not config.openai_api_key.startswith('sk-'):
            raise HTTPException(status_code=400, detail="Invalid OpenAI API key format")
        
        # Require at least one AI API key for AI features
        if not config.claude_api_key and not config.perplexity_api_key:
            logger.warning("No AI API keys provided - only quantitative analysis will be available")

        # Store configuration (in production, encrypt sensitive data)
        user_api_keys[user_id] = config
        
        logger.info(f"API keys updated for user {user_id}")
        
        # Determine what features will be available
        ai_features_enabled = bool(config.claude_api_key or config.perplexity_api_key)
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
            # No user config - check environment variables
            return ApiKeyStatus(
                kite_configured=bool(os.getenv("KITE_API_KEY")),
                kite_authenticated=bool(os.getenv("KITE_ACCESS_TOKEN")),
                claude_configured=bool(os.getenv("ANTHROPIC_API_KEY")),
                perplexity_configured=bool(os.getenv("PERPLEXITY_API_KEY")),
                openai_configured=bool(os.getenv("OPENAI_API_KEY"))
            )
        else:
            # Using user-provided keys
            return ApiKeyStatus(
                kite_configured=bool(config.kite_api_key and config.kite_api_secret),
                kite_authenticated=bool(config.kite_access_token),
                claude_configured=bool(config.claude_api_key),
                perplexity_configured=bool(config.perplexity_api_key),
                openai_configured=bool(config.openai_api_key)
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
    """Get API keys for a user, falling back to environment variables."""
    if not user_id:
        user_id = get_current_user_id()
    
    config = user_api_keys.get(user_id)
    
    if not config:
        # Return default environment keys
        return {
            "kite_api_key": os.getenv("KITE_API_KEY"),
            "kite_api_secret": os.getenv("KITE_API_SECRET"),
            "kite_access_token": os.getenv("KITE_ACCESS_TOKEN"),
            "claude_api_key": os.getenv("ANTHROPIC_API_KEY"),
            "perplexity_api_key": os.getenv("PERPLEXITY_API_KEY"),
            "openai_api_key": os.getenv("OPENAI_API_KEY")
        }
    else:
        # Return user-provided keys
        return {
            "kite_api_key": config.kite_api_key,
            "kite_api_secret": config.kite_api_secret,
            "kite_access_token": config.kite_access_token,
            "claude_api_key": config.claude_api_key,
            "perplexity_api_key": config.perplexity_api_key,
            "openai_api_key": config.openai_api_key
        }

@router.get("/deployment-info")
async def get_deployment_info():
    """Get deployment configuration information."""
    return {
        "deployment_mode": "multi-user" if os.getenv("MULTI_USER_MODE") == "true" else "single-user",
        "features": {
            "user_api_keys": True,
            "kite_connect": bool(os.getenv("KITE_API_KEY")) or bool(user_api_keys),
            "openai_integration": False,  # Coming soon
            "real_time_data": True,
            "dcf_valuation": True
        },
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }