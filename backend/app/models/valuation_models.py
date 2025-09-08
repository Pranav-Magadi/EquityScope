# Valuation Models Data Structures
# Pydantic models for multiple valuation approaches

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class ValuationMethod(str, Enum):
    SECTOR_DCF = "sector_dcf"
    GENERIC_DCF = "generic_dcf"
    PE_MULTIPLE = "pe_multiple"
    EV_EBITDA = "ev_ebitda"
    PEG_RATIO = "peg_ratio"
    PRICE_TO_BOOK = "price_to_book"
    DIVIDEND_DISCOUNT = "dividend_discount"

class ModelAssumptions(BaseModel):
    """Key assumptions used in valuation model"""
    growth_assumptions: Dict[str, str] = Field(
        description="Growth-related assumptions (revenue, earnings, etc.)"
    )
    risk_assumptions: Dict[str, str] = Field(
        description="Risk and discount rate assumptions"
    )
    terminal_assumptions: Dict[str, str] = Field(
        description="Terminal value assumptions"
    )
    sector_specific: Dict[str, str] = Field(
        description="Sector-specific assumptions and adjustments"
    )

class ValuationModelResponse(BaseModel):
    """Response from a single valuation model"""
    model_id: str = Field(description="Unique identifier for the valuation model")
    model_name: str = Field(description="Human-readable model name")
    ticker: str = Field(description="Stock ticker symbol")
    
    # Valuation Results
    fair_value: float = Field(description="Calculated fair value per share")
    current_price: float = Field(description="Current market price per share")
    upside_downside_pct: float = Field(description="Upside/downside percentage")
    confidence: float = Field(ge=0, le=1, description="Model confidence score (0-1)")
    
    # Methodology
    method: str = Field(description="Valuation methodology used")
    assumptions: ModelAssumptions
    key_factors: List[str] = Field(description="Key factors influencing valuation")
    
    # Metadata
    calculation_timestamp: datetime = Field(description="When the calculation was performed")
    data_sources: List[str] = Field(description="Data sources used in calculation")
    limitations: List[str] = Field(description="Known limitations of this model")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ValuationSummary(BaseModel):
    """Summary statistics across multiple valuation models"""
    ticker: str
    current_price: float
    
    fair_value_range: Dict[str, float] = Field(
        description="Min, max, mean, median fair values across models"
    )
    upside_range: Dict[str, float] = Field(
        description="Min, max, mean upside percentages"
    )
    
    consensus_confidence: float = Field(
        ge=0, le=1, 
        description="Average confidence across all models"
    )
    model_agreement: float = Field(
        ge=0, le=1,
        description="How well models agree (1 = perfect agreement)"
    )
    
    calculation_timestamp: datetime

class ValuationComparison(BaseModel):
    """Comprehensive comparison of multiple valuation models"""
    ticker: str
    models: Dict[str, ValuationModelResponse] = Field(
        description="Dictionary of model_id -> ValuationModelResponse"
    )
    summary: ValuationSummary
    warnings: List[str] = Field(
        default=[],
        description="Any warnings or errors during calculation"
    )
    recommendation: str = Field(
        description="Overall investment recommendation based on model consensus"
    )

# Generic DCF Service Response Models
class GenericDCFResult(BaseModel):
    """Result from generic DCF calculation"""
    ticker: str
    fair_value: float
    current_price: float
    upside_downside_pct: float
    confidence: float
    dcf_method: str = "Generic_DCF"
    
    # DCF Components
    terminal_value: float
    total_pv_fcf: float
    net_debt: float
    shares_outstanding: float
    
    # Key Metrics
    wacc: float
    terminal_growth_rate: float
    forecast_years: int
    
    reasoning: List[str] = Field(default=[])
    assumptions: Dict[str, Any] = Field(default={})

# Multiples Valuation Service Response Models
class MultiplesResult(BaseModel):
    """Result from multiples-based valuation"""
    ticker: str
    fair_value: float
    current_price: float
    upside_downside_pct: float
    confidence: float
    method: str
    
    # Multiple Details
    applied_multiple: float
    peer_multiples: Dict[str, float] = Field(
        description="Peer ticker -> multiple value"
    )
    industry_median: float
    
    # Quality Adjustments
    quality_premium_discount: float = Field(
        description="Premium/discount applied for quality (+/- %)"
    )
    
    reasoning: List[str] = Field(default=[])
    assumptions: Dict[str, Any] = Field(default={})

# Model Comparison Utilities
class ModelRanking(BaseModel):
    """Ranking of models by reliability for a given company"""
    ticker: str
    rankings: List[Dict[str, Any]] = Field(
        description="List of models ranked by suitability"
    )
    reasoning: Dict[str, str] = Field(
        description="Why each model is ranked as it is"
    )

class ValuationDashboard(BaseModel):
    """Complete valuation dashboard for a company"""
    ticker: str
    company_name: str
    sector: str
    
    # Primary Valuation
    primary_model: ValuationModelResponse
    
    # Model Comparison
    comparison: ValuationComparison
    
    # Risk Assessment
    valuation_risks: List[str] = Field(
        description="Key risks to valuation assumptions"
    )
    
    # Scenario Analysis
    scenarios: Dict[str, Dict[str, float]] = Field(
        default={},
        description="Bull/bear/base case scenarios"
    )
    
    last_updated: datetime

# Request Models
class ValuationRequest(BaseModel):
    """Request for valuation calculation"""
    ticker: str
    models: Optional[List[str]] = Field(
        default=None,
        description="Specific models to calculate (if None, all available)"
    )
    force_refresh: bool = Field(
        default=False,
        description="Force recalculation even if cached data exists"
    )
    
class ModelParameterOverride(BaseModel):
    """Override default model parameters"""
    model_id: str
    parameters: Dict[str, Any] = Field(
        description="Parameter name -> value overrides"
    )

class CustomValuationRequest(ValuationRequest):
    """Extended request allowing parameter customization"""
    parameter_overrides: List[ModelParameterOverride] = Field(
        default=[],
        description="Custom parameters for specific models"
    )
    include_scenarios: bool = Field(
        default=False,
        description="Include bull/bear scenario calculations"
    )