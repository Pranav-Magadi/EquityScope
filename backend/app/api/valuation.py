from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import logging
from ..services.data_service import DataService
from ..services.enhanced_data_service import get_enhanced_data_service
from ..services.dcf_service import DCFService
from ..services.technical_analysis import technical_analysis_service
from ..services.claude_service import claude_service, ClaudeService
from ..services.price_service import price_service
from ..models.dcf import DCFAssumptions, DCFResponse, DCFDefaults, FinancialData

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/valuation", tags=["valuation"])

@router.get("/{ticker}/financials", response_model=FinancialData)
async def get_financial_data(ticker: str, years: int = 5):
    """Get historical financial data for DCF analysis"""
    try:
        financial_data = DataService.get_financial_data(ticker, years)
        if not financial_data:
            raise HTTPException(status_code=404, detail=f"Financial data not found for ticker: {ticker}")
        return financial_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching financial data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/defaults", response_model=DCFDefaults)
async def get_dcf_defaults(ticker: str, sector: str = Query(None, description="Sector classification for sector-specific assumptions")):
    """Get intelligent default assumptions for DCF analysis with sector intelligence"""
    try:
        # Try enhanced data service first
        enhanced_service = get_enhanced_data_service()
        
        # Try to get financial data from enhanced service
        financial_data = None
        try:
            financial_data = await enhanced_service.get_financial_data(ticker, years=5)
            if not financial_data and ticker.endswith('.NS'):
                # Try without .NS suffix
                base_ticker = ticker.replace('.NS', '')
                financial_data = await enhanced_service.get_financial_data(base_ticker, years=5)
        except Exception as e:
            logger.warning(f"Enhanced service failed for {ticker}: {e}")
        
        # Fallback to DataService if enhanced service fails
        if not financial_data:
            logger.info(f"Using DataService fallback for {ticker}")
            financial_data = DataService.get_financial_data(ticker)
        
        if not financial_data:
            # Generate mock defaults for demonstration
            logger.warning(f"No financial data available for {ticker}, generating mock defaults")
            return await _generate_mock_dcf_defaults(ticker, sector)
        
        # Use async call since DCFService.calculate_default_assumptions is now async
        defaults = await DCFService.calculate_default_assumptions(financial_data, ticker, sector)
        return defaults
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating DCF defaults for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/dcf", response_model=DCFResponse)
async def calculate_dcf_valuation(ticker: str, assumptions: DCFAssumptions):
    """Calculate DCF valuation with custom assumptions"""
    try:
        logger.info(f"DCF calculation request for {ticker} with assumptions: {assumptions}")
        
        # Fetch financial data
        financial_data = DataService.get_financial_data(ticker)
        if not financial_data:
            logger.error(f"No financial data found for ticker: {ticker}")
            raise HTTPException(status_code=404, detail=f"Financial data not found for ticker: {ticker}")
        
        logger.info(f"Financial data retrieved for {ticker}: {len(financial_data.revenue)} years of revenue data")
        
        # Get defaults to fetch current market price
        defaults = DCFService.calculate_default_assumptions(financial_data, ticker)
        current_price = defaults.current_price
        logger.info(f"Current price for {ticker}: {current_price}")
        
        # Calculate DCF valuation with current market price
        valuation = DCFService.calculate_dcf(financial_data, assumptions, current_price)
        logger.info(f"DCF valuation calculated successfully for {ticker}")
        
        # Generate sensitivity analysis
        sensitivity = DCFService.generate_sensitivity_analysis(financial_data, assumptions)
        logger.info(f"Sensitivity analysis generated for {ticker}")
        
        response = DCFResponse(
            valuation=valuation,
            sensitivity=sensitivity,
            financial_data=financial_data,
            last_updated=datetime.now()
        )
        
        logger.info(f"DCF calculation completed successfully for {ticker}")
        return response
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error calculating DCF for {ticker}: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid data for DCF calculation: {str(e)}")
    except Exception as e:
        logger.error(f"Error calculating DCF valuation for {ticker}: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{ticker}/quick-dcf")
async def quick_dcf_valuation(
    ticker: str,
    revenue_growth: float = None,
    ebitda_margin: float = None,
    tax_rate: float = None,
    wacc: float = None,
    terminal_growth: float = None
):
    """Quick DCF calculation with optional parameter overrides"""
    try:
        # Get financial data and defaults
        financial_data = DataService.get_financial_data(ticker)
        if not financial_data:
            raise HTTPException(status_code=404, detail=f"Financial data not found for ticker: {ticker}")
        
        defaults = DCFService.calculate_default_assumptions(financial_data)
        
        # Create assumptions with provided overrides or defaults
        assumptions = DCFAssumptions(
            revenue_growth_rate=revenue_growth if revenue_growth is not None else defaults.revenue_growth_rate,
            ebitda_margin=ebitda_margin if ebitda_margin is not None else defaults.ebitda_margin,
            tax_rate=tax_rate if tax_rate is not None else defaults.tax_rate,
            wacc=wacc if wacc is not None else defaults.wacc,
            terminal_growth_rate=terminal_growth if terminal_growth is not None else defaults.terminal_growth_rate
        )
        
        # Calculate valuation with current market price
        current_price = defaults.current_price
        valuation = DCFService.calculate_dcf(financial_data, assumptions, current_price)
        
        return {
            "ticker": ticker,
            "intrinsic_value_per_share": valuation.intrinsic_value_per_share,
            "upside_downside": valuation.upside_downside,
            "assumptions_used": assumptions.dict(),
            "calculation_timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in quick DCF calculation for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/sensitivity")
async def get_sensitivity_analysis(ticker: str):
    """Get sensitivity analysis using default assumptions"""
    try:
        # Get financial data and defaults
        financial_data = DataService.get_financial_data(ticker)
        if not financial_data:
            raise HTTPException(status_code=404, detail=f"Financial data not found for ticker: {ticker}")
        
        defaults = DCFService.calculate_default_assumptions(financial_data)
        
        assumptions = DCFAssumptions(
            revenue_growth_rate=defaults.revenue_growth_rate,
            ebitda_margin=defaults.ebitda_margin,
            tax_rate=defaults.tax_rate,
            wacc=defaults.wacc,
            terminal_growth_rate=defaults.terminal_growth_rate
        )
        
        sensitivity = DCFService.generate_sensitivity_analysis(financial_data, assumptions)
        return sensitivity
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating sensitivity analysis for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/technical-analysis")
async def get_technical_analysis(
    ticker: str,
    period: str = Query(default="1y", regex="^(3mo|6mo|1y|3y)$"),
    mode: str = Query(default="simple", regex="^(simple|agentic)$")
):
    """Get technical analysis with charts and indicators"""
    try:
        logger.info(f"Getting technical analysis for {ticker} with period {period}")
        
        # Get technical analysis data
        tech_data = technical_analysis_service.get_technical_analysis(ticker, period)
        if not tech_data:
            raise HTTPException(status_code=404, detail=f"Technical analysis data not found for ticker: {ticker}")
        
        # Only generate AI commentary in agentic mode (when Claude is available)
        ai_summary = None
        if mode == "agentic":
            # Initialize fresh Claude service to get latest API keys
            claude_service = ClaudeService()
            if claude_service.is_available():
                try:
                    ai_summary = await claude_service.technical_analyst_agent(tech_data['indicator_values'], ticker)
                except Exception as e:
                    logger.warning(f"AI technical analysis failed for {ticker}: {e}")
                    # Continue without AI summary
        
        # Add AI summary to the response if available
        if ai_summary:
            tech_data['ai_summary'] = ai_summary
        
        return tech_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating technical analysis for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/technical-indicators")
async def get_technical_indicators(
    ticker: str,
    period: str = Query(default="1y", regex="^(3mo|6mo|1y|3y)$")
):
    """Get just the technical indicator values without charts"""
    try:
        logger.info(f"Getting technical indicators for {ticker} with period {period}")
        
        # Get technical analysis data
        tech_data = technical_analysis_service.get_technical_analysis(ticker, period)
        if not tech_data:
            raise HTTPException(status_code=404, detail=f"Technical data not found for ticker: {ticker}")
        
        # Return only indicator values
        return {
            'ticker': ticker,
            'period': period,
            'indicator_values': tech_data['indicator_values'],
            'analysis_timestamp': tech_data['analysis_timestamp']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting technical indicators for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/price-cache/status")
async def get_price_cache_status():
    """Get price cache status for debugging"""
    try:
        cache_status = price_service.get_cache_status()
        return {
            'cache_status': cache_status,
            'timestamp': datetime.now().isoformat(),
            'total_cached_tickers': len(cache_status)
        }
    except Exception as e:
        logger.error(f"Error getting cache status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/price-cache/{ticker}")
async def clear_price_cache(ticker: str = None):
    """Clear price cache for specific ticker or all tickers"""
    try:
        price_service.clear_cache(ticker if ticker != "all" else None)
        return {
            'message': f'Cache cleared for {ticker if ticker != "all" else "all tickers"}',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def _generate_mock_dcf_defaults(ticker: str, sector: str = None) -> DCFDefaults:
    """Generate mock DCF defaults for demonstration when real data is unavailable"""
    logger.info(f"Generating mock DCF defaults for {ticker}")
    
    # Mock current price based on ticker
    if ticker.startswith('TCS'):
        current_price = 3500.0
    elif ticker.startswith('RELIANCE'):
        current_price = 2800.0
    else:
        current_price = 1500.0
    
    return DCFDefaults(
        revenue_growth_rate=0.12,  # 12% growth
        ebitda_margin=0.25,        # 25% EBITDA margin
        tax_rate=0.30,             # 30% tax rate (India corporate tax)
        wacc=0.11,                 # 11% WACC
        terminal_growth_rate=0.04, # 4% terminal growth
        current_price=current_price,
        rationale={
            "revenue_growth": "Based on historical sector performance and market conditions",
            "ebitda_margin": "Industry average for technology companies in India",
            "tax_rate": "Standard Indian corporate tax rate",
            "wacc": "Estimated cost of capital for large-cap Indian tech stocks",
            "terminal_growth": "Conservative long-term GDP growth assumption"
        }
    )