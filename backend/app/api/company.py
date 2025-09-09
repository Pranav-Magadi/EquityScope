from fastapi import APIRouter, HTTPException
from typing import Optional
import logging
from ..services.data_service import DataService
from ..services.analysis_service import AnalysisService
from ..models.company import CompanyInfo, StockPrice, SWOTAnalysis, NewsSentiment, MarketLandscape, EmployeeSentiment, CompanyAnalysis

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/company", tags=["company"])

@router.get("/{ticker}/basic")
async def get_basic_company_data(ticker: str):
    """Get basic company info and stock price without AI analysis"""
    try:
        # Use enhanced data service for better data availability
        from ..services.enhanced_data_service import get_enhanced_data_service
        enhanced_service = get_enhanced_data_service()
        
        # Fetch company info
        company_info = await enhanced_service.get_company_info(ticker)
        if not company_info:
            raise HTTPException(status_code=404, detail=f"Company data not found for ticker: {ticker}")
        
        # Fetch stock price
        stock_price = await enhanced_service.get_stock_price(ticker)
        if not stock_price:
            raise HTTPException(status_code=404, detail=f"Stock price data not found for ticker: {ticker}")
        
        return {
            "company_info": company_info,
            "stock_price": stock_price
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching basic company data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}", response_model=CompanyAnalysis)
async def get_company_analysis(ticker: str):
    """Get comprehensive company analysis including all qualitative metrics"""
    try:
        # Fetch company info
        company_info = DataService.get_company_info(ticker)
        if not company_info:
            raise HTTPException(status_code=404, detail=f"Company data not found for ticker: {ticker}")
        
        # Fetch stock price
        stock_price = DataService.get_stock_price(ticker)
        if not stock_price:
            raise HTTPException(status_code=404, detail=f"Stock price data not found for ticker: {ticker}")
        
        # Generate qualitative analysis
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
        logger.error(f"Error fetching company analysis for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/info", response_model=CompanyInfo)
async def get_company_info(ticker: str):
    """Get basic company information"""
    try:
        company_info = DataService.get_company_info(ticker)
        if not company_info:
            raise HTTPException(status_code=404, detail=f"Company info not found for ticker: {ticker}")
        return company_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching company info for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/price", response_model=StockPrice)
async def get_stock_price(ticker: str):
    """Get current stock price and metrics"""
    try:
        stock_price = DataService.get_stock_price(ticker)
        if not stock_price:
            raise HTTPException(status_code=404, detail=f"Stock price not found for ticker: {ticker}")
        return stock_price
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock price for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/swot", response_model=SWOTAnalysis)
async def get_swot_analysis(ticker: str):
    """Get SWOT analysis for the company"""
    try:
        company_info = DataService.get_company_info(ticker)
        if not company_info:
            raise HTTPException(status_code=404, detail=f"Company info not found for ticker: {ticker}")
        
        swot = AnalysisService.get_swot_analysis(ticker, company_info.name)
        return swot
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching SWOT analysis for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/sentiment", response_model=NewsSentiment)
async def get_news_sentiment(ticker: str):
    """Get Claude-based contextual news sentiment analysis"""
    try:
        # Get company info for context
        company_info = DataService.get_company_info(ticker)
        company_name = company_info.name if company_info else ticker
        sector = company_info.sector if company_info else None
        
        # Use new Claude-based sentiment service
        sentiment = await AnalysisService.get_news_sentiment(
            ticker=ticker,
            company_name=company_name,
            sector=sector
        )
        return sentiment
    except Exception as e:
        logger.error(f"Error fetching Claude sentiment for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/market", response_model=MarketLandscape)
async def get_market_landscape(ticker: str):
    """Get market landscape analysis"""
    try:
        company_info = DataService.get_company_info(ticker)
        if not company_info:
            raise HTTPException(status_code=404, detail=f"Company info not found for ticker: {ticker}")
        
        market_landscape = AnalysisService.get_market_landscape(ticker, company_info.name, company_info.sector)
        return market_landscape
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market landscape for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/employee", response_model=EmployeeSentiment)
async def get_employee_sentiment(ticker: str):
    """Get employee sentiment analysis"""
    try:
        company_info = DataService.get_company_info(ticker)
        if not company_info:
            raise HTTPException(status_code=404, detail=f"Company info not found for ticker: {ticker}")
        
        employee_sentiment = AnalysisService.get_employee_sentiment(company_info.name)
        return employee_sentiment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching employee sentiment for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")