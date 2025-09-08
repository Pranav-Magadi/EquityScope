import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
from kiteconnect import KiteConnect
from kiteconnect.exceptions import KiteException
import os
from ..models.kite import (
    KiteQuote, KiteHistoricalData, KiteInstrument, KiteConfig,
    KiteQuoteResponse, KiteHistoricalResponse, KiteError,
    KiteExchange, KiteInstrumentType
)

logger = logging.getLogger(__name__)

class KiteService:
    """Service for Kite Connect API integration"""
    
    def __init__(self, config: Optional[KiteConfig] = None):
        self.config = config or self._load_config()
        self.kite = None
        self._instruments_cache = {}
        self._cache_expiry = {}
        self._session_initialized = False
        
    def _load_config(self) -> KiteConfig:
        """Load Kite configuration from environment variables"""
        return KiteConfig(
            api_key=os.getenv("KITE_API_KEY", ""),
            api_secret=os.getenv("KITE_API_SECRET", ""),
            access_token=os.getenv("KITE_ACCESS_TOKEN", ""),
            request_token=os.getenv("KITE_REQUEST_TOKEN", ""),
        )
    
    async def initialize_session(self) -> bool:
        """Initialize Kite Connect session"""
        try:
            if not self.config.api_key:
                logger.warning("Kite API key not configured, using demo mode")
                return False
                
            self.kite = KiteConnect(api_key=self.config.api_key)
            
            # If we have an access token, use it
            if self.config.access_token:
                self.kite.set_access_token(self.config.access_token)
                self._session_initialized = True
                return True
            
            # If we have a request token, generate access token
            if self.config.request_token:
                data = self.kite.generate_session(
                    self.config.request_token, 
                    api_secret=self.config.api_secret
                )
                self.config.access_token = data["access_token"]
                self.kite.set_access_token(self.config.access_token)
                self._session_initialized = True
                return True
                
            logger.error("No access token or request token available")
            return False
            
        except Exception as e:
            logger.error(f"Failed to initialize Kite session: {e}")
            return False
    
    def _is_session_valid(self) -> bool:
        """Check if current session is valid"""
        return self._session_initialized and self.kite is not None
    
    async def get_login_url(self) -> str:
        """Get Kite Connect login URL for authentication"""
        if not self.config.api_key:
            raise ValueError("API key not configured")
            
        kite_temp = KiteConnect(api_key=self.config.api_key)
        return kite_temp.login_url()
    
    def _normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol for Kite (remove .NS suffix, etc.)"""
        if symbol.endswith('.NS'):
            return symbol[:-3]
        return symbol.upper()
    
    async def get_instruments(self, exchange: Optional[str] = None) -> List[KiteInstrument]:
        """Get all tradable instruments"""
        if not self._is_session_valid():
            return []
            
        try:
            cache_key = f"instruments_{exchange or 'all'}"
            
            # Check cache (valid for 1 hour)
            if (cache_key in self._instruments_cache and 
                cache_key in self._cache_expiry and
                datetime.now() < self._cache_expiry[cache_key]):
                return self._instruments_cache[cache_key]
            
            # Fetch from API
            instruments_data = self.kite.instruments(exchange)
            instruments = []
            
            for item in instruments_data:
                try:
                    instrument = KiteInstrument(
                        instrument_token=item['instrument_token'],
                        exchange_token=item['exchange_token'],
                        tradingsymbol=item['tradingsymbol'],
                        name=item['name'],
                        last_price=item.get('last_price', 0.0),
                        expiry=datetime.strptime(item['expiry'], '%Y-%m-%d').date() if item.get('expiry') else None,
                        strike=item.get('strike'),
                        tick_size=item['tick_size'],
                        lot_size=item['lot_size'],
                        instrument_type=KiteInstrumentType(item['instrument_type']),
                        segment=item['segment'],
                        exchange=KiteExchange(item['exchange'])
                    )
                    instruments.append(instrument)
                except Exception as e:
                    logger.warning(f"Error parsing instrument {item}: {e}")
                    continue
            
            # Cache the results
            self._instruments_cache[cache_key] = instruments
            self._cache_expiry[cache_key] = datetime.now() + timedelta(hours=1)
            
            return instruments
            
        except KiteException as e:
            logger.error(f"Kite API error fetching instruments: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching instruments: {e}")
            return []
    
    async def find_instrument_token(self, symbol: str, exchange: str = "NSE") -> Optional[int]:
        """Find instrument token for a given symbol"""
        normalized_symbol = self._normalize_symbol(symbol)
        instruments = await self.get_instruments(exchange)
        
        for instrument in instruments:
            if (instrument.tradingsymbol == normalized_symbol and 
                instrument.exchange.value == exchange and
                instrument.instrument_type == KiteInstrumentType.EQ):
                return instrument.instrument_token
        
        return None
    
    async def get_quote(self, symbol: str) -> Optional[KiteQuote]:
        """Get real-time quote for a symbol"""
        if not self._is_session_valid():
            logger.warning("Kite session not initialized, cannot fetch quote")
            return None
            
        try:
            # Find instrument token
            instrument_token = await self.find_instrument_token(symbol)
            if not instrument_token:
                logger.warning(f"Instrument token not found for {symbol}")
                return None
            
            # Get quote data
            quote_data = self.kite.quote([instrument_token])
            
            if str(instrument_token) not in quote_data:
                return None
                
            data = quote_data[str(instrument_token)]
            
            # Parse the quote data
            quote = KiteQuote(
                instrument_token=instrument_token,
                timestamp=datetime.now(),
                last_price=data['last_price'],
                last_quantity=data.get('last_quantity', 0),
                last_trade_time=datetime.strptime(data['last_trade_time'], '%Y-%m-%d %H:%M:%S') if data.get('last_trade_time') else datetime.now(),
                change=data.get('net_change', 0),
                change_percent=data.get('change_percent', 0),
                volume=data.get('volume', 0),
                average_price=data.get('average_price', 0),
                oi=data.get('oi'),
                oi_day_high=data.get('oi_day_high'),
                oi_day_low=data.get('oi_day_low'),
                ohlc=data.get('ohlc', {}),
                depth=data.get('depth', {}),
                upper_circuit_limit=data.get('upper_circuit_limit'),
                lower_circuit_limit=data.get('lower_circuit_limit')
            )
            
            return quote
            
        except KiteException as e:
            logger.error(f"Kite API error fetching quote for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
    
    async def get_historical_data(
        self, 
        symbol: str, 
        from_date: datetime,
        to_date: datetime,
        interval: str = "day"
    ) -> List[KiteHistoricalData]:
        """Get historical OHLCV data"""
        if not self._is_session_valid():
            logger.warning("Kite session not initialized, cannot fetch historical data")
            return []
            
        try:
            # Find instrument token
            instrument_token = await self.find_instrument_token(symbol)
            if not instrument_token:
                logger.warning(f"Instrument token not found for {symbol}")
                return []
            
            # Get historical data
            historical_data = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date.date(),
                to_date=to_date.date(),
                interval=interval
            )
            
            # Parse the data
            parsed_data = []
            for item in historical_data:
                try:
                    data_point = KiteHistoricalData(
                        date=item['date'],
                        open=item['open'],
                        high=item['high'],
                        low=item['low'],
                        close=item['close'],
                        volume=item['volume'],
                        oi=item.get('oi')
                    )
                    parsed_data.append(data_point)
                except Exception as e:
                    logger.warning(f"Error parsing historical data point {item}: {e}")
                    continue
            
            return parsed_data
            
        except KiteException as e:
            logger.error(f"Kite API error fetching historical data for {symbol}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return []
    
    async def get_market_status(self) -> Dict[str, Any]:
        """Get current market status"""
        if not self._is_session_valid():
            return {"error": "Session not initialized"}
            
        try:
            return self.kite.market_status()
        except Exception as e:
            logger.error(f"Error fetching market status: {e}")
            return {"error": str(e)}
    
    async def search_instruments(self, query: str, exchange: str = "NSE") -> List[KiteInstrument]:
        """Search for instruments by name or symbol"""
        instruments = await self.get_instruments(exchange)
        query_lower = query.lower()
        
        matches = []
        for instrument in instruments:
            if (query_lower in instrument.tradingsymbol.lower() or 
                query_lower in instrument.name.lower()):
                matches.append(instrument)
                
            # Limit results to prevent overwhelming response
            if len(matches) >= 20:
                break
        
        return matches
    
    async def get_portfolio(self) -> List[Dict[str, Any]]:
        """Get portfolio holdings (requires authenticated session)"""
        if not self._is_session_valid():
            return []
            
        try:
            return self.kite.holdings()
        except Exception as e:
            logger.error(f"Error fetching portfolio: {e}")
            return []
    
    async def close_session(self):
        """Clean up resources"""
        try:
            if self.kite:
                # Kite doesn't have explicit session cleanup
                self.kite = None
            self._session_initialized = False
            self._instruments_cache.clear()
            self._cache_expiry.clear()
        except Exception as e:
            logger.error(f"Error closing Kite session: {e}")

# Singleton instance
_kite_service_instance = None

def get_kite_service() -> KiteService:
    """Get singleton KiteService instance"""
    global _kite_service_instance
    if _kite_service_instance is None:
        _kite_service_instance = KiteService()
    return _kite_service_instance