"""
Protected Analysis API Endpoints
DCF analysis endpoints with user authentication and rate limiting
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
import json

from app.models.user import User
from app.api.auth import get_current_user, get_current_user_optional
from app.services.user_service import UserService
from app.services.multi_model_dcf import MultiModelDCFService
from app.services.intelligent_cache import intelligent_cache, CacheType

router = APIRouter(prefix="/api/v2", tags=["Protected Analysis"])
user_service = UserService()
dcf_service = MultiModelDCFService()

@router.post("/analyze")
async def analyze_company_authenticated(
    request: Request,
    ticker: str,
    user_assumptions: Optional[Dict[str, Any]] = None,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Comprehensive company analysis with user authentication and rate limiting
    """
    # Handle both authenticated and anonymous users
    if current_user:
        # Check rate limits for authenticated users
        rate_limit_status = await user_service.check_rate_limit(current_user.id)
        if rate_limit_status["is_rate_limited"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Rate limit exceeded",
                    "rate_limit_status": rate_limit_status
                }
            )
        
        # Record analysis for rate limiting
        await user_service.record_analysis(current_user.id)
        user_tier = current_user.tier.value
        user_level = "intermediate"  # Could be determined from user profile
        
    else:
        # Anonymous users get basic rate limiting (IP-based would be implemented here)
        user_tier = "anonymous"
        user_level = "beginner"
    
    try:
        # Check cache first
        cache_key_params = {
            "user_assumptions": user_assumptions,
            "user_tier": user_tier
        }
        
        cached_result = await intelligent_cache.get(
            CacheType.AI_INSIGHTS,
            ticker,
            **cache_key_params
        )
        
        if cached_result:
            # Add user-specific metadata
            cached_result["metadata"] = {
                **cached_result.get("metadata", {}),
                "cached": True,
                "user_tier": user_tier,
                "user_id": current_user.id if current_user else None,
                "rate_limit_status": await user_service.check_rate_limit(current_user.id) if current_user else None
            }
            return cached_result
        
        # Perform fresh analysis
        analysis_result = await dcf_service.comprehensive_analysis(
            ticker=ticker,
            user_assumptions=user_assumptions,
            user_level=user_level
        )
        
        # Add user-specific metadata
        analysis_result["metadata"] = {
            **analysis_result.get("metadata", {}),
            "cached": False,
            "user_tier": user_tier,
            "user_id": current_user.id if current_user else None,
            "analysis_timestamp": "utcnow().isoformat()",
            "rate_limit_status": await user_service.check_rate_limit(current_user.id) if current_user else None
        }
        
        # Cache the result
        await intelligent_cache.set(
            CacheType.AI_INSIGHTS,
            ticker,
            analysis_result,
            **cache_key_params
        )
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/multi-stage-dcf")
async def multi_stage_dcf_authenticated(
    ticker: str,
    mode: Optional[str] = None,
    user_level: str = "intermediate",
    user_assumptions: Optional[Dict[str, Any]] = None,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    10-year multi-stage DCF analysis with authentication and rate limiting
    """
    # Handle rate limiting
    if current_user:
        rate_limit_status = await user_service.check_rate_limit(current_user.id)
        if rate_limit_status["is_rate_limited"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Rate limit exceeded",
                    "rate_limit_status": rate_limit_status
                }
            )
        await user_service.record_analysis(current_user.id)
        
    try:
        # Check cache
        cache_params = {
            "mode": mode,
            "user_level": user_level,
            "user_assumptions": user_assumptions
        }
        
        cached_result = await intelligent_cache.get(
            CacheType.AI_INSIGHTS,
            f"dcf_{ticker}",
            **cache_params
        )
        
        if cached_result:
            return cached_result
        
        # Perform DCF analysis
        dcf_result = await dcf_service.multi_stage_dcf_analysis(
            ticker=ticker,
            mode=mode,
            user_level=user_level,
            user_assumptions=user_assumptions
        )
        
        # Cache result
        await intelligent_cache.set(
            CacheType.AI_INSIGHTS,
            f"dcf_{ticker}",
            dcf_result,
            **cache_params
        )
        
        return dcf_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DCF analysis failed: {str(e)}"
        )

@router.post("/mode-recommendation")
async def get_mode_recommendation_authenticated(
    ticker: str,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get DCF mode recommendation with caching
    """
    try:
        # Check cache
        cached_result = await intelligent_cache.get(
            CacheType.MODEL_RECOMMENDATIONS,
            ticker
        )
        
        if cached_result:
            return cached_result
        
        # Get fresh recommendation
        recommendation = await dcf_service.get_mode_recommendation(ticker)
        
        # Cache result
        await intelligent_cache.set(
            CacheType.MODEL_RECOMMENDATIONS,
            ticker,
            recommendation
        )
        
        return recommendation
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mode recommendation failed: {str(e)}"
        )

@router.get("/demo-analyses/{ticker}")
async def get_demo_analysis(ticker: str):
    """
    Get pre-built demo analysis (no authentication required)
    """
    try:
        # Import demo data
        from app.data.demo_analyses import DEMO_ANALYSES
        
        if ticker not in DEMO_ANALYSES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Demo analysis not available for {ticker}"
            )
        
        return DEMO_ANALYSES[ticker]
        
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Demo analyses not available"
        )

@router.get("/demo-analyses")
async def list_demo_analyses():
    """
    List available demo analyses
    """
    try:
        from app.data.demo_analyses import DEMO_ANALYSES
        
        return {
            "available_demos": [
                {
                    "ticker": ticker,
                    "company_name": data["companyName"],
                    "sector": data["sector"],
                    "description": data["description"],
                    "difficulty": "beginner" if ticker == "TCS.NS" else "intermediate" if ticker == "HDFCBANK.NS" else "advanced"
                }
                for ticker, data in DEMO_ANALYSES.items()
            ]
        }
        
    except ImportError:
        return {"available_demos": []}

@router.get("/user-dashboard")
async def get_user_dashboard(current_user: User = Depends(get_current_user)):
    """
    Get personalized user dashboard with usage stats and recommendations
    """
    try:
        # Get usage statistics
        usage_stats = await user_service.get_usage_stats(current_user.id)
        
        # Get cache statistics for cost savings
        cache_stats = await intelligent_cache.get_cache_stats()
        
        # Recent analyses (would be tracked in a real system)
        recent_analyses = []  # Placeholder
        
        # Personalized recommendations based on usage
        recommendations = {
            "suggested_companies": ["TCS.NS", "RELIANCE.NS", "HDFCBANK.NS"],
            "educational_content": [
                "Try the demo mode to learn DCF fundamentals",
                "Explore the 10-year multi-stage DCF system",
                "Understanding 'What This Means' sections"
            ],
            "subscription_suggestions": []
        }
        
        # Add subscription suggestions for free users
        if current_user.tier.value == "free":
            rate_limit_status = await user_service.check_rate_limit(current_user.id)
            if rate_limit_status["monthly_usage"] > 80:  # Near monthly limit
                recommendations["subscription_suggestions"].append(
                    "Consider upgrading to Professional for unlimited analyses"
                )
        
        return {
            "user_info": {
                "name": current_user.full_name or current_user.email,
                "tier": current_user.tier.value,
                "member_since": current_user.created_at.isoformat()
            },
            "usage_statistics": usage_stats,
            "cache_performance": {
                "total_cost_saved": cache_stats["cache_statistics"]["total_cost_saved_usd"],
                "hit_rate": cache_stats["cache_statistics"]["hit_rate_percentage"]
            },
            "recent_analyses": recent_analyses,
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard data failed: {str(e)}"
        )

@router.get("/subscription-plans")
async def get_subscription_plans():
    """
    Get available subscription plans and features
    """
    return {
        "plans": {
            "free": {
                "name": "Free",
                "price": 0,
                "currency": "USD",
                "billing_period": "month",
                "features": [
                    "5 analyses per hour",
                    "20 analyses per day", 
                    "100 analyses per month",
                    "Basic DCF analysis",
                    "Demo mode access",
                    "Email support"
                ],
                "rate_limits": {
                    "analyses_per_hour": 5,
                    "analyses_per_day": 20,
                    "analyses_per_month": 100
                }
            },
            "professional": {
                "name": "Professional",
                "price": 29,
                "currency": "USD",
                "billing_period": "month",
                "features": [
                    "50 analyses per hour",
                    "200 analyses per day",
                    "2,000 analyses per month",
                    "Advanced 10-year DCF analysis",
                    "All educational content",
                    "Priority email support",
                    "API access",
                    "Custom assumptions"
                ],
                "rate_limits": {
                    "analyses_per_hour": 50,
                    "analyses_per_day": 200,
                    "analyses_per_month": 2000
                }
            },
            "enterprise": {
                "name": "Enterprise",
                "price": 99,
                "currency": "USD", 
                "billing_period": "month",
                "features": [
                    "500 analyses per hour",
                    "2,000 analyses per day",
                    "20,000 analyses per month",
                    "All DCF modes and features",
                    "White-label options",
                    "Dedicated support",
                    "Advanced API access",
                    "Custom integrations",
                    "Team management"
                ],
                "rate_limits": {
                    "analyses_per_hour": 500,
                    "analyses_per_day": 2000,
                    "analyses_per_month": 20000
                }
            }
        }
    }

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    System health check
    """
    try:
        # Check database connectivity (file system)
        system_stats = await user_service.get_system_stats()
        
        # Check cache system
        cache_stats = await intelligent_cache.get_cache_stats()
        
        return {
            "status": "healthy",
            "timestamp": "utcnow().isoformat()",
            "system_stats": system_stats,
            "cache_stats": cache_stats["cache_statistics"],
            "version": "2.0.0"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"System unhealthy: {str(e)}"
        )