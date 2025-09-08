# EquityScope v3 Summary Engine API
# Based on Architecture Migration Strategy

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import Optional
import logging
from datetime import datetime

from ..models.summary import (
    SummaryResponse, 
    SimpleSummaryResponse, 
    AgenticSummaryResponse,
    SummaryRequest,
    InvestmentLabel,
    FairValueBand
)
from ..services.v3_summary_service import V3SummaryService
from ..services.dcf_service import DCFService

router = APIRouter(prefix="/api/v3", tags=["v3-summary"])
logger = logging.getLogger(__name__)

# Initialize services
summary_service = V3SummaryService()
dcf_service = DCFService()

@router.get("/summary/{ticker}/simple", response_model=SimpleSummaryResponse)
async def get_simple_summary(
    ticker: str,
    force_refresh: bool = Query(False, description="Force refresh of cached analysis")
) -> SimpleSummaryResponse:
    """
    Get rule-based simple mode summary analysis
    
    **Rule-based & formula-driven summaries + templated insight sentences**
    
    - **No LLM inference** - Pure quantitative rules and heuristics
    - **Fast response** - Typically under 5 seconds
    - **Deterministic** - Consistent results for same input data
    - **Sector-aware** - Different rules for different sectors
    """
    try:
        logger.info(f"Generating simple mode summary for {ticker}")
        
        # Get rule-based summary
        summary_data = await summary_service.generate_simple_summary(
            ticker=ticker, 
            force_refresh=force_refresh
        )
        
        return summary_data
        
    except ValueError as e:
        logger.error(f"Invalid ticker {ticker}: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid ticker: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating simple summary for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/summary/{ticker}/agentic", response_model=AgenticSummaryResponse)
async def get_agentic_summary(
    ticker: str,
    force_refresh: bool = Query(False, description="Force refresh of cached analysis")
) -> AgenticSummaryResponse:
    """
    Get AI-powered agentic mode summary analysis
    
    **Single Financial Analyst Agent with sector-specific reasoning**
    
    - **LLM-enabled** - Advanced reasoning and synthesis
    - **Sector-aware** - Tailored analysis per industry
    - **Comprehensive** - Multi-lens investment thesis
    - **Natural language** - Human-readable insights
    """
    try:
        logger.info(f"Generating agentic mode summary for {ticker}")
        
        # Get AI-powered summary
        summary_data = await summary_service.generate_agentic_summary(
            ticker=ticker,
            force_refresh=force_refresh
        )
        
        return summary_data
        
    except ValueError as e:
        logger.error(f"Invalid ticker {ticker}: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid ticker: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating agentic summary for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/summary/{ticker}", response_model=SummaryResponse)
async def get_summary(
    ticker: str,
    mode: str = Query("simple", description="Analysis mode: 'simple' or 'agentic'"),
    force_refresh: bool = Query(False, description="Force refresh of cached analysis")
) -> SummaryResponse:
    """
    Get summary analysis with mode selection
    
    **Unified endpoint supporting both analysis modes**
    
    - **mode=simple**: Rule-based analysis (fast, deterministic)
    - **mode=agentic**: AI-powered analysis (comprehensive, natural language)
    """
    if mode not in ["simple", "agentic"]:
        raise HTTPException(status_code=400, detail="Mode must be 'simple' or 'agentic'")
    
    if mode == "simple":
        return await get_simple_summary(ticker, force_refresh)
    else:
        return await get_agentic_summary(ticker, force_refresh)

@router.get("/peers/{ticker}", response_model=dict)
async def get_peer_analysis(
    ticker: str,
    target_count: int = Query(5, ge=3, le=10, description="Number of peers to select")
) -> dict:
    """
    Get peer comparison analysis
    
    **Auto-selected peer comparison with sector context**
    
    - **Sector-based selection** - 3-5 peers from same industry
    - **Market cap matching** - Similar sized companies
    - **Comparative metrics** - PE, PB, ROE ratios
    - **Fallback handling** - Graceful degradation if peers unavailable
    """
    try:
        logger.info(f"Getting peer analysis for {ticker} with {target_count} peers")
        
        peer_data = await summary_service.get_peer_analysis(
            ticker=ticker,
            target_count=target_count
        )
        
        return peer_data
        
    except ValueError as e:
        logger.error(f"Invalid ticker {ticker}: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid ticker: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting peer analysis for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Peer analysis failed: {str(e)}")

@router.post("/summary/batch", response_model=dict)
async def get_batch_summaries(
    request: dict,
    mode: str = Query("simple", description="Analysis mode for all tickers")
) -> dict:
    """
    Get summary analysis for multiple tickers in batch
    
    **Batch processing for multiple stock analysis**
    
    - **Efficient processing** - Parallel analysis of multiple stocks
    - **Consistent mode** - Same analysis mode for all tickers
    - **Error handling** - Individual failures don't break entire batch
    """
    try:
        tickers = request.get("tickers", [])
        if not tickers or len(tickers) > 10:
            raise HTTPException(status_code=400, detail="Provide 1-10 tickers")
        
        logger.info(f"Generating batch summaries for {len(tickers)} tickers in {mode} mode")
        
        batch_results = await summary_service.generate_batch_summaries(
            tickers=tickers,
            mode=mode
        )
        
        return batch_results
        
    except Exception as e:
        logger.error(f"Error in batch summary generation: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

# Health and utility endpoints
@router.get("/health")
async def v3_health_check():
    """Health check for v3 Summary Engine"""
    return {
        "status": "healthy",
        "service": "equityscope-v3-summary-engine",
        "version": "3.0.0",
        "features": {
            "simple_mode": "Rule-based analysis with quantitative heuristics",
            "agentic_mode": "AI-powered single-agent investment thesis",
            "peer_analysis": "Auto-selected peer comparison system",
            "sector_awareness": "Industry-specific analysis logic",
            "graceful_degradation": "Fallback handling for missing data"
        },
        "endpoints": {
            "simple_summary": "/api/v3/summary/{ticker}/simple",
            "agentic_summary": "/api/v3/summary/{ticker}/agentic",
            "unified_summary": "/api/v3/summary/{ticker}?mode=simple|agentic",
            "peer_analysis": "/api/v3/peers/{ticker}",
            "batch_analysis": "/api/v3/summary/batch"
        }
    }

@router.get("/sectors")
async def get_supported_sectors():
    """Get list of sectors with specific analysis logic"""
    return {
        "priority_sectors": [
            {
                "name": "BFSI",
                "description": "Banks, NBFCs, Financial Services",
                "valuation_model": "Excess Return Model",
                "key_metrics": ["GNPA", "NII", "Cost-to-income"]
            },
            {
                "name": "FMCG", 
                "description": "Fast Moving Consumer Goods",
                "valuation_model": "DCF + EV/EBITDA",
                "key_metrics": ["Volume growth", "ASP trends", "Distribution reach"]
            },
            {
                "name": "IT & Services",
                "description": "Information Technology",
                "valuation_model": "DCF + Revenue multiples",
                "key_metrics": ["Client additions", "Deal wins", "Margin expansion"]
            },
            {
                "name": "Pharma",
                "description": "Pharmaceuticals",
                "valuation_model": "DCF + EV/EBITDA",
                "key_metrics": ["R&D spend", "ANDA pipeline", "USFDA observations"]
            },
            {
                "name": "Energy & Commodities",
                "description": "Oil, Gas, Metals, Mining",
                "valuation_model": "NAV + Commodity price sensitivity",
                "key_metrics": ["Production volumes", "Commodity prices", "Cost per unit"]
            },
            {
                "name": "Real Estate",
                "description": "Real Estate Development",
                "valuation_model": "NAV-based valuation",
                "key_metrics": ["Inventory velocity", "Absorption rate", "Project pipeline"]
            }
        ],
        "fallback": {
            "name": "General",
            "description": "Generic analysis for other sectors",
            "valuation_model": "DCF",
            "key_metrics": ["Revenue growth", "Margin trends", "ROE"]
        }
    }