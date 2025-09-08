from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class KiteInstrumentType(str, Enum):
    EQ = "EQ"
    FUT = "FUT"
    CE = "CE"
    PE = "PE"

class KiteExchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"
    NFO = "NFO"
    BFO = "BFO"
    MCX = "MCX"

class KiteQuote(BaseModel):
    instrument_token: int
    timestamp: datetime
    last_price: float
    last_quantity: int
    last_trade_time: datetime
    change: float
    change_percent: float
    volume: int
    average_price: float
    oi: Optional[int] = None  # Open Interest for F&O
    oi_day_high: Optional[int] = None
    oi_day_low: Optional[int] = None
    
    # OHLC data
    ohlc: Dict[str, float]  # open, high, low, close
    
    # Market depth
    depth: Dict[str, List[Dict[str, Union[float, int]]]]  # buy/sell depth
    
    # Additional metrics
    upper_circuit_limit: Optional[float] = None
    lower_circuit_limit: Optional[float] = None
    
class KiteHistoricalData(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    oi: Optional[int] = None

class KiteInstrument(BaseModel):
    instrument_token: int
    exchange_token: int
    tradingsymbol: str
    name: str
    last_price: float
    expiry: Optional[datetime] = None
    strike: Optional[float] = None  # For options
    tick_size: float
    lot_size: int
    instrument_type: KiteInstrumentType
    segment: str
    exchange: KiteExchange

class KiteTechnicalIndicator(BaseModel):
    indicator_name: str
    value: float
    signal: str  # BUY, SELL, NEUTRAL
    timestamp: datetime

class KiteMarketStatus(BaseModel):
    exchange: str
    status: str  # open, close, holiday
    market_type: str  # normal, pre_market, post_market
    timestamp: datetime

class KiteTick(BaseModel):
    instrument_token: int
    last_price: float
    last_quantity: int
    average_traded_price: float
    volume_traded: int
    total_buy_quantity: int
    total_sell_quantity: int
    ohlc: Dict[str, float]
    change: float
    timestamp: datetime
    
    # Market depth (top 5 bids and offers)
    depth: Optional[Dict[str, List[Dict[str, Any]]]] = None

class KiteOrderbook(BaseModel):
    order_id: str
    exchange_order_id: Optional[str] = None
    parent_order_id: Optional[str] = None
    status: str
    status_message: Optional[str] = None
    order_timestamp: datetime
    exchange_update_timestamp: Optional[datetime] = None
    exchange_timestamp: Optional[datetime] = None
    variety: str
    exchange: str
    tradingsymbol: str
    instrument_token: int
    order_type: str
    transaction_type: str
    validity: str
    product: str
    quantity: int
    disclosed_quantity: int
    price: float
    trigger_price: float
    average_price: float
    filled_quantity: int
    pending_quantity: int
    cancelled_quantity: int

class KitePortfolioHolding(BaseModel):
    tradingsymbol: str
    exchange: str
    instrument_token: int
    isin: str
    product: str
    price: float
    quantity: int
    used_quantity: int
    t1_quantity: int
    realised_quantity: int
    authorised_quantity: int
    authorised_date: Optional[datetime] = None
    opening_quantity: int
    collateral_quantity: int
    collateral_type: Optional[str] = None
    discrepancy: bool
    average_price: float
    last_price: float
    close_price: float
    pnl: float
    day_change: float
    day_change_percentage: float

class KiteGTT(BaseModel):
    """Good Till Triggered order"""
    id: int
    user_id: str
    parent_trigger: Optional[Dict[str, Any]] = None
    type: str
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    status: str
    condition: Dict[str, Any]
    orders: List[Dict[str, Any]]
    meta: Optional[Dict[str, Any]] = None

class KiteMarginCalculation(BaseModel):
    equity: Dict[str, float]
    commodity: Dict[str, float]

class KiteProfile(BaseModel):
    user_id: str
    user_name: str
    user_shortname: str
    avatar_url: Optional[str] = None
    user_type: str
    email: str
    broker: str
    exchanges: List[str]
    products: List[str]
    order_types: List[str]
    
# Response models for API endpoints
class KiteQuoteResponse(BaseModel):
    status: str
    data: Dict[str, KiteQuote]

class KiteHistoricalResponse(BaseModel):
    status: str
    data: Dict[str, List[KiteHistoricalData]]

class KiteInstrumentsResponse(BaseModel):
    status: str
    data: List[KiteInstrument]

class KiteTickerData(BaseModel):
    """Real-time ticker data for WebSocket"""
    mode: str  # ltp, quote, full
    tradable: bool
    tokens: List[int]

# Configuration models
class KiteConfig(BaseModel):
    api_key: str
    api_secret: str
    request_token: Optional[str] = None
    access_token: Optional[str] = None
    public_token: Optional[str] = None
    login_time: Optional[datetime] = None
    
    # Rate limiting
    requests_per_second: int = 10
    max_historical_candles: int = 60000
    
    # WebSocket configuration
    reconnect_attempts: int = 5
    reconnect_delay: int = 5
    
    # Data preferences
    default_exchange: KiteExchange = KiteExchange.NSE
    default_interval: str = "day"  # minute, day, 3minute, 5minute, etc.

class KiteError(BaseModel):
    """Kite API error response"""
    status: str
    message: str
    error_type: str
    data: Optional[Dict[str, Any]] = None