from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

# Import demo data
from ..data.demo_analyses import DEMO_ANALYSES

router = APIRouter(prefix="/api/v2", tags=["Demo Analysis"])
logger = logging.getLogger(__name__)

@router.get("/demo-analyses")
async def get_available_demo_analyses():
    """Get list of available demo analyses"""
    try:
        demo_list = []
        for ticker, data in DEMO_ANALYSES.items():
            demo_list.append({
                "ticker": ticker,
                "companyName": data["companyName"],
                "sector": data["sector"],
                "description": data["description"]
            })
        
        return {
            "demos": demo_list,
            "count": len(demo_list),
            "message": "Available demo analyses for EquityScope v2-optimized"
        }
    except Exception as e:
        logger.error(f"Error fetching demo analyses list: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch demo analyses")

@router.get("/demo-analyses/{ticker}")
async def get_demo_analysis(ticker: str):
    """Get specific demo analysis for a ticker"""
    try:
        if ticker not in DEMO_ANALYSES:
            available_tickers = list(DEMO_ANALYSES.keys())
            raise HTTPException(
                status_code=404, 
                detail=f"Demo analysis not found for {ticker}. Available: {available_tickers}"
            )
        
        demo_data = DEMO_ANALYSES[ticker]
        logger.info(f"Serving demo analysis for {ticker}")
        
        return {
            "ticker": ticker,
            "demo_mode": True,
            "data": demo_data,
            "message": f"Demo analysis for {demo_data['companyName']}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching demo analysis for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch demo analysis for {ticker}")

@router.get("/subscription-plans")
async def get_subscription_plans():
    """Get available subscription plans for EquityScope"""
    try:
        plans = {
            "plans": [
                {
                    "id": "free",
                    "name": "Free",
                    "price": 0,
                    "currency": "INR",
                    "period": "monthly",
                    "features": [
                        "3 DCF analyses per month",
                        "Basic demo mode access",
                        "Educational content",
                        "Simple DCF mode only"
                    ],
                    "limits": {
                        "analyses_per_month": 3,
                        "advanced_features": False,
                        "ai_agentic_mode": False
                    }
                },
                {
                    "id": "professional", 
                    "name": "Professional",
                    "price": 2999,
                    "currency": "INR",
                    "period": "monthly",
                    "features": [
                        "Unlimited DCF analyses",
                        "AI Agentic Mode",
                        "Advanced multi-stage DCF",
                        "Technical analysis",
                        "Investment committee insights",
                        "Real-time data"
                    ],
                    "limits": {
                        "analyses_per_month": -1,
                        "advanced_features": True,
                        "ai_agentic_mode": True
                    }
                },
                {
                    "id": "enterprise",
                    "name": "Enterprise", 
                    "price": 9999,
                    "currency": "INR",
                    "period": "monthly",
                    "features": [
                        "Everything in Professional",
                        "API access",
                        "Custom integrations",
                        "Priority support",
                        "White-label options"
                    ],
                    "limits": {
                        "analyses_per_month": -1,
                        "advanced_features": True,
                        "ai_agentic_mode": True,
                        "api_access": True
                    }
                }
            ]
        }
        
        return plans
    except Exception as e:
        logger.error(f"Error fetching subscription plans: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch subscription plans")