# Generic DCF Service
# Standard discounted cash flow model for cross-sector valuation

import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from ..models.valuation_models import GenericDCFResult
from .intelligent_cache import intelligent_cache, CacheType

logger = logging.getLogger(__name__)

@dataclass
class GenericDCFInputs:
    """Standard inputs for generic DCF model"""
    ticker: str
    current_price: float
    
    # Financial Metrics
    revenue_ttm: float
    ebitda_ttm: float
    ebit_ttm: float
    net_income_ttm: float
    free_cash_flow_ttm: float
    
    # Balance Sheet
    total_debt: float
    cash_and_equivalents: float
    shares_outstanding: float
    
    # Market Data
    market_cap: float
    enterprise_value: float
    beta: float = 1.0

class GenericDCFService:
    """
    Generic DCF valuation service
    
    Uses standard assumptions applicable across sectors:
    - Revenue growth assumptions based on historical trends
    - Standard margin assumptions
    - Market-based WACC calculation
    - Conservative terminal growth rates
    """
    
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        self.cache_manager = intelligent_cache
        
        # Standard DCF assumptions
        self.default_assumptions = {
            "risk_free_rate": 0.065,          # 10Y G-Sec yield
            "market_risk_premium": 0.08,      # India market premium
            "terminal_growth": 0.03,          # GDP growth assumption
            "forecast_years": 10,             # Forecast period
            "tax_rate": 0.25,                # Corporate tax rate
            
            # Growth Stage Assumptions
            "high_growth_years": 3,           # Years 1-3
            "moderate_growth_years": 4,       # Years 4-7  
            "stable_growth_years": 3,         # Years 8-10
            
            # Margin Assumptions
            "target_ebitda_margin": 0.20,     # Long-term EBITDA margin
            "capex_to_revenue": 0.04,         # Maintenance capex
            "working_capital_change": 0.01,   # WC as % of revenue change
        }
    
    async def calculate_dcf(
        self,
        ticker: str,
        forecast_years: int = 10,
        force_refresh: bool = False
    ) -> GenericDCFResult:
        """
        Calculate generic DCF valuation
        
        Args:
            ticker: Company ticker symbol
            forecast_years: Number of years to forecast (5-15)
            force_refresh: Bypass cache if True
            
        Returns:
            GenericDCFResult with fair value and components
        """
        try:
            logger.info(f"Calculating generic DCF for {ticker}")
            
            # Check cache first
            if self.use_cache and not force_refresh:
                cache_key = f"{ticker}_generic_dcf_{forecast_years}"
                cached_result = await self.cache_manager.get(
                    cache_key, CacheType.FINANCIAL_DATA
                )
                if cached_result:
                    logger.info(f"Cache hit for {ticker} generic DCF")
                    return GenericDCFResult(**cached_result)
            
            # Gather financial data
            dcf_inputs = await self._gather_financial_data(ticker)
            
            # Calculate WACC
            wacc = self._calculate_wacc(dcf_inputs)
            logger.info(f"Calculated WACC for {ticker}: {wacc:.2%}")
            
            # Project free cash flows
            fcf_projections = self._project_free_cash_flows(
                dcf_inputs, forecast_years
            )
            
            # Calculate terminal value
            terminal_fcf = fcf_projections[-1]
            terminal_value = self._calculate_terminal_value(
                terminal_fcf, wacc, self.default_assumptions["terminal_growth"]
            )
            
            # Discount cash flows to present value
            pv_fcf = self._discount_cash_flows(fcf_projections, wacc)
            pv_terminal = terminal_value / ((1 + wacc) ** forecast_years)
            
            # Calculate enterprise and equity value
            enterprise_value = sum(pv_fcf) + pv_terminal
            net_debt = dcf_inputs.total_debt - dcf_inputs.cash_and_equivalents
            equity_value = enterprise_value - net_debt
            fair_value_per_share = equity_value / dcf_inputs.shares_outstanding
            
            # Calculate upside/downside
            upside_downside_pct = (
                (fair_value_per_share - dcf_inputs.current_price) / dcf_inputs.current_price
            ) * 100
            
            # Assess confidence based on data quality
            confidence = self._assess_model_confidence(dcf_inputs, wacc)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                dcf_inputs, fair_value_per_share, wacc, confidence
            )
            
            # Create result
            result = GenericDCFResult(
                ticker=ticker,
                fair_value=fair_value_per_share,
                current_price=dcf_inputs.current_price,
                upside_downside_pct=upside_downside_pct,
                confidence=confidence,
                terminal_value=pv_terminal,
                total_pv_fcf=sum(pv_fcf),
                net_debt=net_debt,
                shares_outstanding=dcf_inputs.shares_outstanding,
                wacc=wacc,
                terminal_growth_rate=self.default_assumptions["terminal_growth"],
                forecast_years=forecast_years,
                reasoning=reasoning,
                assumptions=self._get_model_assumptions(wacc)
            )
            
            # Cache result
            if self.use_cache:
                cache_key = f"{ticker}_generic_dcf_{forecast_years}"
                await self.cache_manager.set(
                    cache_key, 
                    result.dict(), 
                    CacheType.FINANCIAL_DATA
                )
                logger.info(f"Cached generic DCF result for {ticker}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating generic DCF for {ticker}: {str(e)}")
            raise

    async def _gather_financial_data(self, ticker: str) -> GenericDCFInputs:
        """Gather required financial data for DCF calculation"""
        try:
            # This would integrate with your existing financial data services
            # For now, using placeholder implementation
            
            # In production, this would call:
            # - Financial data service for statements
            # - Market data service for price/beta
            # - Sector classification for benchmarks
            
            # Placeholder data - replace with actual service calls
            return GenericDCFInputs(
                ticker=ticker,
                current_price=1000.0,  # Would fetch from market data
                revenue_ttm=50000.0,   # From financial statements
                ebitda_ttm=10000.0,
                ebit_ttm=8000.0,
                net_income_ttm=6000.0,
                free_cash_flow_ttm=5000.0,
                total_debt=5000.0,
                cash_and_equivalents=2000.0,
                shares_outstanding=1000.0,
                market_cap=1000000.0,
                enterprise_value=1003000.0,
                beta=1.2
            )
            
        except Exception as e:
            logger.error(f"Error gathering financial data for {ticker}: {str(e)}")
            raise

    def _calculate_wacc(self, inputs: GenericDCFInputs) -> float:
        """Calculate Weighted Average Cost of Capital"""
        try:
            # Cost of Equity (CAPM)
            risk_free_rate = self.default_assumptions["risk_free_rate"]
            market_risk_premium = self.default_assumptions["market_risk_premium"]
            cost_of_equity = risk_free_rate + (inputs.beta * market_risk_premium)
            
            # Cost of Debt (simplified)
            cost_of_debt = risk_free_rate + 0.02  # Risk premium for corporate debt
            tax_rate = self.default_assumptions["tax_rate"]
            after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate)
            
            # Market value weights
            equity_value = inputs.market_cap
            debt_value = inputs.total_debt
            total_value = equity_value + debt_value
            
            if total_value == 0:
                return cost_of_equity  # All-equity financing
            
            weight_equity = equity_value / total_value
            weight_debt = debt_value / total_value
            
            # WACC calculation
            wacc = (weight_equity * cost_of_equity) + (weight_debt * after_tax_cost_of_debt)
            
            # Sanity check
            wacc = max(0.08, min(0.20, wacc))  # Between 8% and 20%
            
            return wacc
            
        except Exception as e:
            logger.error(f"Error calculating WACC: {str(e)}")
            return 0.12  # Default fallback

    def _project_free_cash_flows(
        self, 
        inputs: GenericDCFInputs, 
        forecast_years: int
    ) -> List[float]:
        """Project free cash flows for forecast period"""
        try:
            projections = []
            current_revenue = inputs.revenue_ttm
            current_ebitda = inputs.ebitda_ttm
            
            for year in range(1, forecast_years + 1):
                # Growth stage assumptions
                if year <= 3:
                    revenue_growth = 0.10  # 10% high growth
                elif year <= 7:
                    revenue_growth = 0.08  # 8% moderate growth  
                else:
                    revenue_growth = 0.05  # 5% stable growth
                
                # Project revenue
                current_revenue *= (1 + revenue_growth)
                
                # Project EBITDA (gradual margin improvement)
                target_margin = self.default_assumptions["target_ebitda_margin"]
                current_margin = current_ebitda / inputs.revenue_ttm
                margin_improvement = (target_margin - current_margin) / forecast_years
                new_margin = current_margin + (margin_improvement * year)
                projected_ebitda = current_revenue * new_margin
                
                # Calculate FCF
                # FCF = EBITDA - Taxes - Capex - Working Capital Change
                tax_rate = self.default_assumptions["tax_rate"]
                taxes = projected_ebitda * tax_rate  # Simplified
                capex = current_revenue * self.default_assumptions["capex_to_revenue"]
                wc_change = (current_revenue * revenue_growth * 
                           self.default_assumptions["working_capital_change"])
                
                fcf = projected_ebitda - taxes - capex - wc_change
                projections.append(max(0, fcf))  # Ensure non-negative
            
            return projections
            
        except Exception as e:
            logger.error(f"Error projecting FCF: {str(e)}")
            return [inputs.free_cash_flow_ttm * 1.05 ** i for i in range(1, forecast_years + 1)]

    def _calculate_terminal_value(
        self, 
        terminal_fcf: float, 
        wacc: float, 
        terminal_growth: float
    ) -> float:
        """Calculate terminal value using perpetuity growth model"""
        try:
            if wacc <= terminal_growth:
                # Avoid division by zero or negative denominators
                wacc = terminal_growth + 0.02
            
            terminal_value = (terminal_fcf * (1 + terminal_growth)) / (wacc - terminal_growth)
            return max(0, terminal_value)
            
        except Exception as e:
            logger.error(f"Error calculating terminal value: {str(e)}")
            return terminal_fcf * 10  # Fallback to 10x multiple

    def _discount_cash_flows(self, cash_flows: List[float], wacc: float) -> List[float]:
        """Discount projected cash flows to present value"""
        try:
            pv_cash_flows = []
            for year, cf in enumerate(cash_flows, 1):
                pv = cf / ((1 + wacc) ** year)
                pv_cash_flows.append(pv)
            return pv_cash_flows
            
        except Exception as e:
            logger.error(f"Error discounting cash flows: {str(e)}")
            return cash_flows  # Return undiscounted as fallback

    def _assess_model_confidence(self, inputs: GenericDCFInputs, wacc: float) -> float:
        """Assess confidence in the DCF model results"""
        try:
            confidence_factors = []
            
            # Data quality factors
            if inputs.free_cash_flow_ttm > 0:
                confidence_factors.append(0.2)  # Positive FCF
            if inputs.revenue_ttm > 1000:
                confidence_factors.append(0.15)  # Reasonable revenue scale
            if 0.08 <= wacc <= 0.16:
                confidence_factors.append(0.15)  # WACC in reasonable range
            if inputs.beta > 0.5 and inputs.beta < 2.0:
                confidence_factors.append(0.1)   # Beta in normal range
                
            # Business quality factors
            if inputs.ebitda_ttm / inputs.revenue_ttm > 0.1:
                confidence_factors.append(0.1)   # Reasonable margins
            if inputs.cash_and_equivalents > inputs.total_debt:
                confidence_factors.append(0.1)   # Net cash position
                
            # Model applicability
            confidence_factors.append(0.2)  # Base confidence for generic model
            
            return min(1.0, sum(confidence_factors))
            
        except Exception as e:
            logger.error(f"Error assessing confidence: {str(e)}")
            return 0.6  # Default moderate confidence

    def _generate_reasoning(
        self, 
        inputs: GenericDCFInputs, 
        fair_value: float, 
        wacc: float,
        confidence: float
    ) -> List[str]:
        """Generate reasoning for the valuation"""
        reasoning = []
        
        # Valuation summary
        upside = ((fair_value - inputs.current_price) / inputs.current_price) * 100
        if upside > 10:
            reasoning.append(f"DCF suggests {upside:.1f}% upside potential")
        elif upside < -10:
            reasoning.append(f"DCF indicates {abs(upside):.1f}% overvaluation")
        else:
            reasoning.append("DCF fair value near current market price")
        
        # Key assumptions
        reasoning.append(f"Based on {wacc:.1%} WACC and 3% terminal growth")
        
        # Model strengths
        if inputs.free_cash_flow_ttm > 0:
            reasoning.append("Company generates positive free cash flow")
        if confidence > 0.7:
            reasoning.append("High confidence due to strong financial metrics")
        elif confidence < 0.5:
            reasoning.append("Lower confidence due to data quality concerns")
        
        # Limitations
        reasoning.append("Generic model may not capture sector-specific dynamics")
        
        return reasoning

    def _get_model_assumptions(self, wacc: float) -> Dict[str, any]:
        """Get detailed model assumptions for transparency"""
        return {
            "wacc": f"{wacc:.1%}",
            "terminal_growth": f"{self.default_assumptions['terminal_growth']:.1%}",
            "forecast_years": self.default_assumptions["forecast_years"],
            "target_ebitda_margin": f"{self.default_assumptions['target_ebitda_margin']:.1%}",
            "tax_rate": f"{self.default_assumptions['tax_rate']:.1%}",
            "risk_free_rate": f"{self.default_assumptions['risk_free_rate']:.1%}",
            "market_risk_premium": f"{self.default_assumptions['market_risk_premium']:.1%}"
        }