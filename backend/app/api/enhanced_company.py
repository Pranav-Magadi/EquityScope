from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
import logging
from ..services.enhanced_data_service import get_enhanced_data_service, EnhancedDataService
from ..services.analysis_service import AnalysisService
from ..models.company import CompanyInfo, StockPrice, SWOTAnalysis, NewsSentiment, MarketLandscape, EmployeeSentiment, CompanyAnalysis
from ..models.kite import KiteHistoricalData

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2/company", tags=["enhanced-company"])

async def get_data_service() -> EnhancedDataService:
    """Dependency to get enhanced data service instance"""
    service = get_enhanced_data_service()
    if not service._initialized:
        await service.initialize()
    return service

@router.get("/status")
async def get_data_source_status(
    service: EnhancedDataService = Depends(get_data_service)
):
    """Get status of data sources (Kite vs yfinance)"""
    return service.get_data_source_status()

@router.get("/{ticker}", response_model=CompanyAnalysis)
async def get_enhanced_company_analysis(
    ticker: str,
    service: EnhancedDataService = Depends(get_data_service)
):
    """Get comprehensive company analysis using enhanced data sources"""
    try:
        # Fetch company info with Kite enhancement
        company_info = await service.get_company_info(ticker)
        if not company_info:
            raise HTTPException(status_code=404, detail=f"Company data not found for ticker: {ticker}")
        
        # Fetch enhanced stock price (real-time from Kite if available)
        stock_price = await service.get_stock_price(ticker)
        if not stock_price:
            raise HTTPException(status_code=404, detail=f"Stock price data not found for ticker: {ticker}")
        
        # Generate qualitative analysis with Claude-based sentiment
        swot = AnalysisService.get_swot_analysis(ticker, company_info.name)
        news_sentiment = await AnalysisService.get_news_sentiment(
            ticker=ticker,
            company_name=company_info.name,
            sector=company_info.sector
        )
        market_landscape = AnalysisService.get_market_landscape(ticker, company_info.name, company_info.sector)
        employee_sentiment = AnalysisService.get_employee_sentiment(company_info.name)
        
        return CompanyAnalysis(
            company_info=company_info,
            stock_price=stock_price,
            swot=swot,
            news_sentiment=news_sentiment,
            market_landscape=market_landscape,
            employee_sentiment=employee_sentiment
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching enhanced company analysis for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/info", response_model=CompanyInfo)
async def get_enhanced_company_info(
    ticker: str,
    service: EnhancedDataService = Depends(get_data_service)
):
    """Get enhanced company information"""
    try:
        company_info = await service.get_company_info(ticker)
        if not company_info:
            raise HTTPException(status_code=404, detail=f"Company info not found for ticker: {ticker}")
        return company_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching enhanced company info for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/price", response_model=StockPrice)
async def get_enhanced_stock_price(
    ticker: str,
    service: EnhancedDataService = Depends(get_data_service)
):
    """Get enhanced real-time stock price"""
    try:
        stock_price = await service.get_stock_price(ticker)
        if not stock_price:
            raise HTTPException(status_code=404, detail=f"Stock price not found for ticker: {ticker}")
        return stock_price
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching enhanced stock price for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/intraday")
async def get_intraday_data(
    ticker: str,
    interval: str = Query(default="5minute", description="Interval: minute, 3minute, 5minute, 15minute, 30minute, 60minute"),
    service: EnhancedDataService = Depends(get_data_service)
):
    """Get intraday price data (only available with Kite)"""
    try:
        intraday_data = await service.get_intraday_data(ticker, interval)
        
        return {
            "ticker": ticker,
            "interval": interval,
            "data": [
                {
                    "timestamp": data.date.isoformat(),
                    "open": data.open,
                    "high": data.high,
                    "low": data.low,
                    "close": data.close,
                    "volume": data.volume
                }
                for data in intraday_data
            ],
            "count": len(intraday_data),
            "source": "kite" if intraday_data else "unavailable"
        }
        
    except Exception as e:
        logger.error(f"Error fetching intraday data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/market-depth")
async def get_market_depth(
    ticker: str,
    service: EnhancedDataService = Depends(get_data_service)
):
    """Get market depth data (only available with Kite)"""
    try:
        depth_data = await service.get_market_depth(ticker)
        
        if not depth_data:
            return {
                "ticker": ticker,
                "message": "Market depth data not available",
                "source": "unavailable"
            }
        
        return depth_data
        
    except Exception as e:
        logger.error(f"Error fetching market depth for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/quotes")
async def get_multiple_quotes(
    tickers: List[str],
    service: EnhancedDataService = Depends(get_data_service)
):
    """Get quotes for multiple symbols efficiently"""
    try:
        if len(tickers) > 50:
            raise HTTPException(status_code=400, detail="Maximum 50 tickers allowed per request")
        
        quotes = await service.get_multiple_quotes(tickers)
        
        return {
            "quotes": quotes,
            "count": len([q for q in quotes.values() if q is not None]),
            "total_requested": len(tickers),
            "source": service.get_data_source_status()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching multiple quotes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search/{query}")
async def search_symbols(
    query: str,
    limit: int = Query(default=20, le=50, description="Maximum number of results"),
    service: EnhancedDataService = Depends(get_data_service)
):
    """Search for symbols/companies"""
    try:
        if len(query) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters long")
        
        results = await service.search_symbols(query)
        
        # Limit results
        limited_results = results[:limit]
        
        return {
            "query": query,
            "results": limited_results,
            "count": len(limited_results),
            "total_found": len(results),
            "source": "kite" if results else "unavailable"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching symbols for query '{query}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/market/status")
async def get_market_status(
    service: EnhancedDataService = Depends(get_data_service)
):
    """Get current market status"""
    try:
        status = await service.get_market_status()
        return {
            "market_status": status,
            "timestamp": "now",
            "source": "kite" if "error" not in status else "unavailable"
        }
        
    except Exception as e:
        logger.error(f"Error fetching market status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/portfolio/holdings")
async def get_portfolio_holdings(
    service: EnhancedDataService = Depends(get_data_service)
):
    """Get portfolio holdings (requires authenticated Kite session)"""
    try:
        holdings = await service.get_portfolio_data()
        
        return {
            "holdings": holdings,
            "count": len(holdings),
            "source": "kite" if holdings else "unavailable",
            "note": "Requires authenticated Kite Connect session"
        }
        
    except Exception as e:
        logger.error(f"Error fetching portfolio holdings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Utility endpoints for Kite integration
@router.get("/kite/login-url")
async def get_kite_login_url(
    service: EnhancedDataService = Depends(get_data_service)
):
    """Get Kite Connect login URL for authentication"""
    try:
        login_url = await service.kite_service.get_login_url()
        return {
            "login_url": login_url,
            "instructions": "Visit this URL to authenticate with Kite Connect and get request token"
        }
    except Exception as e:
        logger.error(f"Error generating Kite login URL: {e}")
        raise HTTPException(status_code=500, detail="Could not generate login URL")

@router.post("/kite/set-tokens")
async def set_kite_tokens(
    request_token: Optional[str] = None,
    access_token: Optional[str] = None,
    service: EnhancedDataService = Depends(get_data_service)
):
    """Set Kite Connect tokens for authentication"""
    try:
        if request_token:
            service.kite_service.config.request_token = request_token
        if access_token:
            service.kite_service.config.access_token = access_token
        
        # Re-initialize session with new tokens
        success = await service.kite_service.initialize_session()
        
        return {
            "success": success,
            "message": "Tokens updated successfully" if success else "Failed to initialize session",
            "status": service.get_data_source_status()
        }
        
    except Exception as e:
        logger.error(f"Error setting Kite tokens: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")