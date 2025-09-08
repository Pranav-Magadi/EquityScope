from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class CompanyInfo(BaseModel):
    ticker: str
    name: str
    sector: str
    industry: str
    market_cap: Optional[float] = None
    current_price: Optional[float] = None
    currency: str = "INR"
    exchange: str = "NSE"

class StockPrice(BaseModel):
    current_price: float
    change: float
    change_percent: float
    volume: int
    market_cap: float
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None

class SWOTAnalysis(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]

class NewsSentiment(BaseModel):
    headlines: List[str]
    sentiment_score: float  # -1 to 1
    sentiment_label: str  # Positive, Negative, Neutral
    news_count: int
    last_updated: datetime

class MarketLandscape(BaseModel):
    competitors: List[Dict[str, Any]]
    market_share: Optional[float] = None
    industry_trends: List[str]
    market_position: str

class EmployeeSentiment(BaseModel):
    rating: float  # 1-5 scale
    review_count: int
    pros: List[str]
    cons: List[str]
    sentiment_summary: str

class CompanyAnalysis(BaseModel):
    company_info: CompanyInfo
    stock_price: StockPrice
    swot: SWOTAnalysis
    news_sentiment: NewsSentiment
    market_landscape: MarketLandscape
    employee_sentiment: EmployeeSentiment