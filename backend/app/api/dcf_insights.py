"""
DCF AI Insights API Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import logging

from ..services.dcf_ai_insights_service import dcf_ai_insights_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dcf", tags=["DCF AI Insights"])


@router.post("/insights/{ticker}")
async def get_dcf_insights(
    ticker: str,
    dcf_data: Dict[str, Any],
    force_refresh: bool = Query(False, description="Force refresh of cached insights")
):
    """
    Generate AI insights for DCF valuation results
    
    Expected dcf_data structure:
    {
        "dcf_result": {
            "fairValue": float,
            "currentPrice": float, 
            "upside": float,
            "confidence": float,
            "method": str
        },
        "assumptions": {
            "wacc": float,
            "revenue_growth_rate": float,
            "terminal_growth_rate": float,
            ...
        },
        "company_data": {
            "name": str,
            "sector": str,
            "market_cap": float
        }
    }
    """
    
    try:
        logger.info(f"Generating DCF insights for {ticker}")
        
        # Validate input data
        if not dcf_data or 'dcf_result' not in dcf_data:
            raise HTTPException(
                status_code=400,
                detail="Missing required DCF result data"
            )
        
        dcf_result = dcf_data.get('dcf_result', {})
        assumptions = dcf_data.get('assumptions', {})
        company_data = dcf_data.get('company_data', {})
        
        # Generate insights
        insights = await dcf_ai_insights_service.generate_dcf_insights(
            ticker=ticker.upper(),
            dcf_result=dcf_result,
            assumptions=assumptions,
            company_data=company_data
        )
        
        return {
            "ticker": ticker.upper(),
            "insights": insights,
            "cached": not force_refresh,
            "api_version": "2.0.0"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating DCF insights for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate DCF insights: {str(e)}"
        )