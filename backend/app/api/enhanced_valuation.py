from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import logging
from ..services.enhanced_data_service import get_enhanced_data_service, EnhancedDataService
from ..services.dcf_service import DCFService
from ..models.dcf import DCFAssumptions, DCFResponse, DCFDefaults, FinancialData

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2/valuation", tags=["enhanced-valuation"])

async def get_data_service() -> EnhancedDataService:
    """Dependency to get enhanced data service instance"""
    service = get_enhanced_data_service()
    if not service._initialized:
        await service.initialize()
    return service

@router.get("/{ticker}/financials", response_model=FinancialData)
async def get_enhanced_financial_data(
    ticker: str, 
    years: int = 5,
    service: EnhancedDataService = Depends(get_data_service)
):
    """Get enhanced financial data for DCF analysis"""
    try:
        financial_data = await service.get_financial_data(ticker, years)
        if not financial_data:
            raise HTTPException(status_code=404, detail=f"Financial data not found for ticker: {ticker}")
        return financial_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching enhanced financial data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/defaults", response_model=DCFDefaults)
async def get_enhanced_dcf_defaults(
    ticker: str,
    service: EnhancedDataService = Depends(get_data_service)
):
    """Get intelligent default assumptions for DCF analysis using enhanced data"""
    try:
        financial_data = await service.get_financial_data(ticker)
        if not financial_data:
            raise HTTPException(status_code=404, detail=f"Financial data not found for ticker: {ticker}")
        
        defaults = DCFService.calculate_default_assumptions(financial_data)
        
        # Enhance defaults with market data if available
        try:
            market_status = await service.get_market_status()
            if 'error' not in market_status:
                # Could enhance WACC calculation with real-time risk-free rate
                # For now, use standard calculation
                pass
        except Exception as e:
            logger.warning(f"Could not enhance defaults with market data: {e}")
        
        return defaults
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating enhanced DCF defaults for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/dcf", response_model=DCFResponse)
async def calculate_enhanced_dcf_valuation(
    ticker: str, 
    assumptions: DCFAssumptions,
    service: EnhancedDataService = Depends(get_data_service)
):
    """Calculate DCF valuation with enhanced data sources"""
    try:
        # Fetch enhanced financial data
        financial_data = await service.get_financial_data(ticker)
        if not financial_data:
            raise HTTPException(status_code=404, detail=f"Financial data not found for ticker: {ticker}")
        
        # Calculate DCF valuation
        valuation = DCFService.calculate_dcf(financial_data, assumptions)
        
        # Generate sensitivity analysis
        sensitivity = DCFService.generate_sensitivity_analysis(financial_data, assumptions)
        
        # Get current market price for comparison (using enhanced real-time data)
        try:
            current_quote = await service.get_stock_price(ticker)
            if current_quote:
                # Update valuation with real-time price for better comparison
                valuation.current_stock_price = current_quote.current_price
                valuation.upside_downside = (
                    (valuation.intrinsic_value_per_share - current_quote.current_price) / 
                    current_quote.current_price
                ) * 100
        except Exception as e:
            logger.warning(f"Could not update with real-time price: {e}")
        
        return DCFResponse(
            valuation=valuation,
            sensitivity=sensitivity,
            financial_data=financial_data,
            last_updated=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating enhanced DCF valuation for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{ticker}/quick-dcf")
async def quick_enhanced_dcf_valuation(
    ticker: str,
    revenue_growth: float = None,
    ebitda_margin: float = None,
    tax_rate: float = None,
    wacc: float = None,
    terminal_growth: float = None,
    service: EnhancedDataService = Depends(get_data_service)
):
    """Quick DCF calculation with enhanced data and optional parameter overrides"""
    try:
        # Get enhanced financial data and defaults
        financial_data = await service.get_financial_data(ticker)
        if not financial_data:
            raise HTTPException(status_code=404, detail=f"Financial data not found for ticker: {ticker}")
        
        defaults = DCFService.calculate_default_assumptions(financial_data)
        
        # Create assumptions with provided overrides or enhanced defaults
        assumptions = DCFAssumptions(
            revenue_growth_rate=revenue_growth if revenue_growth is not None else defaults.revenue_growth_rate,
            ebitda_margin=ebitda_margin if ebitda_margin is not None else defaults.ebitda_margin,
            tax_rate=tax_rate if tax_rate is not None else defaults.tax_rate,
            wacc=wacc if wacc is not None else defaults.wacc,
            terminal_growth_rate=terminal_growth if terminal_growth is not None else defaults.terminal_growth_rate
        )
        
        # Calculate valuation
        valuation = DCFService.calculate_dcf(financial_data, assumptions)
        
        # Get real-time price for comparison
        current_price = None
        try:
            quote = await service.get_stock_price(ticker)
            if quote:
                current_price = quote.current_price
                valuation.current_stock_price = current_price
                valuation.upside_downside = (
                    (valuation.intrinsic_value_per_share - current_price) / current_price
                ) * 100
        except Exception as e:
            logger.warning(f"Could not get real-time price: {e}")
        
        return {
            "ticker": ticker,
            "intrinsic_value_per_share": valuation.intrinsic_value_per_share,
            "current_market_price": current_price,
            "upside_downside": valuation.upside_downside,
            "assumptions_used": assumptions.dict(),
            "data_source": service.get_data_source_status(),
            "calculation_timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced quick DCF calculation for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/sensitivity")
async def get_enhanced_sensitivity_analysis(
    ticker: str,
    service: EnhancedDataService = Depends(get_data_service)
):
    """Get sensitivity analysis using enhanced default assumptions"""
    try:
        # Get enhanced financial data and defaults
        financial_data = await service.get_financial_data(ticker)
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
        
        return {
            "ticker": ticker,
            "sensitivity_analysis": sensitivity,
            "base_assumptions": assumptions.dict(),
            "data_source": service.get_data_source_status(),
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating enhanced sensitivity analysis for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/real-time-metrics")
async def get_real_time_valuation_metrics(
    ticker: str,
    service: EnhancedDataService = Depends(get_data_service)
):
    """Get real-time valuation metrics combining DCF with market data"""
    try:
        # Get current quote
        quote = await service.get_stock_price(ticker)
        if not quote:
            raise HTTPException(status_code=404, detail=f"Real-time quote not available for {ticker}")
        
        # Get financial data for ratios
        financial_data = await service.get_financial_data(ticker, 1)  # Last year only for speed
        
        metrics = {
            "ticker": ticker,
            "timestamp": datetime.now(),
            "current_price": quote.current_price,
            "change": quote.change,
            "change_percent": quote.change_percent,
            "volume": quote.volume,
            "source": service.get_data_source_status()
        }
        
        # Add calculated ratios if financial data available
        if financial_data and len(financial_data.revenue) > 0:
            latest_revenue = financial_data.revenue[0]
            latest_shares = financial_data.shares_outstanding[0] if financial_data.shares_outstanding else 1
            
            if latest_shares > 0:
                metrics.update({
                    "price_to_sales": quote.current_price / (latest_revenue / latest_shares) if latest_revenue > 0 else None,
                    "market_cap": quote.current_price * latest_shares,
                })
        
        # Get intraday performance if available
        try:
            intraday_data = await service.get_intraday_data(ticker, "5minute")
            if intraday_data:
                day_open = intraday_data[0].open
                day_high = max(data.high for data in intraday_data)
                day_low = min(data.low for data in intraday_data)
                
                metrics.update({
                    "day_open": day_open,
                    "day_high": day_high,
                    "day_low": day_low,
                    "intraday_data_points": len(intraday_data)
                })
        except Exception as e:
            logger.warning(f"Could not fetch intraday data: {e}")
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching real-time valuation metrics for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{ticker}/comparison")
async def get_peer_comparison(
    ticker: str,
    peers: str = None,  # Comma-separated list of peer tickers
    service: EnhancedDataService = Depends(get_data_service)
):
    """Get valuation comparison with peer companies"""
    try:
        if not peers:
            # Default peers for major Indian companies (simplified)
            peer_mapping = {
                "RELIANCE": ["IOC", "BPCL", "ONGC"],
                "TCS": ["INFY", "WIPRO", "HCLTECH"],
                "HDFCBANK": ["ICICIBANK", "KOTAKBANK", "AXISBANK"],
                "ITC": ["HUL", "NESTLEIND", "DABUR"]
            }
            base_symbol = ticker.replace('.NS', '').upper()
            peer_symbols = peer_mapping.get(base_symbol, [])
        else:
            peer_symbols = [p.strip() for p in peers.split(',')]
        
        if not peer_symbols:
            return {
                "ticker": ticker,
                "message": "No peer companies specified",
                "suggestions": "Use 'peers' parameter with comma-separated ticker list"
            }
        
        # Get quotes for all companies
        all_tickers = [ticker] + [f"{p}.NS" if not p.endswith('.NS') else p for p in peer_symbols]
        quotes = await service.get_multiple_quotes(all_tickers)
        
        comparison_data = {}
        for tick, quote in quotes.items():
            if quote:
                comparison_data[tick] = {
                    "price": quote.current_price,
                    "change_percent": quote.change_percent,
                    "volume": quote.volume,
                    "market_cap": quote.market_cap
                }
        
        return {
            "base_ticker": ticker,
            "peer_comparison": comparison_data,
            "timestamp": datetime.now(),
            "data_source": service.get_data_source_status()
        }
        
    except Exception as e:
        logger.error(f"Error fetching peer comparison for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")