# Pharma Sector DCF Calculator
# Implements DCF + EV/EBITDA hybrid model for pharmaceutical companies

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class PharmaMetrics:
    """Pharma-specific financial metrics"""
    revenue: float
    ebitda: float
    ebitda_margin: float
    rd_expense: float
    rd_percentage: float        # R&D as % of revenue
    free_cash_flow: float
    working_capital: float
    capex: float
    
    # Pharma-specific metrics
    us_revenue_percentage: float    # US market exposure
    domestic_revenue_percentage: float
    anda_filings: int              # ANDA applications
    dmf_filings: int               # Drug Master Files
    usfda_observations: int        # Recent FDA observations
    patent_expiry_risk: float      # Revenue at risk from patent expiry
    
    # Valuation metrics
    shares_outstanding: float
    market_cap: float
    enterprise_value: float
    current_price: float

@dataclass
class PharmaValuationResult:
    """Result of Pharma DCF + EV/EBITDA hybrid calculation"""
    dcf_value_per_share: float
    ev_ebitda_value_per_share: float
    hybrid_fair_value: float
    dcf_weight: float
    multiple_weight: float
    rd_adjustment: float
    regulatory_risk_discount: float
    method: str = "DCF_EV_EBITDA_Hybrid"
    confidence: float = 0.0
    assumptions: Dict[str, float] = None

class PharmaDCFCalculator:
    """
    Pharma sector DCF using DCF + EV/EBITDA hybrid approach
    
    Methodology:
    1. Traditional DCF for base business
    2. EV/EBITDA multiple for peer comparison
    3. R&D pipeline value adjustment
    4. Regulatory risk discounting
    5. Weighted average of DCF and Multiple
    """
    
    def __init__(self):
        # Pharma sector benchmarks
        self.sector_benchmarks = {
            "risk_free_rate": 0.065,
            "market_risk_premium": 0.08,
            "terminal_growth": 0.04,      # Higher than economy due to healthcare growth
            "forecast_years": 10,
            "sector_ev_ebitda": 15.0,     # Median pharma EV/EBITDA
            "min_rd_threshold": 0.05,     # Minimum 5% R&D spend
            "optimal_rd_threshold": 0.12   # Optimal 12% R&D spend
        }
        
        # Pharma-specific risk adjustments
        self.risk_factors = {
            "low_rd_penalty": 0.02,           # Penalty for R&D < 5%
            "high_rd_bonus": -0.01,           # Bonus for R&D > 12%
            "us_exposure_bonus": -0.005,      # Lower risk for US exposure
            "patent_expiry_penalty": 0.03,    # Risk for high patent expiry
            "regulatory_risk_base": 0.015     # Base regulatory risk
        }
        
        # Geographic risk premiums
        self.geographic_premiums = {
            "us_market": 0.0,         # Lowest risk
            "eu_market": 0.005,       # Slightly higher
            "domestic_india": 0.01,   # Regulatory and pricing risk
            "emerging_markets": 0.02  # Highest risk
        }
    
    async def calculate_fair_value(
        self, 
        ticker: str, 
        pharma_metrics: PharmaMetrics,
        peer_multiples: Dict = None,
        market_data: Dict = None
    ) -> PharmaValuationResult:
        """
        Calculate fair value using Pharma DCF + EV/EBITDA hybrid
        
        Args:
            ticker: Pharma company ticker
            pharma_metrics: Pharma-specific metrics
            peer_multiples: Industry multiple data
            market_data: Market data including beta
        
        Returns:
            PharmaValuationResult with hybrid valuation
        """
        try:
            logger.info(f"Calculating pharma hybrid DCF for {ticker}")
            
            # Step 1: Traditional DCF calculation
            dcf_value = await self._calculate_dcf_value(ticker, pharma_metrics, market_data)
            
            # Step 2: EV/EBITDA multiple valuation
            multiple_value = self._calculate_multiple_value(pharma_metrics, peer_multiples)
            
            # Step 3: R&D pipeline adjustment
            rd_adjustment = self._calculate_rd_adjustment(pharma_metrics)
            
            # Step 4: Regulatory risk discount
            regulatory_discount = self._calculate_regulatory_risk(pharma_metrics)
            
            # Step 5: Determine hybrid weights based on business characteristics
            dcf_weight, multiple_weight = self._determine_hybrid_weights(pharma_metrics)
            
            # Step 6: Calculate weighted hybrid value
            adjusted_dcf = dcf_value * (1 + rd_adjustment) * (1 - regulatory_discount)
            adjusted_multiple = multiple_value * (1 - regulatory_discount * 0.5)  # Lower discount for multiple
            
            hybrid_value = (adjusted_dcf * dcf_weight) + (adjusted_multiple * multiple_weight)
            
            # Step 7: Calculate confidence score
            confidence = self._calculate_confidence_score(pharma_metrics)
            
            # Prepare assumptions
            assumptions = {
                "risk_free_rate": self.sector_benchmarks["risk_free_rate"],
                "terminal_growth": self.sector_benchmarks["terminal_growth"],
                "sector_ev_ebitda": peer_multiples.get("median_ev_ebitda", self.sector_benchmarks["sector_ev_ebitda"]) if peer_multiples else self.sector_benchmarks["sector_ev_ebitda"],
                "dcf_weight": dcf_weight,
                "multiple_weight": multiple_weight,
                "rd_adjustment": rd_adjustment,
                "regulatory_discount": regulatory_discount
            }
            
            result = PharmaValuationResult(
                dcf_value_per_share=dcf_value,
                ev_ebitda_value_per_share=multiple_value,
                hybrid_fair_value=hybrid_value,
                dcf_weight=dcf_weight,
                multiple_weight=multiple_weight,
                rd_adjustment=rd_adjustment,
                regulatory_risk_discount=regulatory_discount,
                confidence=confidence,
                assumptions=assumptions
            )
            
            logger.info(f"Pharma hybrid DCF completed for {ticker}: Fair Value = ₹{hybrid_value:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in pharma DCF calculation for {ticker}: {e}")
            raise
    
    async def _calculate_dcf_value(
        self, 
        ticker: str, 
        metrics: PharmaMetrics, 
        market_data: Dict = None
    ) -> float:
        """Calculate traditional DCF value for pharma company"""
        
        # Calculate cost of equity with pharma-specific adjustments
        cost_of_equity = self._calculate_pharma_cost_of_equity(metrics, market_data)
        
        # Project free cash flows
        projected_fcfs = self._project_pharma_fcfs(metrics)
        
        # Calculate terminal value
        terminal_fcf = projected_fcfs[-1] * (1 + self.sector_benchmarks["terminal_growth"])
        terminal_value = terminal_fcf / (cost_of_equity - self.sector_benchmarks["terminal_growth"])
        
        # Discount all cash flows to present value
        pv_fcfs = 0
        for year, fcf in enumerate(projected_fcfs, 1):
            pv_fcfs += fcf / ((1 + cost_of_equity) ** year)
        
        # Present value of terminal value
        pv_terminal = terminal_value / ((1 + cost_of_equity) ** len(projected_fcfs))
        
        # Enterprise value
        enterprise_value = pv_fcfs + pv_terminal
        
        # Convert to equity value per share (simplified - assume no net debt)
        equity_value = enterprise_value
        value_per_share = equity_value / metrics.shares_outstanding
        
        return value_per_share
    
    def _calculate_multiple_value(
        self, 
        metrics: PharmaMetrics, 
        peer_multiples: Dict = None
    ) -> float:
        """Calculate EV/EBITDA multiple-based valuation"""
        
        # Use peer multiple if available, otherwise sector benchmark
        if peer_multiples and "median_ev_ebitda" in peer_multiples:
            ev_ebitda_multiple = peer_multiples["median_ev_ebitda"]
        else:
            ev_ebitda_multiple = self.sector_benchmarks["sector_ev_ebitda"]
        
        # Adjust multiple based on company characteristics
        # Higher R&D intensity commands premium
        if metrics.rd_percentage > 0.10:
            ev_ebitda_multiple *= 1.1  # 10% premium
        elif metrics.rd_percentage < 0.05:
            ev_ebitda_multiple *= 0.9  # 10% discount
        
        # US exposure premium
        if metrics.us_revenue_percentage > 0.40:
            ev_ebitda_multiple *= 1.05  # 5% premium
        
        # Calculate implied enterprise value
        enterprise_value = metrics.ebitda * ev_ebitda_multiple
        
        # Convert to per share value (simplified)
        value_per_share = enterprise_value / metrics.shares_outstanding
        
        return value_per_share
    
    def _calculate_pharma_cost_of_equity(
        self, 
        metrics: PharmaMetrics, 
        market_data: Dict = None
    ) -> float:
        """Calculate pharma-specific cost of equity"""
        
        # Base CAPM
        risk_free = self.sector_benchmarks["risk_free_rate"]
        market_premium = self.sector_benchmarks["market_risk_premium"]
        beta = market_data.get("beta", 1.1) if market_data else 1.1  # Pharma sector avg
        
        base_coe = risk_free + (beta * market_premium)
        
        # Pharma-specific risk adjustments
        pharma_risk_premium = 0
        
        # R&D risk
        if metrics.rd_percentage < self.sector_benchmarks["min_rd_threshold"]:
            pharma_risk_premium += self.risk_factors["low_rd_penalty"]
        elif metrics.rd_percentage > self.sector_benchmarks["optimal_rd_threshold"]:
            pharma_risk_premium += self.risk_factors["high_rd_bonus"]  # Negative = bonus
        
        # Patent expiry risk
        if metrics.patent_expiry_risk > 0.20:  # >20% revenue at risk
            pharma_risk_premium += self.risk_factors["patent_expiry_penalty"]
        
        # Regulatory risk (USFDA observations)
        if metrics.usfda_observations > 5:
            pharma_risk_premium += self.risk_factors["regulatory_risk_base"]
        
        # Geographic diversification
        if metrics.us_revenue_percentage > 0.30:
            pharma_risk_premium += self.risk_factors["us_exposure_bonus"]  # Negative = bonus
        
        return base_coe + pharma_risk_premium
    
    def _project_pharma_fcfs(self, metrics: PharmaMetrics) -> List[float]:
        """Project pharma free cash flows with R&D and regulatory considerations"""
        
        projected_fcfs = []
        base_fcf = metrics.free_cash_flow
        
        # Growth assumptions
        revenue_growth_rate = 0.08  # 8% base growth for pharma
        
        # Adjust growth based on R&D intensity
        if metrics.rd_percentage > 0.10:
            revenue_growth_rate += 0.02  # Higher growth potential
        elif metrics.rd_percentage < 0.05:
            revenue_growth_rate -= 0.02  # Lower growth potential
        
        # Project FCFs
        for year in range(1, self.sector_benchmarks["forecast_years"] + 1):
            # Growth decay over time
            growth_rate = revenue_growth_rate * (0.9 ** (year - 1))
            
            # Adjust for patent expiry risk in later years
            if year > 5 and metrics.patent_expiry_risk > 0.15:
                growth_rate -= metrics.patent_expiry_risk * 0.1
            
            projected_fcf = base_fcf * ((1 + growth_rate) ** year)
            projected_fcfs.append(projected_fcf)
        
        return projected_fcfs
    
    def _calculate_rd_adjustment(self, metrics: PharmaMetrics) -> float:
        """Calculate R&D pipeline value adjustment"""
        
        base_adjustment = 0.0
        
        # R&D intensity bonus
        if metrics.rd_percentage > self.sector_benchmarks["optimal_rd_threshold"]:
            rd_excess = metrics.rd_percentage - self.sector_benchmarks["optimal_rd_threshold"]
            base_adjustment += min(rd_excess * 2, 0.15)  # Cap at 15% bonus
        
        # ANDA and DMF pipeline value
        anda_value = metrics.anda_filings * 0.002  # 0.2% per ANDA
        dmf_value = metrics.dmf_filings * 0.001    # 0.1% per DMF
        
        pipeline_adjustment = min(anda_value + dmf_value, 0.10)  # Cap at 10%
        
        return base_adjustment + pipeline_adjustment
    
    def _calculate_regulatory_risk(self, metrics: PharmaMetrics) -> float:
        """Calculate regulatory risk discount"""
        
        base_risk = self.risk_factors["regulatory_risk_base"]
        
        # USFDA observation risk
        if metrics.usfda_observations > 3:
            observation_risk = (metrics.usfda_observations - 3) * 0.01  # 1% per excess observation
            base_risk += min(observation_risk, 0.05)  # Cap at 5%
        
        # Patent expiry risk
        if metrics.patent_expiry_risk > 0.25:
            expiry_risk = (metrics.patent_expiry_risk - 0.25) * 0.2
            base_risk += min(expiry_risk, 0.10)  # Cap at 10%
        
        return min(base_risk, 0.20)  # Total regulatory risk cap at 20%
    
    def _determine_hybrid_weights(self, metrics: PharmaMetrics) -> Tuple[float, float]:
        """Determine DCF vs Multiple weights based on business characteristics"""
        
        # Start with equal weights
        dcf_weight = 0.6  # Slight preference for DCF in pharma
        multiple_weight = 0.4
        
        # Adjust based on R&D intensity (higher R&D = more DCF weight)
        if metrics.rd_percentage > 0.12:
            dcf_weight = 0.7
            multiple_weight = 0.3
        elif metrics.rd_percentage < 0.05:
            dcf_weight = 0.5  # More reliance on multiples
            multiple_weight = 0.5
        
        # Adjust based on business maturity (EBITDA margin)
        if metrics.ebitda_margin > 0.25:  # Mature, profitable
            multiple_weight += 0.1
            dcf_weight -= 0.1
        
        # Ensure weights sum to 1
        total = dcf_weight + multiple_weight
        dcf_weight /= total
        multiple_weight /= total
        
        return dcf_weight, multiple_weight
    
    def _calculate_confidence_score(self, metrics: PharmaMetrics) -> float:
        """Calculate confidence score based on pharma metrics quality"""
        
        confidence = 0.5  # Base confidence
        
        # R&D strength
        if 0.08 <= metrics.rd_percentage <= 0.15:
            confidence += 0.15
        elif metrics.rd_percentage < 0.05:
            confidence -= 0.20
        
        # Profitability
        if metrics.ebitda_margin > 0.20:
            confidence += 0.10
        elif metrics.ebitda_margin < 0.10:
            confidence -= 0.15
        
        # US market presence (de-risking)
        if metrics.us_revenue_percentage > 0.40:
            confidence += 0.10
        
        # Regulatory track record
        if metrics.usfda_observations <= 2:
            confidence += 0.05
        elif metrics.usfda_observations > 8:
            confidence -= 0.15
        
        # Pipeline strength
        total_filings = metrics.anda_filings + metrics.dmf_filings
        if total_filings > 20:
            confidence += 0.05
        elif total_filings < 5:
            confidence -= 0.10
        
        return max(min(confidence, 0.90), 0.30)  # Cap between 30% and 90%

    def validate_pharma_inputs(self, metrics: PharmaMetrics) -> Tuple[bool, str]:
        """Validate pharma metrics for reasonableness"""
        
        validations = [
            (metrics.revenue > 0, "Revenue must be positive"),
            (metrics.ebitda > 0, "EBITDA must be positive for pharma DCF"),
            (0 <= metrics.rd_percentage <= 0.30, "R&D percentage should be between 0% and 30%"),
            (0 <= metrics.us_revenue_percentage <= 1.0, "US revenue % should be between 0% and 100%"),
            (0 <= metrics.domestic_revenue_percentage <= 1.0, "Domestic revenue % should be between 0% and 100%"),
            (metrics.anda_filings >= 0, "ANDA filings cannot be negative"),
            (metrics.usfda_observations >= 0, "USFDA observations cannot be negative"),
            (0 <= metrics.patent_expiry_risk <= 1.0, "Patent expiry risk should be between 0% and 100%"),
            (metrics.shares_outstanding > 0, "Shares outstanding must be positive")
        ]
        
        for is_valid, error_msg in validations:
            if not is_valid:
                return False, error_msg
        
        return True, "All validations passed"