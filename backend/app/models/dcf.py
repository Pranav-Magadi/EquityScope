from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class DCFMode(Enum):
    """DCF calculation modes with different complexity levels."""
    SIMPLE = "simple"      # Historical validation with rule-based logic
    AGENTIC = "agentic"    # AI-enhanced with management guidance and sentiment

class GrowthStage(BaseModel):
    """Growth stage definition for multi-stage DCF projections."""
    years: str              # e.g., "1-2", "3-5", "6-8", "9-10", "terminal"
    start_year: int
    end_year: int
    growth_rate: float      # Percentage
    method: str            # e.g., "historical_cagr", "management_guidance", "gdp_convergence"
    gdp_weight: float      # Weight of GDP growth in blending (0.0 to 1.0)
    confidence: str        # "high", "medium", "low"
    rationale: str         # Explanation for this growth rate

class MultiStageAssumptions(BaseModel):
    """Enhanced DCF assumptions with multi-stage growth."""
    mode: DCFMode
    projection_years: int = 10
    growth_stages: List[GrowthStage]
    ebitda_margin: float        # Percentage
    tax_rate: float            # Percentage
    wacc: float                # Percentage
    terminal_growth_rate: float # Percentage (should match final stage)
    gdp_growth_rate: float = 3.0  # India nominal GDP growth

class FinancialData(BaseModel):
    ticker: str
    years: List[int]
    revenue: List[float]
    ebitda: List[float]
    net_income: List[float]
    free_cash_flow: List[float]
    total_debt: List[float]
    cash: List[float]
    shares_outstanding: List[float]
    # Capital intensity metrics for dynamic calculation
    capex: Optional[List[float]] = None
    working_capital_change: Optional[List[float]] = None
    depreciation_amortization: Optional[List[float]] = None

class DCFAssumptions(BaseModel):
    revenue_growth_rate: float  # Percentage
    ebitda_margin: float        # Percentage
    tax_rate: float            # Percentage
    wacc: float                # Percentage
    terminal_growth_rate: float # Percentage
    projection_years: int = 5

class DCFProjection(BaseModel):
    year: int
    revenue: float
    revenue_growth_rate: float      # Year-over-year growth rate
    ebitda: float
    ebit: float
    tax: float
    nopat: float
    capex: float
    working_capital_change: float
    free_cash_flow: float
    present_value: float
    growth_stage: str               # Which growth stage this year belongs to
    growth_method: str              # Method used for this year's growth

class DCFValuation(BaseModel):
    intrinsic_value_per_share: float
    terminal_value: float
    enterprise_value: float
    equity_value: float
    current_stock_price: float
    upside_downside: float
    projections: List[DCFProjection]
    assumptions: DCFAssumptions  # Legacy support
    multi_stage_assumptions: Optional[MultiStageAssumptions] = None  # New 10-year format
    growth_waterfall: Optional[Dict[str, float]] = None  # Growth stage breakdown

class SensitivityAnalysis(BaseModel):
    wacc_range: List[float]
    terminal_growth_range: List[float]
    sensitivity_matrix: List[List[float]]

class DCFDefaults(BaseModel):
    revenue_growth_rate: float
    ebitda_margin: float
    tax_rate: float
    wacc: float
    terminal_growth_rate: float
    projection_years: int = 5
    capex_percentage: float = 4.0
    working_capital_percentage: float = 2.0
    current_price: float
    rationale: Dict[str, str]

class DCFResponse(BaseModel):
    valuation: DCFValuation
    sensitivity: SensitivityAnalysis
    financial_data: FinancialData
    last_updated: datetime

class MultiStageDCFResponse(BaseModel):
    """Enhanced DCF response with 10-year multi-stage projections."""
    valuation: DCFValuation
    sensitivity: SensitivityAnalysis
    financial_data: FinancialData
    mode: DCFMode
    growth_stages_summary: List[Dict[str, str]]  # Summary for UI display
    education_content: Dict[str, str]  # Progressive disclosure content
    last_updated: datetime