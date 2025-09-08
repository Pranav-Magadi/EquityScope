import yfinance as yf
import pandas as pd
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging
import asyncio
from threading import Lock

logger = logging.getLogger(__name__)

class PriceService:
    """
    Centralized service for fetching and caching stock price data.
    Ensures consistency across all dashboard components.
    """
    
    # Class-level cache to ensure single source of truth
    _price_cache: Dict[str, Dict] = {}
    _cache_timestamps: Dict[str, datetime] = {}
    _cache_lock = Lock()
    _cache_ttl_seconds = 60  # Cache for 1 minute
    
    @classmethod
    def get_unified_stock_data(cls, ticker: str, force_refresh: bool = False) -> Optional[Dict]:
        """
        Get unified stock data including price, info, and historical data.
        Uses caching to ensure consistency across all components.
        
        Args:
            ticker: Stock ticker symbol
            force_refresh: Force refresh of cached data
            
        Returns:
            Dictionary containing unified stock data or None if failed
        """
        with cls._cache_lock:
            # Check cache first
            if not force_refresh and cls._is_cache_valid(ticker):
                logger.info(f"Returning cached data for {ticker}")
                return cls._price_cache[ticker]
            
            try:
                logger.info(f"Fetching fresh data for {ticker}")
                
                # Fetch data from yfinance once
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Get historical data for calculations
                hist = stock.history(period="5d")
                if hist.empty:
                    logger.error(f"No historical data found for {ticker}")
                    return None
                
                # Calculate current price with consistent fallback logic
                current_price = cls._get_standardized_current_price(info, hist)
                if current_price <= 0:
                    logger.error(f"Invalid current price for {ticker}: {current_price}")
                    return None
                
                # Calculate price change consistently
                change, change_percent = cls._calculate_price_change(hist, current_price)
                
                # Create unified data structure
                unified_data = {
                    'ticker': ticker,
                    'current_price': current_price,
                    'change': change,
                    'change_percent': change_percent,
                    'volume': int(hist['Volume'].iloc[-1]) if len(hist) > 0 else 0,
                    'market_cap': info.get('marketCap', 0),
                    'pe_ratio': info.get('trailingPE'),
                    'pb_ratio': info.get('priceToBook'),
                    'info': info,
                    'history': hist,
                    'timestamp': datetime.now(),
                    'data_source': 'yfinance_unified'
                }
                
                # Cache the data
                cls._price_cache[ticker] = unified_data
                cls._cache_timestamps[ticker] = datetime.now()
                
                logger.info(f"Successfully cached unified data for {ticker} - Price: ₹{current_price:.2f}")
                return unified_data
                
            except Exception as e:
                logger.error(f"Error fetching unified stock data for {ticker}: {e}")
                return None
    
    @classmethod
    def _is_cache_valid(cls, ticker: str) -> bool:
        """Check if cached data is still valid"""
        if ticker not in cls._price_cache or ticker not in cls._cache_timestamps:
            return False
        
        cache_age = datetime.now() - cls._cache_timestamps[ticker]
        return cache_age.total_seconds() < cls._cache_ttl_seconds
    
    @classmethod
    def _get_standardized_current_price(cls, info: Dict, hist: pd.DataFrame) -> float:
        """
        Standardized current price extraction with consistent fallback logic.
        This ensures all components use the same price value.
        """
        # Try different price fields in order of preference
        price_fields = [
            'currentPrice',
            'regularMarketPrice', 
            'regularMarketPreviousClose',
            'previousClose'
        ]
        
        for field in price_fields:
            price = info.get(field)
            if price and price > 0:
                return float(price)
        
        # Final fallback to latest historical close
        if not hist.empty and 'Close' in hist.columns:
            latest_close = hist['Close'].iloc[-1]
            if pd.notna(latest_close) and latest_close > 0:
                return float(latest_close)
        
        return 0.0
    
    @classmethod
    def _calculate_price_change(cls, hist: pd.DataFrame, current_price: float) -> Tuple[float, float]:
        """Calculate price change consistently"""
        if hist.empty or len(hist) < 2:
            return 0.0, 0.0
        
        try:
            # Use previous day's close for change calculation
            previous_close = hist['Close'].iloc[-2]
            if pd.isna(previous_close) or previous_close <= 0:
                return 0.0, 0.0
            
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100
            
            return float(change), float(change_percent)
        except Exception:
            return 0.0, 0.0
    
    @classmethod
    def get_price_for_company_header(cls, ticker: str) -> Optional[Dict]:
        """Get price data formatted for company header component"""
        data = cls.get_unified_stock_data(ticker)
        if not data:
            return None
        
        return {
            'current_price': data['current_price'],
            'change': data['change'],
            'change_percent': data['change_percent'],
            'volume': data['volume'],
            'market_cap': data['market_cap'],
            'pe_ratio': data['pe_ratio'],
            'pb_ratio': data['pb_ratio']
        }
    
    @classmethod
    def get_price_for_dcf(cls, ticker: str) -> Optional[float]:
        """Get current price for DCF calculations"""
        data = cls.get_unified_stock_data(ticker)
        return data['current_price'] if data else None
    
    @classmethod
    def get_company_info(cls, ticker: str) -> Optional[Dict]:
        """Get company info with consistent pricing"""
        data = cls.get_unified_stock_data(ticker)
        if not data:
            return None
        
        info = data['info'].copy()
        # Override price fields with our standardized values
        info['currentPrice'] = data['current_price']
        info['regularMarketPrice'] = data['current_price']
        info['marketCap'] = data['market_cap']
        
        return {
            'ticker': ticker,
            'name': info.get('longName', ticker),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'market_cap': data['market_cap'],
            'current_price': data['current_price'],
            'currency': info.get('currency', 'INR'),
            'exchange': info.get('exchange', 'NSE'),
            'info': info
        }
    
    @classmethod
    def clear_cache(cls, ticker: str = None):
        """Clear cache for specific ticker or all tickers"""
        with cls._cache_lock:
            if ticker:
                cls._price_cache.pop(ticker, None)
                cls._cache_timestamps.pop(ticker, None)
                logger.info(f"Cleared cache for {ticker}")
            else:
                cls._price_cache.clear()
                cls._cache_timestamps.clear()
                logger.info("Cleared all price cache")
    
    @classmethod
    def get_cache_status(cls) -> Dict:
        """Get cache status for debugging"""
        with cls._cache_lock:
            status = {}
            for ticker in cls._price_cache:
                cache_age = datetime.now() - cls._cache_timestamps.get(ticker, datetime.now())
                status[ticker] = {
                    'cached': True,
                    'age_seconds': cache_age.total_seconds(),
                    'valid': cls._is_cache_valid(ticker),
                    'price': cls._price_cache[ticker].get('current_price', 0)
                }
            return status

# Global service instance
price_service = PriceService()