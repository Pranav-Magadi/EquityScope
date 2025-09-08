# Banking Sector DCF Calculator
# Implements Excess Return Model for BFSI sector as per v3 requirements

import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class BankingMetrics:
    """Banking-specific financial metrics"""
    net_interest_margin: float  # NIM
    return_on_assets: float     # ROA
    return_on_equity: float     # ROE
    cost_to_income: float       # C/I ratio
    gnpa_ratio: float          # Gross NPA %
    provision_coverage: float   # PCR %
    credit_growth: float       # YoY credit growth
    casa_ratio: float          # CASA deposits %
    capital_adequacy: float    # CAR %
    book_value_per_share: float
    tangible_book_value: float

@dataclass
class ExcessReturnResult:
    """Result of Excess Return Model calculation"""
    fair_value_per_share: float
    excess_return: float
    risk_adjusted_roe: float
    cost_of_equity: float
    sustainable_growth: float
    method: str = "Excess_Return_Model"
    confidence: float = 0.0
    assumptions: Dict[str, float] = None

class BankingDCFCalculator:
    """
    Banking sector DCF using Excess Return Model
    
    Formula: Fair Value = Book Value + PV(Excess Returns)
    Excess Return = (ROE - Cost of Equity) × Book Value
    """
    
    def __init__(self):
        # Banking sector benchmarks
        self.sector_benchmarks = {
            "risk_free_rate": 0.065,      # 10Y G-Sec yield
            "market_risk_premium": 0.08,   # India equity risk premium
            "terminal_growth": 0.03,       # Long-term GDP growth
            "forecast_years": 10           # Explicit forecast period
        }
        
        # Banking-specific risk factors
        self.risk_adjustments = {
            "high_gnpa_penalty": 0.02,     # Additional risk for GNPA > 5%
            "low_provision_penalty": 0.015, # Risk for PCR < 70%
            "low_capital_penalty": 0.025,  # Risk for CAR < 12%
            "strong_casa_bonus": -0.01     # Lower risk for CASA > 40%
        }
    
    async def calculate_fair_value(
        self, 
        ticker: str, 
        banking_metrics: BankingMetrics,
        market_data: Dict = None
    ) -> ExcessReturnResult:
        """
        Calculate fair value using Banking Excess Return Model
        
        Args:
            ticker: Bank ticker symbol
            banking_metrics: Banking-specific financial metrics
            market_data: Market data including beta, market cap etc.
        
        Returns:
            ExcessReturnResult with fair value and components
        """
        try:
            logger.info(f"Calculating banking DCF for {ticker} using Excess Return Model")
            
            # Step 1: Calculate risk-adjusted cost of equity
            cost_of_equity = self._calculate_cost_of_equity(banking_metrics, market_data)
            
            # Step 2: Apply banking-specific risk adjustments
            risk_adjusted_coe = self._apply_banking_risk_adjustments(
                cost_of_equity, banking_metrics
            )
            
            # Step 3: Calculate sustainable ROE
            sustainable_roe = self._calculate_sustainable_roe(banking_metrics)
            
            # Step 4: Calculate excess return
            excess_return = max(0, sustainable_roe - risk_adjusted_coe)
            
            # Step 5: Project excess returns over forecast period
            pv_excess_returns = self._calculate_pv_excess_returns(
                excess_return, 
                banking_metrics.book_value_per_share,
                risk_adjusted_coe
            )
            
            # Step 6: Calculate fair value
            fair_value = banking_metrics.book_value_per_share + pv_excess_returns
            
            # Step 7: Calculate confidence score
            confidence = self._calculate_confidence_score(banking_metrics)
            
            # Prepare assumptions for transparency
            assumptions = {
                "risk_free_rate": self.sector_benchmarks["risk_free_rate"],
                "market_risk_premium": self.sector_benchmarks["market_risk_premium"],
                "terminal_growth": self.sector_benchmarks["terminal_growth"],
                "cost_of_equity": risk_adjusted_coe,
                "sustainable_roe": sustainable_roe,
                "excess_return_spread": excess_return
            }
            
            result = ExcessReturnResult(
                fair_value_per_share=fair_value,
                excess_return=excess_return,
                risk_adjusted_roe=sustainable_roe,
                cost_of_equity=risk_adjusted_coe,
                sustainable_growth=sustainable_roe * (1 - banking_metrics.book_value_per_share / fair_value),
                confidence=confidence,
                assumptions=assumptions
            )
            
            logger.info(f"Banking DCF completed for {ticker}: Fair Value = ₹{fair_value:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in banking DCF calculation for {ticker}: {e}")
            raise
    
    def _calculate_cost_of_equity(
        self, 
        metrics: BankingMetrics, 
        market_data: Dict = None
    ) -> float:
        """Calculate cost of equity using CAPM with banking adjustments"""
        
        # Base CAPM calculation
        risk_free = self.sector_benchmarks["risk_free_rate"]
        market_premium = self.sector_benchmarks["market_risk_premium"]
        
        # Use sector beta if market data not available
        beta = market_data.get("beta", 1.2) if market_data else 1.2  # Banking sector avg
        
        base_coe = risk_free + (beta * market_premium)
        
        # Banking-specific adjustments
        # Adjust for asset quality (GNPA impact)
        if metrics.gnpa_ratio > 0.05:  # GNPA > 5%
            base_coe += (metrics.gnpa_ratio - 0.05) * 0.5  # Penalty for high NPAs
        
        # Adjust for capital strength
        if metrics.capital_adequacy < 0.12:  # CAR < 12%
            base_coe += (0.12 - metrics.capital_adequacy) * 0.3
        
        return max(base_coe, 0.08)  # Minimum 8% CoE for banks
    
    def _apply_banking_risk_adjustments(
        self, 
        base_coe: float, 
        metrics: BankingMetrics
    ) -> float:
        """Apply banking-specific risk adjustments to cost of equity"""
        
        adjusted_coe = base_coe
        
        # High GNPA penalty
        if metrics.gnpa_ratio > 0.05:
            adjusted_coe += self.risk_adjustments["high_gnpa_penalty"]
        
        # Low provision coverage penalty
        if metrics.provision_coverage < 0.70:
            adjusted_coe += self.risk_adjustments["low_provision_penalty"]
        
        # Low capital adequacy penalty
        if metrics.capital_adequacy < 0.12:
            adjusted_coe += self.risk_adjustments["low_capital_penalty"]
        
        # Strong CASA bonus (lower funding cost)
        if metrics.casa_ratio > 0.40:
            adjusted_coe += self.risk_adjustments["strong_casa_bonus"]  # Negative = bonus
        
        return adjusted_coe
    
    def _calculate_sustainable_roe(self, metrics: BankingMetrics) -> float:
        """
        Calculate sustainable ROE for banking sector
        
        Considers:
        - Current ROE trend
        - Asset quality impact
        - Efficiency ratios
        - Regulatory capital requirements
        """
        
        base_roe = metrics.return_on_equity
        
        # Adjust for asset quality deterioration
        if metrics.gnpa_ratio > 0.03:  # Above 3% GNPA
            provisioning_impact = metrics.gnpa_ratio * 0.5  # Provision drag
            base_roe -= provisioning_impact
        
        # Adjust for operational efficiency
        if metrics.cost_to_income > 0.50:  # C/I > 50%
            efficiency_drag = (metrics.cost_to_income - 0.50) * 0.2
            base_roe -= efficiency_drag
        
        # Banking sector sustainable ROE typically 12-18%
        sustainable_roe = max(min(base_roe, 0.18), 0.08)
        
        return sustainable_roe
    
    def _calculate_pv_excess_returns(
        self, 
        excess_return: float, 
        book_value: float, 
        discount_rate: float
    ) -> float:
        """Calculate present value of excess returns over forecast period"""
        
        if excess_return <= 0:
            return 0.0
        
        pv_excess_returns = 0.0
        current_book_value = book_value
        
        # Project excess returns for forecast years
        for year in range(1, self.sector_benchmarks["forecast_years"] + 1):
            # Assume book value grows with retained earnings
            growth_rate = excess_return * 0.6  # 60% retention assumption
            current_book_value *= (1 + growth_rate)
            
            # Calculate excess return for this year
            yearly_excess_return = excess_return * current_book_value
            
            # Discount to present value
            discount_factor = (1 + discount_rate) ** year
            pv_excess_returns += yearly_excess_return / discount_factor
        
        # Terminal value of excess returns
        terminal_excess_return = excess_return * current_book_value
        terminal_growth = self.sector_benchmarks["terminal_growth"]
        
        terminal_value = (terminal_excess_return * (1 + terminal_growth)) / (discount_rate - terminal_growth)
        terminal_pv = terminal_value / ((1 + discount_rate) ** self.sector_benchmarks["forecast_years"])
        
        return pv_excess_returns + terminal_pv
    
    def _calculate_confidence_score(self, metrics: BankingMetrics) -> float:
        """Calculate confidence score based on banking metrics quality"""
        
        confidence = 0.5  # Base confidence
        
        # Asset quality indicators
        if metrics.gnpa_ratio < 0.03:
            confidence += 0.15
        elif metrics.gnpa_ratio > 0.08:
            confidence -= 0.20
        
        # Capital strength
        if metrics.capital_adequacy > 0.15:
            confidence += 0.10
        elif metrics.capital_adequacy < 0.11:
            confidence -= 0.15
        
        # Profitability consistency
        if 0.12 <= metrics.return_on_equity <= 0.20:
            confidence += 0.10
        
        # Operational efficiency
        if metrics.cost_to_income < 0.45:
            confidence += 0.10
        elif metrics.cost_to_income > 0.60:
            confidence -= 0.10
        
        # Funding profile
        if metrics.casa_ratio > 0.40:
            confidence += 0.05
        
        return max(min(confidence, 0.95), 0.25)  # Cap between 25% and 95%

    def validate_banking_inputs(self, metrics: BankingMetrics) -> Tuple[bool, str]:
        """Validate banking metrics for reasonableness"""
        
        validations = [
            (0 <= metrics.gnpa_ratio <= 0.50, "GNPA ratio should be between 0% and 50%"),
            (0 <= metrics.return_on_equity <= 0.50, "ROE should be between 0% and 50%"),
            (0 <= metrics.cost_to_income <= 2.0, "Cost to Income should be between 0% and 200%"),
            (0.08 <= metrics.capital_adequacy <= 0.30, "CAR should be between 8% and 30%"),
            (0 <= metrics.casa_ratio <= 1.0, "CASA ratio should be between 0% and 100%"),
            (metrics.book_value_per_share > 0, "Book value per share must be positive")
        ]
        
        for is_valid, error_msg in validations:
            if not is_valid:
                return False, error_msg
        
        return True, "All validations passed"