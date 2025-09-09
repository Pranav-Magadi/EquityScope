from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
import logging
from ..services.technical_analysis import technical_analysis_service
from ..services.claude_service import ClaudeService

router = APIRouter(prefix="/api", tags=["Technical Analysis"])
logger = logging.getLogger(__name__)

@router.get("/valuation/{ticker}/technical-analysis")
async def get_technical_analysis(
    ticker: str,
    period: str = Query(default="1y", regex="^(3mo|6mo|1y|3y)$"),
    mode: str = Query(default="simple", regex="^(simple|agentic)$")
):
    """Get real technical analysis with professional indicators"""
    try:
        logger.info(f"Getting technical analysis for {ticker} with period {period}")
        
        # Get real technical analysis data using pandas-ta
        tech_data = technical_analysis_service.get_technical_analysis(ticker, period)
        if not tech_data:
            raise HTTPException(status_code=404, detail=f"Technical analysis data not found for ticker: {ticker}")
        
        # Add AI summary only for agentic mode
        if mode == "agentic":
            tech_data['ai_summary'] = await generate_ai_summary(tech_data, ticker)
        else:
            # Simple mode doesn't need AI summary
            tech_data['ai_summary'] = None
        
        return tech_data
        
    except Exception as e:
        logger.error(f"Error fetching technical analysis for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch technical analysis for {ticker}")

async def generate_ai_summary(data: Dict[str, Any], ticker: str) -> str:
    """Generate AI-powered summary for technical analysis using Claude"""
    try:
        # Initialize fresh Claude service to get latest API keys
        claude_service = ClaudeService()
        
        # Try to get AI-powered summary first
        if claude_service.is_available():
            try:
                logger.info(f"Generating Claude AI summary for {ticker} technical analysis")
                ai_summary = await claude_service.technical_analyst_agent(data.get('indicator_values', {}), ticker)
                if ai_summary:
                    return ai_summary
                else:
                    logger.warning(f"Claude returned empty summary for {ticker}, using fallback")
            except Exception as e:
                logger.warning(f"Claude AI technical analysis failed for {ticker}: {e}")
        
        # Fallback to rule-based summary
        indicators = data.get('indicator_values', {})
        
        current_price = indicators.get('current_price', 0)
        rsi = indicators.get('rsi', 50)
        sma_50 = indicators.get('sma_50_current', 0)
        macd_current = indicators.get('macd_current', 0)
        macd_signal = indicators.get('macd_signal_current', 0)
        volume_trend = indicators.get('volume_trend', 'neutral')
        
        # Determine overall trend
        price_trend = "bullish" if current_price > sma_50 else "bearish"
        macd_trend = "bullish" if macd_current > macd_signal else "bearish"
        
        # RSI interpretation
        rsi_status = "overbought" if rsi >= 70 else "oversold" if rsi <= 30 else "neutral"
        
        # Use proper currency symbol
        currency = "₹" if ticker.endswith('.NS') else "$"
        
        summary = f"Technical analysis for {ticker} shows {price_trend} momentum with RSI at {rsi:.1f} ({rsi_status}). "
        summary += f"Current price of {currency}{current_price:.2f} is {'above' if current_price > sma_50 else 'below'} the 50-day moving average. "
        summary += f"MACD indicates {macd_trend} signals, while volume shows {volume_trend} trend."
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating AI summary for {ticker}: {e}")
        return f"Technical analysis completed for {ticker} with professional indicators."