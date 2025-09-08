# EquityScope v3 Summary Engine Models
# Based on Architecture Migration Strategy

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class InvestmentLabel(str, Enum):
    """Investment labels for v3 Summary Engine"""
    STRONGLY_BULLISH = "Strongly Bullish"
    CAUTIOUSLY_BULLISH = "Cautiously Bullish"
    NEUTRAL = "Neutral"
    CAUTIOUSLY_BEARISH = "Cautiously Bearish"
    STRONGLY_BEARISH = "Strongly Bearish"

class FairValueBand(BaseModel):
    """Fair value band with current price and methodology"""
    min_value: float = Field(..., description="Lower bound of fair value range")
    max_value: float = Field(..., description="Upper bound of fair value range")
    current_price: float = Field(..., description="Current market price")
    method: str = Field(..., description="Valuation method used (DCF, PE_Multiple, Sector_Average)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")

class SummaryResponse(BaseModel):
    """v3 Summary Engine primary response model"""
    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., description="Company name")
    fair_value_band: FairValueBand = Field(..., description="Fair value range with current price")
    investment_label: InvestmentLabel = Field(..., description="Investment assessment label")
    key_factors: List[str] = Field(default=[], description="Key factors influencing the investment label")
    
    # Three lens analysis
    valuation_insights: str = Field(..., description="DCF analysis and price multiples")
    market_signals: str = Field(..., description="Technical indicators and momentum")
    business_fundamentals: str = Field(..., description="Financial health and sector dynamics")
    
    # Metadata
    data_health_warnings: List[str] = Field(default=[], description="Data quality warnings and fallbacks")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="When analysis was generated")
    analysis_mode: str = Field(..., description="Analysis mode: 'simple' or 'agentic'")
    sector: str = Field(..., description="Company sector classification")

class SimpleSummaryResponse(SummaryResponse):
    """Rule-based simple mode summary response"""
    rules_applied: List[str] = Field(default=[], description="List of rules that were applied")
    fallback_triggers: List[str] = Field(default=[], description="Fallback mechanisms that were triggered")
    weighted_score: Optional[float] = Field(None, description="Total weighted score (-100 to +100)")
    component_scores: Optional[Dict[str, float]] = Field(None, description="Individual component scores")

class AgenticSummaryResponse(SummaryResponse):
    """AI-powered agentic mode summary response"""
    agent_reasoning: Optional[str] = Field(None, description="Internal agent reasoning process")
    cost_breakdown: Optional[dict] = Field(None, description="Token usage and cost information")
    model_version: Optional[str] = Field(None, description="AI model version used")

# Request models for API
class SummaryRequest(BaseModel):
    """Request model for summary analysis"""
    ticker: str = Field(..., description="Stock ticker to analyze")
    mode: str = Field("simple", description="Analysis mode: 'simple' or 'agentic'")
    
# Legacy support models for migration
class LegacyDCFMapping(BaseModel):
    """Maps legacy DCF response to v3 summary format"""
    intrinsic_value: float
    current_price: float
    upside_downside: float
    confidence_score: Optional[float] = 0.8
    
    def to_fair_value_band(self) -> FairValueBand:
        """Convert legacy DCF to FairValueBand"""
        # Create 10% band around intrinsic value
        band_width = self.intrinsic_value * 0.1
        return FairValueBand(
            min_value=self.intrinsic_value - band_width,
            max_value=self.intrinsic_value + band_width,
            current_price=self.current_price,
            method="DCF",
            confidence=self.confidence_score or 0.8
        )
    
    def to_investment_label(self) -> InvestmentLabel:
        """Convert upside/downside to investment label"""
        if self.upside_downside > 25:
            return InvestmentLabel.STRONGLY_BULLISH
        elif self.upside_downside > 10:
            return InvestmentLabel.CAUTIOUSLY_BULLISH
        elif self.upside_downside > -10:
            return InvestmentLabel.NEUTRAL
        elif self.upside_downside > -25:
            return InvestmentLabel.CAUTIOUSLY_BEARISH
        else:
            return InvestmentLabel.STRONGLY_BEARISH