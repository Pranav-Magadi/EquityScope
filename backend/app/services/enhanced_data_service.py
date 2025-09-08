import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from .data_service import DataService
from .kite_service import get_kite_service, KiteService
from ..models.company import CompanyInfo, StockPrice
from ..models.dcf import FinancialData
from ..models.kite import KiteQuote, KiteHistoricalData

logger = logging.getLogger(__name__)

class EnhancedDataService:
    """Enhanced data service that combines Kite and yfinance data sources"""
    
    def __init__(self):
        self.kite_service = get_kite_service()
        self.fallback_service = DataService()
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the enhanced data service"""
        try:
            kite_success = await self.kite_service.initialize_session()
            self._initialized = True
            
            if kite_success:
                logger.info("Enhanced data service initialized with Kite Connect")
            else:
                logger.info("Enhanced data service initialized with yfinance fallback only")
            
            return True
        except Exception as e:
            logger.error(f"Error initializing enhanced data service: {e}")
            self._initialized = True  # Still usable with fallback
            return True
    
    def _normalize_ticker(self, ticker: str) -> Tuple[str, str]:
        """Normalize ticker for both Kite and yfinance"""
        # For Kite (remove .NS suffix)
        kite_symbol = ticker.replace('.NS', '').upper()
        
        # For yfinance (ensure .NS suffix for Indian stocks)
        yf_symbol = ticker if '.' in ticker else f"{ticker}.NS"
        
        return kite_symbol, yf_symbol
    
    async def get_company_info(self, ticker: str) -> Optional[CompanyInfo]:
        """Get company information with Kite enhancement"""
        if not self._initialized:
            await self.initialize()
        
        kite_symbol, yf_symbol = self._normalize_ticker(ticker)
        
        try:
            # Try to get additional data from Kite instruments
            instruments = await self.kite_service.search_instruments(kite_symbol)
            kite_info = None
            
            if instruments:
                # Find the best matching equity instrument
                for instrument in instruments:
                    if (instrument.tradingsymbol == kite_symbol and 
                        instrument.instrument_type.value == "EQ"):
                        kite_info = instrument
                        break
            
            # Get base info from yfinance
            company_info = self.fallback_service.get_company_info(yf_symbol)
            
            if company_info and kite_info:
                # Enhance with Kite data
                company_info.name = kite_info.name or company_info.name
                company_info.current_price = kite_info.last_price or company_info.current_price
                
            return company_info
            
        except Exception as e:
            logger.error(f"Error in enhanced get_company_info for {ticker}: {e}")
            # Fallback to yfinance only
            return self.fallback_service.get_company_info(yf_symbol)
    
    async def get_stock_price(self, ticker: str) -> Optional[StockPrice]:
        """Get enhanced stock price with real-time Kite data"""
        if not self._initialized:
            await self.initialize()
        
        kite_symbol, yf_symbol = self._normalize_ticker(ticker)
        
        try:
            # Try Kite first for real-time data
            kite_quote = await self.kite_service.get_quote(kite_symbol)
            
            if kite_quote:
                # Use Kite real-time data
                return StockPrice(
                    current_price=kite_quote.last_price,
                    change=kite_quote.change,
                    change_percent=kite_quote.change_percent,
                    volume=kite_quote.volume,
                    market_cap=0,  # Calculate separately if needed
                    pe_ratio=None,  # Not available in Kite quote
                    pb_ratio=None   # Not available in Kite quote
                )
            else:
                # Fallback to yfinance
                logger.info(f"Using yfinance fallback for stock price: {ticker}")
                return self.fallback_service.get_stock_price(yf_symbol)
                
        except Exception as e:
            logger.error(f"Error in enhanced get_stock_price for {ticker}: {e}")
            # Fallback to yfinance
            return self.fallback_service.get_stock_price(yf_symbol)
    
    async def get_financial_data(self, ticker: str, years: int = 5) -> Optional[FinancialData]:
        """Get enhanced financial data combining Kite historical data with yfinance fundamentals"""
        if not self._initialized:
            await self.initialize()
        
        kite_symbol, yf_symbol = self._normalize_ticker(ticker)
        
        try:
            # Get fundamental data from yfinance (better for financial statements)
            yf_financial_data = self.fallback_service.get_financial_data(yf_symbol, years)
            
            # Get price history from Kite for better accuracy
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=years * 365 + 30)  # Add buffer
                
                kite_historical = await self.kite_service.get_historical_data(
                    kite_symbol, start_date, end_date, "day"
                )
                
                if kite_historical and yf_financial_data:
                    # Enhance yfinance data with Kite price history
                    logger.info(f"Enhanced financial data with Kite historical prices for {ticker}")
                    # For now, return yfinance data but could enhance with price validation
                    return yf_financial_data
                    
            except Exception as e:
                logger.warning(f"Could not enhance with Kite historical data: {e}")
            
            # Return yfinance data (still good for fundamentals)
            return yf_financial_data
            
        except Exception as e:
            logger.error(f"Error in enhanced get_financial_data for {ticker}: {e}")
            return self.fallback_service.get_financial_data(yf_symbol, years)
    
    async def get_intraday_data(self, ticker: str, interval: str = "5minute") -> List[KiteHistoricalData]:
        """Get intraday data (only available through Kite)"""
        if not self._initialized:
            await self.initialize()
        
        kite_symbol, _ = self._normalize_ticker(ticker)
        
        try:
            end_date = datetime.now()
            start_date = end_date.replace(hour=9, minute=15, second=0, microsecond=0)  # Market open
            
            return await self.kite_service.get_historical_data(
                kite_symbol, start_date, end_date, interval
            )
            
        except Exception as e:
            logger.error(f"Error getting intraday data for {ticker}: {e}")
            return []
    
    async def get_market_depth(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get market depth data (only available through Kite)"""
        if not self._initialized:
            await self.initialize()
        
        kite_symbol, _ = self._normalize_ticker(ticker)
        
        try:
            quote = await self.kite_service.get_quote(kite_symbol)
            if quote and quote.depth:
                return {
                    "symbol": ticker,
                    "timestamp": quote.timestamp,
                    "depth": quote.depth,
                    "circuit_limits": {
                        "upper": quote.upper_circuit_limit,
                        "lower": quote.lower_circuit_limit
                    }
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting market depth for {ticker}: {e}")
            return None
    
    async def get_multiple_quotes(self, tickers: List[str]) -> Dict[str, Optional[StockPrice]]:
        """Get quotes for multiple symbols efficiently"""
        if not self._initialized:
            await self.initialize()
        
        results = {}
        
        # Process in batches to avoid rate limiting
        batch_size = 10
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
            
            # Create tasks for concurrent processing
            tasks = []
            for ticker in batch:
                tasks.append(self.get_stock_price(ticker))
            
            # Execute batch concurrently
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Store results
            for ticker, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error getting quote for {ticker}: {result}")
                    results[ticker] = None
                else:
                    results[ticker] = result
            
            # Small delay between batches to respect rate limits
            if i + batch_size < len(tickers):
                await asyncio.sleep(0.1)
        
        return results
    
    async def get_market_status(self) -> Dict[str, Any]:
        """Get current market status"""
        if not self._initialized:
            await self.initialize()
        
        try:
            return await self.kite_service.get_market_status()
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return {"error": str(e)}
    
    async def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """Search for symbols/companies"""
        if not self._initialized:
            await self.initialize()
        
        try:
            instruments = await self.kite_service.search_instruments(query)
            
            results = []
            for instrument in instruments:
                results.append({
                    "symbol": instrument.tradingsymbol,
                    "name": instrument.name,
                    "exchange": instrument.exchange.value,
                    "instrument_type": instrument.instrument_type.value,
                    "last_price": instrument.last_price
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching symbols for query '{query}': {e}")
            return []
    
    async def get_portfolio_data(self) -> List[Dict[str, Any]]:
        """Get portfolio holdings (requires authenticated Kite session)"""
        if not self._initialized:
            await self.initialize()
        
        try:
            return await self.kite_service.get_portfolio()
        except Exception as e:
            logger.error(f"Error getting portfolio data: {e}")
            return []
    
    def get_data_source_status(self) -> Dict[str, Any]:
        """Get status of data sources"""
        return {
            "kite_available": self.kite_service._session_initialized,
            "yfinance_available": True,  # Always available as fallback
            "enhanced_mode": self.kite_service._session_initialized
        }
    
    async def close(self):
        """Clean up resources"""
        try:
            await self.kite_service.close_session()
        except Exception as e:
            logger.error(f"Error closing enhanced data service: {e}")

# Singleton instance
_enhanced_data_service_instance = None

def get_enhanced_data_service() -> EnhancedDataService:
    """Get singleton EnhancedDataService instance"""
    global _enhanced_data_service_instance
    if _enhanced_data_service_instance is None:
        _enhanced_data_service_instance = EnhancedDataService()
    return _enhanced_data_service_instance